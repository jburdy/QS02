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
import json, shutil, subprocess

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
NVENC_CQ = 19

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
    rc, out, err = cap([ffprobe, "-v", "error", "-print_format", "json", "-show_streams", str(f)])
    if rc != 0:
        raise RuntimeError(f"ffprobe failed: {f}\n{err}")
    return json.loads(out).get("streams", [])


def first(streams, t):
    for s in streams:
        if s.get("codec_type") == t:
            return s
    return None


def best_audio(streams):
    a = [s for s in streams if s.get("codec_type") == "audio"]
    if not a:
        return None
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


def ffmpeg_cmd(ffmpeg, inp, outp, hdr, trc, a):
    cmd = [ffmpeg, "-hide_banner", "-y" if OVERWRITE else "-n", "-hwaccel", "cuda", "-i", str(inp)]
    cmd += ["-map", "0:v:0"]
    if a:
        ai = int(a["index"])
        cmd += ["-map", f"0:a:{ai}", "-map", f"0:a:{ai}"]  # AC3 + AAC
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

    if a:
        src_codec = (a.get("codec_name") or "").lower()
        ch = int(a.get("channels") or 0)

        # Track 0: AC3 (soundbar)
        if src_codec == "ac3" and ch in {2, 6}:
            cmd += ["-c:a:0", "copy"]
        else:
            cmd += ["-c:a:0", "ac3", "-b:a:0", AC3_BITRATE, "-ac:a:0", ("6" if ch >= 6 else "2")]

        # Track 1: AAC stereo (headphones)
        if src_codec == "aac" and ch == 2:
            cmd += ["-c:a:1", "copy"]
        else:
            cmd += ["-c:a:1", "aac", "-b:a:1", AAC_BITRATE, "-ac:a:1", "2"]

    if KEEP_SUBS:
        cmd += ["-c:s", "copy"]

    cmd += [str(outp)]
    return cmd


def main():
    ffmpeg = need("ffmpeg")
    ffprobe = need("ffprobe")
    if not has_nvenc(ffmpeg):
        raise SystemExit("ERROR: hevc_nvenc non disponible (ffmpeg sans NVENC).")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted({p.resolve() for p in IN_DIR.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS})
    if not files:
        print(f"Aucun fichier trouvé dans {IN_DIR.resolve()}")
        return

    for inp in files:
        streams = probe(ffprobe, inp)
        v = first(streams, "video")
        if not v:
            print(f"SKIP (no video): {inp}")
            continue

        a = best_audio(streams)
        hdr, trc = is_hdr(v)
        tag = "HDR" if hdr else "SDR"
        outp = OUT_DIR / f"{inp.stem}.qs02.wifi.{tag}.mkv"

        if outp.exists() and not OVERWRITE:
            print(f"SKIP (exists): {outp}")
            continue

        cmd = ffmpeg_cmd(ffmpeg, inp, outp, hdr, trc, a)
        print(f"\nIN  : {inp}\nOUT : {outp}\nMODE: {tag} (trc={trc})")
        if DRY_RUN:
            print("CMD:", " ".join(cmd))
            continue
        if subprocess.run(cmd).returncode != 0:
            print(f"FAILED: {inp}")


if __name__ == "__main__":
    main()
