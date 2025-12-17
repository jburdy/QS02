# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
QS02 + Jellyfin (Wi‑Fi) : transcodage "Direct Play friendly" via NVENC (RTX 4070)

But :
- Détecter SDR/HDR avec ffprobe.
- Encoder en HEVC NVENC:
    - HDR -> HEVC Main10 10-bit (p010le) + tags BT.2020 + PQ/HLG.
    - SDR -> HEVC 8-bit (yuv420p) + tags BT.709.
- Audio:
    - Track 0 : AC3 (Dolby Digital) 5.1 si possible (HT‑S40R friendly).
    - Track 1 : AAC stéréo (casque / compat universelle, y compris XM6).
- Plafond bitrate (maxrate/bufsize) = limite les "pics" pour streaming Wi‑Fi.
  La qualité reste pilotée par CQ (constant quality) côté NVENC.

Modifie uniquement la section CONFIG.
"""

from pathlib import Path
import json, re, shutil, subprocess, sys

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
# - AC3 640k = bon standard 5.1 pour barres ARC.
# - AAC 192k stéréo = passe-partout (casques, TV, etc.).
AC3_BITRATE = "640k"
AAC_BITRATE = "192k"

OVERWRITE = False
DRY_RUN = False  # True = affiche juste les commandes

# =========================
HDR_TRCS = {"smpte2084", "arib-std-b67"}  # PQ / HLG


def cap(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def need(binname):
    p = shutil.which(binname)
    if not p:
        raise SystemExit(f"ERROR: '{binname}' introuvable dans PATH")
    return p


def has_nvenc(ffmpeg):
    rc, out, _ = cap([ffmpeg, "-hide_banner", "-encoders"])
    return rc == 0 and "hevc_nvenc" in out


def probe(ffprobe, f):
    rc, out, err = cap([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(f)])
    if rc != 0:
        raise RuntimeError(f"ffprobe failed: {f}\n{err}")
    data = json.loads(out)
    return data.get("streams", []), data.get("format", {})


def first(streams, t):
    for s in streams:
        if s.get("codec_type") == t:
            return s
    return None


def get_language(stream):
    tags = stream.get("tags", {})
    lang = (tags.get("language") or "").lower()
    if lang in {"fra", "fre", "fr"}:
        return "fr"
    if lang in {"eng", "en"}:
        return "en"
    return None


def best_audio(streams):
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


def is_hdr(video):
    trc = (video.get("color_transfer") or video.get("color_trc") or "").strip()
    if trc in HDR_TRCS:
        return True, trc
    pix = video.get("pix_fmt") or ""
    prim = video.get("color_primaries") or ""
    csp = video.get("color_space") or ""
    if pix.endswith("10le") and (prim == "bt2020" or csp in {"bt2020nc", "bt2020c"}):
        return True, "smpte2084"
    return False, "bt709"


def get_resolution_p(video):
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    if height > 0:
        return f"{height}p"
    return ""


def clean_filename(name):
    # Remove common technical info patterns
    patterns = [
        r"\b(HEVC|H\.264|H264|AVC|X264|X265|H\.265|H265)\b",
        r"\b(10bit|8bit|10-bit|8-bit)\b",
        r"\b(DTS|DTS-HD|DTSHD|TrueHD|EAC3|E-AC3|AC3|AAC|FLAC|MP3)\b",
        r"\b(BluRay|Blu-Ray|BDRip|BDR|WEBRip|WEB-DL|WEB|HDTV|DVDRip|DVD)\b",
        r"\b(REMUX|Remux|REMASTERED|Remastered)\b",
        r"\b(2160p|1080p|720p|480p|4K|UHD)\b",
        r"\b(HDR|HDR10|HDR10\+|DV|Dolby Vision|HLG)\b",
        r"\b(x264|x265|X264|X265)\b",
        r"\b(DD\+|DD5\.1|DD7\.1|5\.1|7\.1|2\.0)\b",
        r"\b(AMZN|NF|HMAX|Hulu|iTunes|iT)\b",
        # Remove brackets/parens only if they contain technical keywords
        r"\[(?:HEVC|H\.264|H264|AVC|X264|X265|H\.265|H265|10bit|8bit|DTS|TrueHD|EAC3|AC3|BluRay|BDRip|WEBRip|REMUX|2160p|1080p|720p|4K|UHD|HDR|HDR10|DV|HLG|x264|x265)\w*\]",
        r"\((?:HEVC|H\.264|H264|AVC|X264|X265|H\.265|H265|10bit|8bit|DTS|TrueHD|EAC3|AC3|BluRay|BDRip|WEBRip|REMUX|2160p|1080p|720p|4K|UHD|HDR|HDR10|DV|HLG|x264|x265)\w*\)",
    ]
    cleaned = name
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    # Clean up multiple spaces and dots
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\.+", ".", cleaned)
    cleaned = re.sub(r"[\.\s]+$", "", cleaned)
    cleaned = re.sub(r"^[\.\s]+", "", cleaned)
    return cleaned.strip()


def extract_movie_info(filename):
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


def build_output_name(movie_title, year, resolution, hdr_tag):
    parts = [movie_title]
    if year:
        parts.append(year)
    if resolution:
        parts.append(resolution)
    parts.append(hdr_tag)
    parts.append("qs02")
    return ".".join(parts)


def create_yaml_file(
    yaml_path,
    source_file,
    source_name,
    source_video_info,
    source_audio_info,
    source_streams_info,
    source_format_info,
    target_file,
    target_name,
    target_video_info,
    target_audio_info,
    target_streams_info,
    target_format_info,
):
    def escape_yaml(s):
        if s is None:
            return "null"
        s = str(s)
        # Escape quotes and wrap in quotes if contains special chars
        if any(c in s for c in [":", "#", "|", ">", "&", "*", "!", "%", "@", "`", '"', "'"]):
            escaped = s.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return s

    def add_file_section(lines, prefix, file_path, file_name, video_info, audio_info, streams_info, format_info):
        lines.append(f"{prefix}:")
        lines.append(f"  file:")
        lines.append(f"    full_name: {escape_yaml(file_name)}")
        lines.append(f"    path: {escape_yaml(str(file_path))}")
        lines.append("")
        lines.append(f"  container:")
        lines.append(f"    format_name: {escape_yaml(format_info.get('format_name', 'unknown'))}")
        lines.append(f"    format_long_name: {escape_yaml(format_info.get('format_long_name', 'unknown'))}")
        lines.append(f"    duration: {format_info.get('duration', 'unknown')}")
        lines.append(f"    size: {format_info.get('size', 'unknown')}")
        lines.append(f"    bit_rate: {format_info.get('bit_rate', 'unknown')}")
        lines.append("")
        lines.append(f"  video:")
        lines.append(f"    codec: {escape_yaml(video_info.get('codec_name', 'unknown'))}")
        lines.append(f"    codec_long_name: {escape_yaml(video_info.get('codec_long_name', 'unknown'))}")
        lines.append(f"    width: {video_info.get('width', 0)}")
        lines.append(f"    height: {video_info.get('height', 0)}")
        lines.append(f"    resolution: {escape_yaml(get_resolution_p(video_info))}")
        lines.append(f"    pixel_format: {escape_yaml(video_info.get('pix_fmt', 'unknown'))}")
        lines.append(f"    color_space: {escape_yaml(video_info.get('color_space', 'unknown'))}")
        lines.append(f"    color_primaries: {escape_yaml(video_info.get('color_primaries', 'unknown'))}")
        lines.append(
            f"    color_transfer: {escape_yaml(video_info.get('color_transfer') or video_info.get('color_trc', 'unknown'))}"
        )
        lines.append(
            f"    bit_depth: {video_info.get('bits_per_raw_sample') or video_info.get('bits_per_sample', 'unknown')}"
        )
        lines.append(f"    frame_rate: {escape_yaml(video_info.get('r_frame_rate', 'unknown'))}")
        lines.append(f"    avg_frame_rate: {escape_yaml(video_info.get('avg_frame_rate', 'unknown'))}")
        lines.append(f"    bit_rate: {video_info.get('bit_rate', 'unknown')}")
        lines.append("")
        lines.append(f"  audio:")
        if audio_info:
            lines.extend(
                [
                    f"    codec: {escape_yaml(audio_info.get('codec_name', 'unknown'))}",
                    f"    codec_long_name: {escape_yaml(audio_info.get('codec_long_name', 'unknown'))}",
                    f"    channels: {audio_info.get('channels', 0)}",
                    f"    channel_layout: {escape_yaml(audio_info.get('channel_layout', 'unknown'))}",
                    f"    sample_rate: {audio_info.get('sample_rate', 'unknown')}",
                    f"    sample_fmt: {escape_yaml(audio_info.get('sample_fmt', 'unknown'))}",
                    f"    bit_rate: {audio_info.get('bit_rate', 'unknown')}",
                ]
            )
        else:
            lines.append('    codec: "none"')
        lines.append("")
        lines.append(f"  streams:")
        lines.append(f"    total: {len(streams_info)}")
        for i, stream in enumerate(streams_info):
            stream_type = stream.get("codec_type", "unknown")
            lines.append(f"    stream_{i}:")
            lines.append(f"      type: {escape_yaml(stream_type)}")
            lines.append(f"      codec: {escape_yaml(stream.get('codec_name', 'unknown'))}")
            lines.append(f"      codec_long_name: {escape_yaml(stream.get('codec_long_name', 'unknown'))}")
            if stream_type == "video":
                lines.append(f"      resolution: {stream.get('width', 0)}x{stream.get('height', 0)}")
                lines.append(f"      pixel_format: {escape_yaml(stream.get('pix_fmt', 'unknown'))}")
            elif stream_type == "audio":
                lines.append(f"      channels: {stream.get('channels', 0)}")
                lines.append(f"      sample_rate: {stream.get('sample_rate', 'unknown')}")
            elif stream_type == "subtitle":
                lines.append(f"      codec_name: {escape_yaml(stream.get('codec_name', 'unknown'))}")

    lines = []
    add_file_section(
        lines,
        "source",
        source_file,
        source_name,
        source_video_info,
        source_audio_info,
        source_streams_info,
        source_format_info,
    )
    lines.append("")
    add_file_section(
        lines,
        "target",
        target_file,
        target_name,
        target_video_info,
        target_audio_info,
        target_streams_info,
        target_format_info,
    )

    yaml_path.write_text("\n".join(lines), encoding="utf-8")


def ffmpeg_cmd(ffmpeg, inp, outp, hdr, trc, audio_streams, all_streams):
    cmd = [ffmpeg, "-hide_banner", "-y" if OVERWRITE else "-n", "-hwaccel", "cuda", "-i", str(inp)]
    cmd += ["-map", "0:v:0"]

    # Map all audio streams by finding their audio index
    all_audio_in_file = [s for s in all_streams if s.get("codec_type") == "audio"]
    for a in audio_streams:
        audio_idx = all_audio_in_file.index(a)
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

    # Convert all audio tracks to AC3 (soundbar compatible)
    for idx, a in enumerate(audio_streams):
        src_codec = (a.get("codec_name") or "").lower()
        ch = int(a.get("channels") or 0)

        # If already AC3 with compatible channels, copy
        if src_codec == "ac3" and ch in {2, 6}:
            cmd += [f"-c:a:{idx}", "copy"]
        else:
            # Convert to AC3
            cmd += [f"-c:a:{idx}", "ac3", f"-b:a:{idx}", AC3_BITRATE, f"-ac:a:{idx}", ("6" if ch >= 6 else "2")]

    if KEEP_SUBS:
        cmd += ["-c:s", "copy"]

    cmd += [str(outp)]
    return cmd


def main():
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

    # Get all audio streams - convert all non-AC3 to AC3
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    hdr, trc = is_hdr(v)
    tag = "HDR" if hdr else "SDR"

    # Extract movie info from filename
    movie_title, year = extract_movie_info(inp.name)
    resolution = get_resolution_p(v)

    # Build clean output name
    output_stem = build_output_name(movie_title, year, resolution, tag)
    outp = OUT_DIR / f"{output_stem}.mkv"

    # Create YAML file with technical info
    yaml_path = OUT_DIR / f"{output_stem}.yaml"

    if outp.exists() and not OVERWRITE:
        print(f"SKIP (exists): {outp}")
        return

    cmd = ffmpeg_cmd(ffmpeg, inp, outp, hdr, trc, audio_streams, streams)
    print(f"\nIN  : {inp}\nOUT : {outp}\nMODE: {tag} (trc={trc})")
    print(f"AUDIO TRACKS: {len(audio_streams)}")
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
    target_a = first(target_streams, "audio")

    # Create YAML file after successful encoding
    create_yaml_file(
        yaml_path,
        inp,
        inp.name,
        v,
        audio_streams[0] if audio_streams else None,
        streams,
        format_info,
        outp,
        outp.name,
        target_v,
        target_a,
        target_streams,
        target_format_info,
    )
    print(f"YAML: {yaml_path}")


if __name__ == "__main__":
    main()
