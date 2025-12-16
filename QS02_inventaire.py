# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Inventaire des films dans X:\Flims pour QS02
Determine quels films sont deja compatibles QS02 et lesquels necessitent une normalisation.
"""

from pathlib import Path
import json
import shutil
import subprocess
import sys

# =========================
# CONFIG
# =========================
FILMS_DIR = Path("X:/Flims")
VIDEO_EXTS = {".mkv", ".mp4", ".m4v", ".mov"}
HDR_TRCS = {"smpte2084", "arib-std-b67"}

# Criteres QS02
QS02_VIDEO_CODECS = {"h264", "h265", "hevc"}  # QS02 supporte H264, H265 (HEVC)
QS02_AUDIO_CODECS = {"ac3", "aac"}
QS02_MAXRATE_HDR = 25_000_000  # 25M
QS02_MAXRATE_SDR = 15_000_000  # 15M


def cap(cmd):
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, p.stdout, p.stderr


def need(binname):
    p = shutil.which(binname)
    if not p:
        raise SystemExit(f"ERROR: '{binname}' introuvable dans PATH")
    return p


def probe(ffprobe, f):
    rc, out, err = cap([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(f)])
    if rc != 0 or out is None or not out.strip():
        return None, None
    try:
        data = json.loads(out)
        return data.get("streams", []), data.get("format", {})
    except (json.JSONDecodeError, TypeError):
        return None, None


def first(streams, t):
    for s in streams:
        if s.get("codec_type") == t:
            return s
    return None


def all_audio(streams):
    return [s for s in streams if s.get("codec_type") == "audio"]


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


def get_bitrate(format_info):
    try:
        return int(format_info.get("bit_rate", 0))
    except (ValueError, TypeError):
        return 0


def check_qs02_compatibility(format_info, video_info):
    issues = []
    is_compatible = True

    # Check video codec
    video_codec = (video_info.get("codec_name") or "").lower()
    if video_codec not in QS02_VIDEO_CODECS:
        issues.append(f"Codec video: {video_codec} (attendu: {', '.join(sorted(QS02_VIDEO_CODECS))})")
        is_compatible = False

    # Check bitrate limits
    hdr, trc = is_hdr(video_info)
    bitrate = get_bitrate(format_info)
    max_bitrate = QS02_MAXRATE_HDR if hdr else QS02_MAXRATE_SDR
    if bitrate > max_bitrate:
        issues.append(
            f"Bitrate trop eleve: {bitrate // 1_000_000}M (max: {max_bitrate // 1_000_000}M pour {'HDR' if hdr else 'SDR'})"
        )
        is_compatible = False

    # Check pixel format
    pix_fmt = video_info.get("pix_fmt") or ""
    if hdr:
        if not pix_fmt.endswith("10le"):
            issues.append(f"Format pixel HDR: {pix_fmt} (attendu: p010le)")
            is_compatible = False
    else:
        if pix_fmt != "yuv420p":
            issues.append(f"Format pixel SDR: {pix_fmt} (attendu: yuv420p)")
            is_compatible = False

    return is_compatible, issues


def analyze_file(ffprobe, filepath):
    streams, format_info = probe(ffprobe, filepath)
    if streams is None:
        return None, "Erreur lors de l'analyse ffprobe"

    video_info = first(streams, "video")
    if not video_info:
        return None, "Pas de piste video"

    audio_streams = all_audio(streams)

    hdr, trc = is_hdr(video_info)
    resolution = f"{video_info.get('height', 0)}p"
    video_codec = video_info.get("codec_name", "unknown")
    bitrate = get_bitrate(format_info)

    is_compatible, issues = check_qs02_compatibility(format_info, video_info)

    # Check naming (info only, not a compatibility criterion)
    has_qs02_tag = ".qs02" in filepath.stem.lower()

    result = {
        "file": filepath,
        "hdr": hdr,
        "trc": trc,
        "resolution": resolution,
        "video_codec": video_codec,
        "bitrate_mb": bitrate // 1_000_000 if bitrate > 0 else 0,
        "audio_tracks": len(audio_streams),
        "audio_codecs": [a.get("codec_name", "unknown") for a in audio_streams],
        "is_compatible": is_compatible,
        "has_qs02_tag": has_qs02_tag,
        "issues": issues,
    }

    return result, None


def format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def main():
    if not FILMS_DIR.exists():
        raise SystemExit(f"ERROR: Repertoire introuvable: {FILMS_DIR}")

    ffprobe = need("ffprobe")

    print(f"Analyse de {FILMS_DIR}...")
    print("=" * 80)

    compatible_files = []
    needs_normalization = []
    errors = []

    # Recursive scan
    video_files = []
    for ext in VIDEO_EXTS:
        video_files.extend(FILMS_DIR.rglob(f"*{ext}"))
        video_files.extend(FILMS_DIR.rglob(f"*{ext.upper()}"))

    # Deduplicate (Windows is case-insensitive)
    video_files = list(dict.fromkeys(video_files))

    total = len(video_files)
    print(f"Fichiers video trouves: {total}\n")

    for i, filepath in enumerate(video_files, 1):
        print(f"[{i}/{total}] {filepath.name}...", end=" ", flush=True)
        result, error = analyze_file(ffprobe, filepath)
        if error:
            errors.append((filepath, error))
            print(f"ERREUR: {error}")
        else:
            if result["is_compatible"]:
                compatible_files.append(result)
                print("OK (compatible QS02)")
            else:
                needs_normalization.append(result)
                print("NORMALISATION REQUISE")

    # Summary report
    print("\n" + "=" * 80)
    print("RESUME")
    print("=" * 80)
    print(f"\nTotal fichiers: {total}")
    print(f"Compatible QS02: {len(compatible_files)}")
    print(f"Normalisation requise: {len(needs_normalization)}")
    print(f"Erreurs: {len(errors)}")

    # Detailed report
    print("\n" + "=" * 80)
    print("FICHIERS COMPATIBLES QS02")
    print("=" * 80)
    if compatible_files:
        for r in sorted(compatible_files, key=lambda x: x["file"].name):
            print(f"\n{r['file'].name}")
            print(f"  Chemin: {r['file']}")
            print(f"  Resolution: {r['resolution']}")
            print(f"  HDR: {r['hdr']} ({r['trc']})")
            print(f"  Codec: {r['video_codec']}")
            print(f"  Bitrate: {r['bitrate_mb']}M")
            print(f"  Audio: {r['audio_tracks']} pistes ({', '.join(r['audio_codecs'])})")
    else:
        print("Aucun fichier compatible trouve.")

    print("\n" + "=" * 80)
    print("FICHIERS REQUERANT NORMALISATION")
    print("=" * 80)
    if needs_normalization:
        for r in sorted(needs_normalization, key=lambda x: x["file"].name):
            print(f"\n{r['file'].name}")
            print(f"  Chemin: {r['file']}")
            print(f"  Resolution: {r['resolution']}")
            print(f"  HDR: {r['hdr']} ({r['trc']})")
            print(f"  Codec: {r['video_codec']}")
            print(f"  Bitrate: {r['bitrate_mb']}M")
            print(f"  Audio: {r['audio_tracks']} pistes ({', '.join(r['audio_codecs'])})")
            if r["issues"]:
                print(f"  Problemes:")
                for issue in r["issues"]:
                    print(f"    - {issue}")
    else:
        print("Aucun fichier necessitant normalisation.")

    if errors:
        print("\n" + "=" * 80)
        print("ERREURS")
        print("=" * 80)
        for filepath, error in errors:
            print(f"{filepath.name}: {error}")

    # Write TSV file
    output_dir = Path(".")
    tsv_file = output_dir / "films_qs02_inventaire.tsv"

    with tsv_file.open("w", encoding="utf-8") as f:
        # Header
        f.write("Statut\tChemin\tResolution\tHDR\tTRC\tCodec\tBitrate_MB\tAudio_Pistes\tAudio_Codecs\tProblemes\n")

        # Write compatible files first
        for r in sorted(compatible_files, key=lambda x: x["file"].name):
            chemin = str(r["file"]).replace("\t", " ").replace("\n", " ")
            resolution = str(r["resolution"]).replace("\t", " ").replace("\n", " ")
            hdr = str(r["hdr"]).replace("\t", " ").replace("\n", " ")
            trc = str(r["trc"]).replace("\t", " ").replace("\n", " ")
            codec = str(r["video_codec"]).replace("\t", " ").replace("\n", " ")
            bitrate = str(r["bitrate_mb"]).replace("\t", " ").replace("\n", " ")
            audio_tracks = str(r["audio_tracks"]).replace("\t", " ").replace("\n", " ")
            audio_codecs = ", ".join(r["audio_codecs"]).replace("\t", " ").replace("\n", " ")
            problemes = ""
            f.write(
                f"OK\t{chemin}\t{resolution}\t{hdr}\t{trc}\t{codec}\t{bitrate}\t{audio_tracks}\t{audio_codecs}\t{problemes}\n"
            )

        # Write files needing normalization
        for r in sorted(needs_normalization, key=lambda x: x["file"].name):
            chemin = str(r["file"]).replace("\t", " ").replace("\n", " ")
            resolution = str(r["resolution"]).replace("\t", " ").replace("\n", " ")
            hdr = str(r["hdr"]).replace("\t", " ").replace("\n", " ")
            trc = str(r["trc"]).replace("\t", " ").replace("\n", " ")
            codec = str(r["video_codec"]).replace("\t", " ").replace("\n", " ")
            bitrate = str(r["bitrate_mb"]).replace("\t", " ").replace("\n", " ")
            audio_tracks = str(r["audio_tracks"]).replace("\t", " ").replace("\n", " ")
            audio_codecs = ", ".join(r["audio_codecs"]).replace("\t", " ").replace("\n", " ")
            problemes = " | ".join(r["issues"]).replace("\t", " ").replace("\n", " ")
            f.write(
                f"NON OK\t{chemin}\t{resolution}\t{hdr}\t{trc}\t{codec}\t{bitrate}\t{audio_tracks}\t{audio_codecs}\t{problemes}\n"
            )

    print(f"\n" + "=" * 80)
    print("FICHIER GENERE")
    print("=" * 80)
    print(f"Inventaire TSV: {tsv_file}")


if __name__ == "__main__":
    main()
