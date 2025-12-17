# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
QS02 + Jellyfin (Wi-Fi) : transcodage "Direct Play friendly" via NVENC (RTX 4070)

But :
- Détecter SDR/HDR avec ffprobe.
- Encoder en HEVC NVENC:
    - HDR -> HEVC Main10 10-bit (p010le) + tags BT.2020 + PQ/HLG.
    - SDR -> HEVC 8-bit (yuv420p) + tags BT.709.
- Audio:
    - Track 0 : AC3 (Dolby Digital) 5.1 ou 2.0 (HT-S40R friendly).
    - Track 1 : AAC stéréo (casque / compat universelle, y compris XM6).
    - Les deux pistes sont générées systématiquement à partir de la meilleure piste source.
- Plafond bitrate (maxrate/bufsize) = limite les "pics" pour streaming Wi-Fi.
  La qualité reste pilotée par CQ (constant quality) côté NVENC.

Modifie uniquement la section CONFIG.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import re
import shutil
import subprocess
import sys

# =========================
# CONFIG (MODIFIER ICI)
# =========================
IN_DIR = Path("./in")
OUT_DIR = Path("./out")
VIDEO_EXTS = {".mkv", ".mp4", ".m4v", ".mov"}

GPU_INDEX = 0

# NVENC qualité:
# - NVENC_CQ plus bas = meilleure qualité (fichier + gros), plus haut = + petit.
#   Valeurs courantes: 18 (très propre), 19-21 (bon "streamable"), 22+ (agressif).
NVENC_PRESET = "slow"  # alternatives: "medium" si tu veux aller plus vite.
NVENC_CQ = 20

# Plafonds "Wi‑Fi friendly" (limite les pointes, évite les buffers):
# - Si ton Wi‑Fi est excellent: monte HDR vers 30-35M.
# - Si ça buffer: baisse HDR vers 20M ou SDR vers 10-12M.
MAXRATE_HDR, BUFSIZE_HDR = "25M", "50M"
MAXRATE_SDR, BUFSIZE_SDR = "15M", "30M"

# Sous-titres:
# - False = maximise Direct Play (moins de risques de burn-in côté Jellyfin).
# - True  = copie les sous-titres (peut déclencher transcodage selon formats/client).
KEEP_SUBS = False

# Audio:
# - Track 0: AC3 640k 5.1 (ou 2.0) = bon standard pour barres ARC (HT-S40R).
# - Track 1: AAC 192k stéréo = passe-partout (casques Bluetooth XM6, TV, etc.).
# - Les deux pistes sont générées systématiquement à partir de la meilleure piste source.
AC3_BITRATE = "640k"
AAC_BITRATE = "192k"

OVERWRITE = False
DRY_RUN = False  # True = affiche juste les commandes

# =========================
HDR_TRCS = {"smpte2084", "arib-std-b67"}  # PQ / HLG


def cap(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def need(binname: str) -> str:
    p = shutil.which(binname)
    if not p:
        raise SystemExit(f"ERROR: '{binname}' introuvable dans PATH")
    return p


def has_nvenc(ffmpeg: str) -> bool:
    rc, out, _ = cap([ffmpeg, "-hide_banner", "-encoders"])
    return rc == 0 and "hevc_nvenc" in out


def probe(ffprobe: str, f: Path) -> tuple[list[dict], dict]:
    rc, out, err = cap([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(f)])
    if rc != 0:
        raise RuntimeError(f"ffprobe failed: {f}\n{err}")
    data = json.loads(out)
    return data.get("streams", []), data.get("format", {})


def first(streams: list[dict], t: str) -> dict | None:
    return next((s for s in streams if s.get("codec_type") == t), None)


def get_language(stream: dict) -> str | None:
    tags = stream.get("tags", {})
    lang = (tags.get("language") or "").lower()
    if lang in {"fra", "fre", "fr"}:
        return "fr"
    if lang in {"eng", "en"}:
        return "en"
    return None


def best_audio(streams: list[dict]) -> dict | None:
    a = [s for s in streams if s.get("codec_type") == "audio"]
    if not a:
        return None

    # Priorite: francais > anglais > plus de canaux
    fr_audio = [s for s in a if get_language(s) == "fr"]
    if fr_audio:
        fr_audio.sort(key=lambda s: int(s.get("channels") or 0), reverse=True)
        return fr_audio[0]

    en_audio = [s for s in a if get_language(s) == "en"]
    if en_audio:
        en_audio.sort(key=lambda s: int(s.get("channels") or 0), reverse=True)
        return en_audio[0]

    # Fallback: plus de canaux
    a.sort(key=lambda s: int(s.get("channels") or 0), reverse=True)
    return a[0]


def is_hdr(video: dict) -> tuple[bool, str]:
    trc = (video.get("color_transfer") or video.get("color_trc") or "").strip()
    if trc in HDR_TRCS:
        return True, trc
    pix = video.get("pix_fmt") or ""
    prim = video.get("color_primaries") or ""
    csp = video.get("color_space") or ""
    if pix.endswith("10le") and (prim == "bt2020" or csp in {"bt2020nc", "bt2020c"}):
        return True, "smpte2084"
    return False, "bt709"


def get_resolution_p(video: dict) -> str:
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    if height > 0:
        return f"{height}p"
    return ""


def clean_filename(name: str) -> str:
    # Technical keywords to remove (case-insensitive)
    tech_keywords = (
        r"HEVC|H\.?264|H264|AVC|X264|X265|H\.?265|H265|"
        r"10[- ]?bit|8[- ]?bit|"
        r"DTS(?:-HD)?|DTSHD|TrueHD|E[- ]?AC3|AC3|AAC|FLAC|MP3|"
        r"Blu[- ]?Ray|BDRip|BDR|WEB[- ]?Rip|WEB[- ]?DL|WEB|HDTV|DVD[- ]?Rip|DVD|"
        r"REMUX|REMASTERED|MULTI|"
        r"2160p|1080p|720p|480p|4K|UHD|"
        r"HDR10?\+?|DV|Dolby\s+Vision|HLG|"
        r"DD\+|DD5\.1|DD7\.1|5\.1|7\.1|2\.0|"
        r"AMZN|NF|HMAX|Hulu|iTunes|iT"
    )

    # Remove technical keywords with word boundaries
    cleaned = re.sub(rf"\b({tech_keywords})\b", "", name, flags=re.IGNORECASE)

    # Remove brackets/parens containing technical keywords
    cleaned = re.sub(rf"\[({tech_keywords})\w*\]", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(rf"\(({tech_keywords})\w*\)", "", cleaned, flags=re.IGNORECASE)

    # Clean up multiple spaces, dots, and trim
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\.+", ".", cleaned)
    cleaned = re.sub(r"[\.\s]+$", "", cleaned)
    cleaned = re.sub(r"^[\.\s]+", "", cleaned)
    return cleaned.strip()


def extract_movie_info(filename: str) -> tuple[str, str | None]:
    stem = Path(filename).stem
    # Try to extract year (4 digits between 1900-2100)
    year_match = re.search(r"\b(19|20)\d{2}\b", stem)
    year = year_match.group(0) if year_match else None

    # Clean the filename to get movie title
    cleaned = clean_filename(stem)

    # Remove year from cleaned name if found
    if year:
        cleaned = re.sub(r"\b" + re.escape(year) + r"\b", "", cleaned, flags=re.IGNORECASE)
        cleaned = clean_filename(cleaned)  # Re-clean after removing year

    # If cleaned is empty or too short, use original stem as fallback
    if not cleaned or len(cleaned) < 2:
        cleaned = stem

    return cleaned, year


def build_output_name(movie_title: str, year: str | None, resolution: str, hdr_tag: str) -> str:
    parts = [movie_title]
    if year:
        parts.append(year)
    if resolution:
        parts.append(resolution)
    parts.append(hdr_tag)
    parts.append("qs02")
    return ".".join(parts)


def find_available_filename(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    counter = 1
    while True:
        new_name = f"{stem}.{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def format_value(val: str | None) -> str:
    if val is None or val == "unknown":
        return "-"
    return str(val)


def format_size(size_bytes: str | int | None) -> str:
    if size_bytes == "unknown" or size_bytes is None:
        return "-"
    try:
        size = int(size_bytes)
        if size == 0:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        exp = int(math.log(size, 1024))
        exp = min(exp, len(units) - 1)
        size_fmt = size / (1024.0**exp)
        return f"{size_fmt:.2f} {units[exp]}"
    except (ValueError, TypeError):
        return str(size_bytes)


def format_bitrate(bitrate: str | int | None) -> str:
    if bitrate == "unknown" or bitrate is None:
        return "-"
    try:
        br = int(bitrate)
        if br < 1000:
            return f"{br} b/s"
        elif br < 1000000:
            return f"{br/1000:.1f} kb/s"
        else:
            return f"{br/1000000:.2f} Mb/s"
    except (ValueError, TypeError):
        return str(bitrate)


def create_md_file(
    md_path: Path,
    source_file: Path,
    source_name: str,
    source_video_info: dict,
    source_audio_info: dict | None,
    source_streams_info: list[dict],
    source_format_info: dict,
    target_file: Path,
    target_name: str,
    target_video_info: dict | None,
    target_audio_info: dict | None,
    target_streams_info: list[dict],
    target_format_info: dict,
) -> None:
    lines: list[str] = []

    def add_row(prop: str, src_val: str | int | None, tgt_val: str | int | None) -> None:
        src_str = format_value(src_val)
        tgt_str = format_value(tgt_val)
        changed = "Y" if src_str != tgt_str and tgt_str != "-" else "N"
        lines.append(f"| {prop} | {src_str} | {tgt_str} | {changed} |")

    def start_table() -> None:
        lines.append("| Propriete | Source | Cible | Change |")
        lines.append("|-----------|--------|-------|--------|")

    def safe_get(d: dict | None, key: str, default: str = "unknown") -> str:
        if d is None:
            return default
        return d.get(key, default) if isinstance(d, dict) else default

    def add_section(title: str, rows: list[tuple[str, str | int | None, str | int | None]]) -> None:
        lines.append(f"### {title}")
        lines.append("")
        start_table()
        for prop, src_val, tgt_val in rows:
            add_row(prop, src_val, tgt_val)
        lines.append("")

    lines.extend(
        [
            "# Comparaison Source / Cible",
            "",
            f"**Source:** `{source_name}`",
            f"**Cible:** `{target_name}`",
            "",
            "## Tableau de comparaison",
            "",
        ]
    )

    # Container
    add_section(
        "Container",
        [
            ("Format", source_format_info.get("format_name", "unknown"), safe_get(target_format_info, "format_name")),
            ("Taille", source_format_info.get("size", "unknown"), safe_get(target_format_info, "size")),
            ("Bitrate", source_format_info.get("bit_rate", "unknown"), safe_get(target_format_info, "bit_rate")),
            ("Duree (s)", source_format_info.get("duration", "unknown"), safe_get(target_format_info, "duration")),
            ("Nb streams", len(source_streams_info), len(target_streams_info) if target_streams_info else 0),
        ],
    )

    # Video
    video_rows = [
        ("Codec", source_video_info.get("codec_name", "unknown"), safe_get(target_video_info, "codec_name")),
        (
            "Resolution",
            f"{source_video_info.get('width', 0)}x{source_video_info.get('height', 0)}",
            (
                f"{safe_get(target_video_info, 'width', 0)}x{safe_get(target_video_info, 'height', 0)}"
                if target_video_info
                else "-"
            ),
        ),
        ("Pixel format", source_video_info.get("pix_fmt", "unknown"), safe_get(target_video_info, "pix_fmt")),
        ("Color space", source_video_info.get("color_space", "unknown"), safe_get(target_video_info, "color_space")),
        (
            "Color primaries",
            source_video_info.get("color_primaries", "unknown"),
            safe_get(target_video_info, "color_primaries"),
        ),
        (
            "Color transfer",
            source_video_info.get("color_transfer") or source_video_info.get("color_trc", "unknown"),
            (
                safe_get(target_video_info, "color_transfer") or safe_get(target_video_info, "color_trc")
                if target_video_info
                else "-"
            ),
        ),
        ("Frame rate", source_video_info.get("r_frame_rate", "unknown"), safe_get(target_video_info, "r_frame_rate")),
    ]
    add_section("Video", video_rows)

    # Audio Track 0 (AC3)
    if source_audio_info:
        add_section(
            "Audio - Track 0 (AC3)",
            [
                (
                    "Codec",
                    source_audio_info.get("codec_name", "unknown"),
                    safe_get(target_audio_info, "codec_name") if target_audio_info else "-",
                ),
                (
                    "Canaux",
                    source_audio_info.get("channels", "unknown"),
                    safe_get(target_audio_info, "channels") if target_audio_info else "-",
                ),
                (
                    "Channel layout",
                    source_audio_info.get("channel_layout", "unknown"),
                    safe_get(target_audio_info, "channel_layout") if target_audio_info else "-",
                ),
                (
                    "Sample rate",
                    source_audio_info.get("sample_rate", "unknown"),
                    safe_get(target_audio_info, "sample_rate") if target_audio_info else "-",
                ),
                (
                    "Bitrate",
                    source_audio_info.get("bit_rate", "unknown"),
                    safe_get(target_audio_info, "bit_rate") if target_audio_info else "-",
                ),
            ],
        )
    else:
        lines.append("### Audio - Track 0 (AC3)")
        lines.append("")
        start_table()
        lines.append("| Codec | - | - | N |")
        lines.append("")

    # Audio Track 1 (AAC stereo)
    target_audio_streams = [s for s in target_streams_info if s.get("codec_type") == "audio"]
    if len(target_audio_streams) > 1:
        target_aac = target_audio_streams[1]
        add_section(
            "Audio - Track 1 (AAC Stereo)",
            [
                ("Codec", "-", target_aac.get("codec_name", "unknown")),
                ("Canaux", "-", target_aac.get("channels", "unknown")),
                ("Sample rate", "-", target_aac.get("sample_rate", "unknown")),
                ("Bitrate", "-", target_aac.get("bit_rate", "unknown")),
            ],
        )

    md_path.write_text("\n".join(lines), encoding="utf-8")


def ffmpeg_cmd(
    ffmpeg: str,
    inp: Path,
    outp: Path,
    hdr: bool,
    trc: str,
    best_audio_stream: dict | None,
    all_streams: list[dict],
) -> list[str]:
    cmd = [ffmpeg, "-hide_banner", "-y" if OVERWRITE else "-n", "-hwaccel", "cuda", "-i", str(inp)]
    cmd += ["-map", "0:v:0"]

    # Map the best audio stream twice: once for AC3, once for AAC stereo
    all_audio_in_file = [s for s in all_streams if s.get("codec_type") == "audio"]
    if best_audio_stream:
        audio_idx = all_audio_in_file.index(best_audio_stream)
        # Map same source twice: Track 0 (AC3) and Track 1 (AAC stereo)
        cmd += ["-map", f"0:a:{audio_idx}"]
        cmd += ["-map", f"0:a:{audio_idx}"]

    if KEEP_SUBS:
        cmd += ["-map", "0:s?"]

    cmd += ["-map_metadata", "0", "-map_chapters", "0"]
    cmd += [
        "-c:v",
        "hevc_nvenc",
        "-gpu",
        str(GPU_INDEX),
        "-preset",
        NVENC_PRESET,
        "-rc:v",
        "vbr",
        "-cq:v",
        str(NVENC_CQ),
        "-b:v",
        "0",
        "-spatial_aq",
        "1",
        "-temporal_aq",
        "1",
        "-aq-strength",
        "8",
        "-rc-lookahead",
        "32",
    ]

    if hdr:
        cmd += [
            "-maxrate:v",
            MAXRATE_HDR,
            "-bufsize:v",
            BUFSIZE_HDR,
            "-profile:v",
            "main10",
            "-pix_fmt",
            "p010le",
            "-color_primaries",
            "bt2020",
            "-colorspace",
            "bt2020nc",
            "-color_trc",
            trc,
        ]
        transfer_num = "18" if trc == "arib-std-b67" else "16"  # HLG=18, PQ=16
        cmd += [
            "-bsf:v",
            f"hevc_metadata=colour_primaries=9:transfer_characteristics={transfer_num}:matrix_coefficients=9",
        ]
    else:
        cmd += [
            "-maxrate:v",
            MAXRATE_SDR,
            "-bufsize:v",
            BUFSIZE_SDR,
            "-profile:v",
            "main",
            "-pix_fmt",
            "yuv420p",
            "-color_primaries",
            "bt709",
            "-colorspace",
            "bt709",
            "-color_trc",
            "bt709",
        ]

    # Track 0: AC3 5.1 (or 2.0) for soundbar (HT-S40R)
    if best_audio_stream:
        src_codec = (best_audio_stream.get("codec_name") or "").lower()
        ch = int(best_audio_stream.get("channels") or 0)
        target_channels = "6" if ch >= 6 else "2"

        # If already AC3 with compatible channels, copy
        if src_codec == "ac3" and ch in {2, 6}:
            cmd += ["-c:a:0", "copy"]
        else:
            # Convert to AC3
            cmd += ["-c:a:0", "ac3", "-b:a:0", AC3_BITRATE, "-ac:a:0", target_channels]

        # Track 1: AAC stereo for headphones/compatibility (always downmix to stereo)
        cmd += ["-c:a:1", "aac", "-b:a:1", AAC_BITRATE, "-ac:a:1", "2"]

    if KEEP_SUBS:
        cmd += ["-c:s", "copy"]

    cmd += [str(outp)]
    return cmd


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <fichier_video>")

    inp_path = Path(sys.argv[1])
    if not inp_path.exists():
        raise SystemExit(f"ERROR: Fichier introuvable: {inp_path}")
    if not inp_path.is_file():
        raise SystemExit(f"ERROR: N'est pas un fichier: {inp_path}")
    if inp_path.suffix.lower() not in VIDEO_EXTS:
        raise SystemExit(f"ERROR: Extension non supportee: {inp_path.suffix}")

    ffmpeg = need("ffmpeg")
    ffprobe = need("ffprobe")
    if not has_nvenc(ffmpeg):
        raise SystemExit("ERROR: hevc_nvenc non disponible (ffmpeg sans NVENC).")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inp = inp_path.resolve()

    streams, format_info = probe(ffprobe, inp)
    v = first(streams, "video")
    if not v:
        raise SystemExit(f"SKIP (no video): {inp}")

    # Select best audio stream (french > english > most channels)
    best_audio_stream = best_audio(streams)
    if not best_audio_stream:
        raise SystemExit(f"SKIP (no audio): {inp}")

    hdr, trc = is_hdr(v)
    tag = "HDR" if hdr else "SDR"

    # Extract movie info from filename
    movie_title, year = extract_movie_info(inp.name)
    resolution = get_resolution_p(v)

    # Build clean output name
    output_stem = build_output_name(movie_title, year, resolution, tag)
    base_outp = OUT_DIR / f"{output_stem}.mkv"

    # Find available filename if not overwriting
    if OVERWRITE:
        outp = base_outp
    else:
        outp = find_available_filename(base_outp)

    # Create MD file with technical info (same stem as video file)
    md_path = OUT_DIR / f"{outp.stem}.md"

    # Create MD file immediately with source info and placeholder for target
    create_md_file(
        md_path,
        inp,
        inp.name,
        v,
        best_audio_stream,
        streams,
        format_info,
        outp,
        outp.name,
        None,  # target_video_info - will be updated after encoding
        None,  # target_audio_info - will be updated after encoding
        [],  # target_streams_info - will be updated after encoding
        {},  # target_format_info - will be updated after encoding
    )
    print(f"MD: {md_path} (created, will be updated after encoding)")

    cmd = ffmpeg_cmd(ffmpeg, inp, outp, hdr, trc, best_audio_stream, streams)
    print(f"\nIN  : {inp}\nOUT : {outp}\nMODE: {tag} (trc={trc})")
    print(
        f"AUDIO: Track 0=AC3 5.1, Track 1=AAC stereo (from {best_audio_stream.get('codec_name', 'unknown')} {best_audio_stream.get('channels', 0)}ch)"
    )
    if DRY_RUN:
        print("CMD:", " ".join(cmd))
        return
    if subprocess.run(cmd).returncode != 0:
        raise SystemExit(f"FAILED: {inp}")

    # Analyze target file after successful encoding
    target_streams, target_format_info = probe(ffprobe, outp)
    target_v = first(target_streams, "video")
    if not target_v:
        raise SystemExit(f"SKIP (no video in target): {outp}")
    target_audio_streams = [s for s in target_streams if s.get("codec_type") == "audio"]
    target_a_ac3 = target_audio_streams[0] if len(target_audio_streams) > 0 else None

    # Update MD file with target info after successful encoding
    create_md_file(
        md_path,
        inp,
        inp.name,
        v,
        best_audio_stream,
        streams,
        format_info,
        outp,
        outp.name,
        target_v,
        target_a_ac3,
        target_streams,
        target_format_info,
    )
    print(f"MD: {md_path} (updated)")


if __name__ == "__main__":
    main()
