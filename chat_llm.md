# Les meilleurs paramètres ffmpeg pour un encodage optimal 4k HDR son 5.1 pour le QS02 du X300G.

Le **X300G avec le dongle QS02** supporte HEVC 4K@60fps, HDR10/HDR10+/HLG et audio Dolby Digital Plus (jusqu'à 7.1 via eARC). Pour un encodage optimal préservant la qualité HDR et le 5.1, voici les paramètres ffmpeg recommandés.[^1_1][^1_2]

## Encodage vidéo HEVC HDR10

```bash
ffmpeg -i input.mkv \
  -c:v libx265 \
  -preset medium \
  -crf 18 \
  -pix_fmt yuv420p10le \
  -profile:v main10 \
  -color_primaries bt2020 \
  -color_trc smpte2084 \
  -colorspace bt2020nc \
  -x265-params "hdr-opt=1:repeat-headers=1:colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc:master-display='G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(10000000,50)':max-cll='1000,400'" \
  -c:a eac3 -b:a 640k -ac 6 \
  output.mkv
```


## Paramètres vidéo détaillés

| Paramètre | Valeur | Raison |
| :-- | :-- | :-- |
| **codec** | libx265 | Seul HEVC supporté à 4K@60fps par X300G [^1_1] |
| **preset** | medium | Compromis vitesse/qualité; slow si temps disponible |
| **crf** | 16-20 | 18 = haute qualité; 16 = quasi-lossless |
| **pix_fmt** | yuv420p10le | 10-bit obligatoire pour HDR10 [^1_3] |
| **profile:v** | main10 | Profile HEVC 10-bit requis [^1_4] |
| **color_trc** | smpte2084 | Courbe PQ pour HDR10 [^1_3] |

## Paramètres audio

Le QS02 supporte Dolby Digital Plus (EAC3) jusqu'à 7.1ch mais l'encodeur ffmpeg eac3 est limité à 5.1. Pour une compatibilité maximale:[^1_5]

- **EAC3 5.1**: `-c:a eac3 -b:a 640k -ac 6` (recommandé, meilleure compression que AC3)[^1_2]
- **AC3 5.1 fallback**: `-c:a ac3 -b:a 640k -ac 6` (si problèmes de compatibilité)[^1_6]


## Métadonnées HDR10

Les valeurs `master-display` et `max-cll` dans `-x265-params` sont **critiques** pour la reconnaissance HDR:[^1_4][^1_7]

- Extraire depuis source: `ffprobe -show_frames input.mkv | grep "side_data"`
- Valeurs génériques ci-dessus (1000 nits, rec.2020) fonctionnent mais moins optimal


## Critique et alternative

**Limite**: Cette commande suppose un fichier source HDR10 avec métadonnées. Si absent, le résultat sera SDR déguisé en HDR.

**Alternative pragmatique**: Pour contenus depuis streaming ou sans métadonnées fiables, encoder en SDR haute qualité (`-crf 18 -preset slow` sans params HDR) évite les artefacts de tonemapping incorrect. Le X300G applique son propre HDR-PRO  sur contenus SDR avec résultats souvent supérieurs à un faux HDR10.[^1_8]
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://www.benq.com/en-us/projector/gaming/x300g/spec.html

[^1_2]: https://www.benq.eu/en-eu/accessory/projectoraccessory/certified-android-tv-dongle-qs02.html

[^1_3]: https://www.reddit.com/r/ffmpeg/comments/g3uucr/how_do_i_encode_4k_hdr_video_as_h265_with_ffmpeg/

[^1_4]: https://forum.doom9.org/showthread.php?t=174491

[^1_5]: https://www.reddit.com/r/ffmpeg/comments/17sji2y/converting_audio_to_eac3_cmd_line_questions/

[^1_6]: https://ffmpeg.org/pipermail/ffmpeg-user/2012-May/006750.html

[^1_7]: https://stackoverflow.com/questions/48524993/encode-hevc-h-265-hdr-video-for-youtube-from-10bit-pro-res-using-ffmpeg\&rut=dac9249ade89d8a15221b2697e02eb42494f66bb08477ad6f5cebcc9aa34e0ee

[^1_8]: https://www.projectorreviews.com/benq/benq-x300g-4k-3led-portable-gaming-projector-review/

[^1_9]: https://www.benq.com/en-ap/projector/gaming/x300g/spec.html

[^1_10]: https://www.benq.com/en-ap/projector/gaming/x300g.html

[^1_11]: https://forum.libreelec.tv/thread/17729-questions-about-audio-formats-passthrough-and-conversion-on-rasberry-pi/

[^1_12]: https://www.reddit.com/r/ffmpeg/comments/1jzkd6z/adding_hdr_metadata_maxcll_maxfall_to_hevc_file/

[^1_13]: https://www.benq.eu/de-at/accessory/projectoraccessory/certified-android-tv-dongle-qs02.html

[^1_14]: https://www.reddit.com/r/kodi/comments/1gjp7p3/eac3ac3_passthrough_audio_sync_problems/

[^1_15]: https://forum.doom9.org/showthread.php?t=175260\&page=2

[^1_16]: https://www.youtube.com/watch?v=gryV0quPZz0

[^1_17]: https://community.sony.si/t5/android-tv/audio-passthrough/m-p/2366563

[^1_18]: https://trac.ffmpeg.org/ticket/7037

[^1_19]: https://www.benq.eu/de-ch/projector/gaming/x300g/buy.html

[^1_20]: https://github.com/Stremio/stremio-features/issues/812

[^1_21]: https://codecalamity.com/encoding-uhd-4k-hdr10-videos-with-ffmpeg/

[^1_22]: https://www.youtube.com/watch?v=raXPfuWCchI

[^1_23]: https://www.reddit.com/r/AndroidTV/comments/1nanpy0/any_android_tvs_not_external_box_supporting_hd/

[^1_24]: https://stackoverflow.com/questions/59813840/transcoding-hevc-4k-hdr-using-ffmpeg-and-vaapi

[^1_25]: https://www.youtube.com/watch?v=UN2DdbbVCUQ

[^1_26]: https://forums.developer.nvidia.com/t/encoding-hevc-hdr-bt2020-lost/47137

[^1_27]: https://blog.csdn.net/qq26983255/article/details/105395574

[^1_28]: https://www.reddit.com/r/ffmpeg/comments/yf9sd0/how_to_transcode_4k_hdr_using_libx265_or/

[^1_29]: https://www.reddit.com/r/ffmpeg/comments/qs8o4w/ac3_51_640_kbps_vs_eac3_51_640_kbps_which_is/

[^1_30]: https://ffmpeg.org/ffmpeg-codecs.html

[^1_31]: https://forum.doom9.org/showthread.php?t=175260

[^1_32]: https://www.reddit.com/r/ffmpeg/comments/f8083v/is_this_command_ok_for_converting_to_ac3_51/

[^1_33]: https://cloud.tencent.com/developer/ask/sof/107585192

[^1_34]: https://stackoverflow.com/questions/74611078/converting-eac3-to-aac-with-ffmpeg

[^1_35]: https://forum.doom9.org/showthread.php?t=174418

[^1_36]: https://www.reddit.com/r/ffmpeg/comments/1fos4em/aac_vs_ac3_and_what_bitrate_for_51_stereo/

[^1_37]: http://forum.doom9.org/archive/index.php/t-174418.html

[^1_38]: https://forum.videohelp.com/threads/386011-E-AC3-to-AC3-conversion-using-ffmpeg


---

# Avec ffmpeg encodage matériel nvidia rtx 4070 et contrôle aiguillage si source SDR et HDR.

Cible audio pour Sony HT-S40R via eARC HDMI et casque Sony XM6

Pour une RTX 4070, la stratégie fiable est: **NVENC HEVC 10‑bit** quand la source est HDR (PQ/HLG), et HEVC 8‑bit quand la source est SDR, en pilotant ça via `ffprobe`/bash. Les contraintes audio sont surtout côté HT‑S40R: via HDMI ARC il n’accepte que Dolby Digital (AC3) ou LPCM 2.0, donc viser AC3 5.1 (ou stéréo si la source n’a pas de 5.1).[^2_1]

## Détection SDR vs HDR (aiguillage)

Le plus robuste est de détecter HDR si le stream annonce `color_trc`/`color_transfer` = `smpte2084` (HDR10/PQ) ou `arib-std-b67` (HLG). Exemple minimal (qui marche bien en script) :[^2_2]

```bash
TRC=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer,color_trc \
  -of default=nk=1:nw=1 "input.mkv" | tr '\n' ' ')
if echo "$TRC" | grep -Eq 'smpte2084|arib-std-b67'; then
  MODE=HDR
else
  MODE=SDR
fi
```


## NVENC HDR (HEVC 10‑bit)

En HDR, force 10‑bit (`p010le`) + tags BT.2020 + PQ, sinon certains lecteurs basculent en SDR. Exemple “template” NVENC HDR (à adapter à ton contrôle débit/qualité) :[^2_3][^2_2]

```bash
ffmpeg -hwaccel cuda -i "input.mkv" \
  -map 0:v:0 -c:v hevc_nvenc -profile:v main10 -pix_fmt p010le \
  -color_primaries bt2020 -colorspace bt2020nc -color_trc smpte2084 \
  -bsf:v "hevc_metadata=transfer_characteristics=16:colour_primaries=9:matrix_coefficients=9" \
  -map 0:a:0 -c:a:0 ac3 -b:a:0 640k -ac:a:0 6 \
  -map 0:a:0 -c:a:1 aac -b:a:1 192k -ac:a:1 2 \
  "out_HDR.mkv"
```

Le bitstream filter `hevc_metadata` est utile pour “verrouiller” les infos HDR (primaries/transfer/matrix), surtout si la source est bancale ou si tu as constaté une perte de metadata.[^2_3]

## NVENC SDR (HEVC 8‑bit)

En SDR, vise Rec.709 (bt709) pour éviter un rendu délavé (mauvaise signalisation couleurs). Exemple :[^2_2]

```bash
ffmpeg -hwaccel cuda -i "input.mkv" \
  -map 0:v:0 -c:v hevc_nvenc -pix_fmt yuv420p \
  -color_primaries bt709 -colorspace bt709 -color_trc bt709 \
  -map 0:a:0 -c:a:0 ac3 -b:a:0 640k -ac:a:0 6 \
  -map 0:a:0 -c:a:1 aac -b:a:1 192k -ac:a:1 2 \
  "out_SDR.mkv"
```


## Audio: HT‑S40R + XM6

Côté ampli, la HT‑S40R via HDMI ARC annonce Dolby Digital (AC3) et LPCM 2ch, mais pas Dolby Digital Plus (E‑AC3). Côté casque, le WH‑1000XM6 supporte SBC/AAC/LDAC (Classic) et LC3 (LE Audio), donc un track AAC stéréo est un bon “passe‑partout” pour lecture sur Android TV/BT.[^2_4][^2_5][^2_1]


| Usage | Track recommandé dans le fichier | Pourquoi |
| :-- | :-- | :-- |
| Sony HT‑S40R (HDMI ARC/eARC en amont) | AC3 5.1 @ 640 kbps | Compatible Dolby Digital (5.1) côté barre [^2_1] |
| Sony WH‑1000XM6 (Bluetooth) | AAC stéréo 160–256 kbps | Codec supporté par le casque et typiquement bien géré côté lecteurs [^2_4][^2_5] |

Critique constructive: ré-encoder en NVENC “pour optimiser” n’est rentable que si tu cherches surtout vitesse/standardisation; en qualité pure, éviter de transcoder (remux + ajout d’une piste AC3/AAC de compat) donne souvent un meilleur résultat, et évite les pièges de metadata HDR. Quelle est ta priorité: taille de fichier (Go/film), vitesse d’encodage, ou qualité perçue sur le X300G ?
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_20][^2_21][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/specifications

[^2_2]: https://ffmpeg.org/ffmpeg-codecs.html

[^2_3]: https://www.reddit.com/r/ffmpeg/comments/mudgxc/ffmpeg_hardware_acceleration_hdr/

[^2_4]: https://www.sony.com/electronics/support/wireless-headphones-bluetooth-headphones/wh-1000xm6/specifications

[^2_5]: https://helpguide.sony.net/mdr/2984/v1/en/contents/TP1001856790.html

[^2_6]: https://www.sony.com/en-cd/electronics/sound-bars/ht-s40r/specifications

[^2_7]: https://www.sony-asia.com/electronics/sound-bars/ht-s40r/specifications

[^2_8]: https://www.reddit.com/r/Soundbars/comments/11468wx/just_found_out_my_new_51_soundbar_hts40r_only/

[^2_9]: https://www.sony.co.uk/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/specifications

[^2_10]: https://www.youtube.com/watch?v=ApLT2b2_jMU

[^2_11]: https://www.sony.co.in/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/specifications

[^2_12]: https://codecalamity.com/encoding-uhd-4k-hdr10-videos-with-ffmpeg/

[^2_13]: https://www.sony.co.in/electronics/sound-bars/ht-s40r/specifications

[^2_14]: https://www.reddit.com/r/ffmpeg/comments/i36i2a/encode_uhdhdr_with_hevc_nvenc_encode/

[^2_15]: https://www.youtube.com/watch?v=Vm9BK_LHMg4

[^2_16]: https://www.ruralrobo.in/soundbar/sony-s/sony-ht-s40r-soundbar-specs-review

[^2_17]: https://blog.csdn.net/qq26983255/article/details/105395574

[^2_18]: https://www.sony.ch/fr/electronics/barres-de-son/ht-s40r/specifications

[^2_19]: https://cloud.tencent.com/developer/ask/sof/107585192

[^2_20]: https://helpguide.sony.net/mdr/2984/v1/de/contents/TP1001856749.html

[^2_21]: https://www.sony.co.uk/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/faqs


---

# Fait un script python 3.14 qui gère tout ça automatiquement

Ce script Python détecte automatiquement SDR vs HDR en lisant `color_transfer`/`color_trc` via `ffprobe` (HDR si `smpte2084` ou `arib-std-b67`) et encode en HEVC NVENC (RTX 4070) avec tags couleur cohérents.[^3_1][^3_2]
Il produit un MKV avec 2 pistes audio : AC3 (Dolby Digital) pour la Sony HT‑S40R (ARC/eARC) et AAC stéréo pour un casque Sony WH‑1000XM6 (compat Bluetooth très large).[^3_3][^3_4]
Il vérifie aussi que `hevc_nvenc` est disponible dans ton ffmpeg.[^3_5][^3_6]

```python
#!/usr/bin/env python3
"""
transcode_auto_nvenc.py
Python 3.14+

Objectif:
- Auto-détection SDR/HDR via ffprobe (color_transfer/color_trc).
- Encodage vidéo HEVC NVENC (8-bit SDR / 10-bit HDR).
- Audio cible:
  - Track 0: AC3 (Dolby Digital) pour Sony HT-S40R (5.1 si possible, sinon 2.0).
  - Track 1: AAC stéréo pour casque (XM6).
- Sortie MKV, conservation optionnelle des sous-titres en "copy".

Pré-requis:
- ffmpeg + ffprobe accessibles dans PATH
- ffmpeg compilé avec NVENC (hevc_nvenc)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


HDR_TRCS = {"smpte2084", "arib-std-b67"}  # PQ / HLG


@dataclass(frozen=True)
class StreamInfo:
    index: int
    codec_type: str
    codec_name: str | None
    channels: int | None
    color_transfer: str | None
    color_trc: str | None
    color_primaries: str | None
    color_space: str | None
    pix_fmt: str | None


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    if capture:
        return subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return subprocess.run(cmd, check=False)


def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def which_or_die(bin_name: str) -> str:
    path = shutil.which(bin_name)
    if not path:
        die(f"{bin_name} not found in PATH")
    return path


def ffprobe_json(ffprobe_bin: str, input_path: Path) -> dict[str, Any]:
    cmd = [
        ffprobe_bin, "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(input_path),
    ]
    p = run(cmd, capture=True)
    if p.returncode != 0:
        die(f"ffprobe failed for {input_path}:\n{p.stderr}")
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError as e:
        die(f"ffprobe JSON parse failed: {e}")


def parse_streams(probe: dict[str, Any]) -> list[StreamInfo]:
    out: list[StreamInfo] = []
    for s in probe.get("streams", []):
        out.append(StreamInfo(
            index=int(s.get("index", -1)),
            codec_type=s.get("codec_type", ""),
            codec_name=s.get("codec_name"),
            channels=s.get("channels"),
            color_transfer=s.get("color_transfer"),
            color_trc=s.get("color_trc"),
            color_primaries=s.get("color_primaries"),
            color_space=s.get("color_space"),
            pix_fmt=s.get("pix_fmt"),
        ))
    return out


def pick_video_stream(streams: list[StreamInfo]) -> StreamInfo:
    for s in streams:
        if s.codec_type == "video":
            return s
    die("No video stream found")
    raise AssertionError


def pick_best_audio_stream(streams: list[StreamInfo]) -> Optional[StreamInfo]:
    audios = [s for s in streams if s.codec_type == "audio"]
    if not audios:
        return None
    # KISS: prendre celui avec le plus de canaux, sinon le premier.
    audios.sort(key=lambda s: (s.channels or 0, -(s.index)), reverse=True)
    return audios[^3_0]


def detect_mode(video: StreamInfo, forced: str) -> tuple[str, str]:
    """
    Returns: (MODE, TRC)
      MODE: "HDR" or "SDR"
      TRC: "smpte2084" | "arib-std-b67" | "bt709"
    """
    if forced in {"hdr", "sdr"}:
        return ("HDR", "smpte2084") if forced == "hdr" else ("SDR", "bt709")

    trc = (video.color_transfer or video.color_trc or "").strip()
    if trc in HDR_TRCS:
        return ("HDR", trc)

    # Fallback heuristique: si 10-bit + bt2020, probablement HDR.
    if (video.pix_fmt or "").endswith("10le") and (video.color_primaries == "bt2020" or video.color_space in {"bt2020nc", "bt2020c"}):
        return ("HDR", "smpte2084")

    return ("SDR", "bt709")


def ffmpeg_has_nvenc(ffmpeg_bin: str) -> bool:
    p = run([ffmpeg_bin, "-hide_banner", "-encoders"], capture=True)
    if p.returncode != 0:
        return False
    return "hevc_nvenc" in p.stdout


def build_ffmpeg_cmd(
    ffmpeg_bin: str,
    input_path: Path,
    output_path: Path,
    mode: str,
    trc: str,
    audio: Optional[StreamInfo],
    *,
    gpu: int,
    preset: str,
    cq: int,
    maxrate: Optional[str],
    bufsize: Optional[str],
    keep_subs: bool,
    overwrite: bool,
) -> list[str]:

    cmd: list[str] = [ffmpeg_bin, "-hide_banner"]
    cmd += ["-y" if overwrite else "-n"]

    # Decode acceleration (optional but helpful)
    cmd += ["-hwaccel", "cuda"]

    cmd += ["-i", str(input_path)]

    # Mapping
    cmd += ["-map", "0:v:0"]
    if audio is not None:
        cmd += ["-map", f"0:a:{audio.index}"]
        cmd += ["-map", f"0:a:{audio.index}"]  # duplicate for 2nd encoded track
    if keep_subs:
        cmd += ["-map", "0:s?"]

    # Preserve metadata/chapters (MKV handles well)
    cmd += ["-map_metadata", "0", "-map_chapters", "0"]

    # ---------- Video (NVENC HEVC) ----------
    cmd += ["-c:v", "hevc_nvenc", "-gpu", str(gpu)]
    cmd += ["-preset", preset]  # e.g. "slow", "medium"
    # Constant quality-ish for NVENC: VBR with cq + b=0
    cmd += ["-rc:v", "vbr", "-cq:v", str(cq), "-b:v", "0"]

    if maxrate:
        cmd += ["-maxrate:v", maxrate]
    if bufsize:
        cmd += ["-bufsize:v", bufsize]

    # Optional quality knobs (généralement safe)
    cmd += ["-spatial_aq", "1", "-temporal_aq", "1", "-aq-strength", "8", "-rc-lookahead", "32"]

    if mode == "HDR":
        cmd += ["-profile:v", "main10", "-pix_fmt", "p010le"]
        cmd += ["-color_primaries", "bt2020", "-colorspace", "bt2020nc", "-color_trc", trc]
        # Verrouillage metadata HEVC (PQ=16, HLG=18, bt2020 primaries=9, bt2020nc matrix=9)
        transfer_num = "18" if trc == "arib-std-b67" else "16"
        cmd += ["-bsf:v", f"hevc_metadata=colour_primaries=9:transfer_characteristics={transfer_num}:matrix_coefficients=9"]
    else:
        cmd += ["-profile:v", "main", "-pix_fmt", "yuv420p"]
        cmd += ["-color_primaries", "bt709", "-colorspace", "bt709", "-color_trc", "bt709"]

    # ---------- Audio ----------
    if audio is not None:
        src_codec = (audio.codec_name or "").lower()
        src_ch = int(audio.channels or 0)

        # Track 0: AC3 for HT-S40R
        # If already AC3, copy when possible (avoid re-encode).
        if src_codec == "ac3" and src_ch in {2, 6}:
            cmd += ["-c:a:0", "copy"]
        else:
            ac_channels = "6" if src_ch >= 6 else "2"
            # -ac will downmix automatically if needed (7.1 -> 5.1, etc.).
            cmd += ["-c:a:0", "ac3", "-b:a:0", "640k", "-ac:a:0", ac_channels]

        # Track 1: AAC stereo for headphones
        if src_codec == "aac" and src_ch == 2:
            cmd += ["-c:a:1", "copy"]
        else:
            cmd += ["-c:a:1", "aac", "-b:a:1", "192k", "-ac:a:1", "2"]
    else:
        # no audio
        pass

    # ---------- Subtitles ----------
    if keep_subs:
        cmd += ["-c:s", "copy"]

    cmd += [str(output_path)]
    return cmd


def expand_inputs(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in patterns:
        path = Path(p)
        if any(ch in p for ch in ["*", "?", "["]):
            files.extend([Path(x) for x in sorted(map(str, path.parent.glob(path.name)))])
        else:
            files.append(path)
    # Deduplicate + keep order
    seen: set[Path] = set()
    out: list[Path] = []
    for f in files:
        f = f.expanduser()
        if f not in seen:
            out.append(f)
            seen.add(f)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto SDR/HDR NVENC HEVC transcode with dual audio tracks (AC3 + AAC).")
    ap.add_argument("inputs", nargs="+", help="Input files (or globs), e.g. '*.mkv'")
    ap.add_argument("-o", "--outdir", default="out", help="Output directory")
    ap.add_argument("--mode", choices=["auto", "hdr", "sdr"], default="auto", help="Force mode or auto-detect")
    ap.add_argument("--gpu", type=int, default=0, help="NVENC GPU index (0=first)")
    ap.add_argument("--preset", default="slow", help="NVENC preset (e.g. slow|medium|fast)")
    ap.add_argument("--cq", type=int, default=19, help="NVENC constant quality target (lower=better, bigger=smaller)")
    ap.add_argument("--maxrate", default=None, help="Optional maxrate like '25M'")
    ap.add_argument("--bufsize", default=None, help="Optional bufsize like '50M'")
    ap.add_argument("--keep-subs", action="store_true", help="Copy subtitles into MKV when possible")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite output files")
    ap.add_argument("--dry-run", action="store_true", help="Print ffmpeg commands without running")
    args = ap.parse_args()

    ffmpeg_bin = which_or_die("ffmpeg")
    ffprobe_bin = which_or_die("ffprobe")

    if not ffmpeg_has_nvenc(ffmpeg_bin):
        die("ffmpeg does not expose hevc_nvenc (NVENC). Install/compile ffmpeg with NVENC support.")

    outdir = Path(args.outdir).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)

    inputs = expand_inputs(args.inputs)
    if not inputs:
        die("No input files matched.")

    for inp in inputs:
        if not inp.exists():
            print(f"SKIP (missing): {inp}", file=sys.stderr)
            continue

        probe = ffprobe_json(ffprobe_bin, inp)
        streams = parse_streams(probe)
        v = pick_video_stream(streams)
        a = pick_best_audio_stream(streams)

        mode, trc = detect_mode(v, args.mode)

        suffix = "HDR" if mode == "HDR" else "SDR"
        out_name = f"{inp.stem}.nvenc.{suffix}.mkv"
        out_path = outdir / out_name

        cmd = build_ffmpeg_cmd(
            ffmpeg_bin, inp, out_path, mode, trc, a,
            gpu=args.gpu, preset=args.preset, cq=args.cq,
            maxrate=args.maxrate, bufsize=args.bufsize,
            keep_subs=args.keep_subs, overwrite=args.overwrite,
        )

        print("\n".join([
            f"Input : {inp}",
            f"Mode  : {mode} (trc={trc})",
            f"Audio : {'none' if a is None else f'0:a:{a.index} codec={a.codec_name} ch={a.channels}'}",
            f"Output: {out_path}",
            "CMD   : " + " ".join(cmd),
            "-" * 60,
        ]))

        if not args.dry_run:
            p = run(cmd, capture=False)
            if p.returncode != 0:
                print(f"FAILED: {inp}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Utilisation (exemples) :

- Un fichier : `python transcode_auto_nvenc.py film.mkv -o out --keep-subs`
- Batch : `python transcode_auto_nvenc.py "Films/*.mkv" -o out --keep-subs --cq 19 --preset slow`
- Test sans exécuter : `python transcode_auto_nvenc.py "*.mkv" -o out --dry-run`

Question simple pour verrouiller le “BestValue” : tu veux plutôt (A) taille minimale constante (avec `--maxrate/--bufsize`) ou (B) qualité constante (laisser `--cq` faire le job, sans plafond) ?
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_18][^3_19][^3_20][^3_21][^3_22][^3_23][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://github.com/photoprism/photoprism/issues/4488

[^3_2]: https://www.ffmpeg.org/ffprobe-all.html

[^3_3]: https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/specifications

[^3_4]: https://helpguide.sony.net/mdr/2984/v1/en/contents/TP1001856790.html

[^3_5]: https://forums.developer.nvidia.com/t/nvenc-ffmpeg-plugin-cbr-options/81654

[^3_6]: https://ffmpeg.org/ffmpeg-codecs.html

[^3_7]: https://www.reddit.com/r/ffmpeg/comments/kjwxm9/how_to_detect_if_video_is_hdr_or_sdr_batch_script/

[^3_8]: https://codecalamity.com/encoding-uhd-4k-hdr10-videos-with-ffmpeg/

[^3_9]: https://github.com/cdgriffith/FastFlix/issues/102

[^3_10]: https://gensoft.pasteur.fr/docs/ffmpeg/4.3.1/ffprobe-all.html

[^3_11]: https://www.voukoder.org/forum/thread/462-hevc-nvenc-add-qmin-and-qmax/

[^3_12]: https://www.kaggle.com/code/yassinealouini/ffmpeg-101

[^3_13]: https://stackoverflow.com/questions/57893739/ffmpeg-gpu-10-bit-hevc-encoding-using-nvenc

[^3_14]: http://www.djyqxbc.vip/static/web_page/ffmpeg/ffmpeg-all.html

[^3_15]: https://www.reddit.com/r/ffmpeg/comments/1124x2z/ffmpeg_with_hevc_nvenc_am_i_doing_anything_dumb/

[^3_16]: https://manpages.ubuntu.com/manpages/focal/en/man1/ffmpeg-all.1.html

[^3_17]: https://stackoverflow.com/questions/75148787/how-to-see-default-nvenc-hevc-options-in-ffmpeg/75773676

[^3_18]: https://x265.readthedocs.io/en/master/cli.html

[^3_19]: https://www.reddit.com/r/ffmpeg/comments/supo6c/drowning_in_options_hevc_nvenc/

[^3_20]: https://www.reddit.com/r/ffmpeg/comments/1124x2z/ffmpeg_avec_hevc_nvenc_estce_que_je_fais_quelque/fr/

[^3_21]: https://forum.videohelp.com/threads/396188-What-hevc-nvenc-settings-do-work-with-lossless-preset-in-ffmpeg

[^3_22]: https://www.reddit.com/r/ffmpeg/comments/151aqiq/how_should_i_transcode_to_h264265_with_nvenc_cq/

[^3_23]: https://obsproject.com/forum/threads/true-constant-quality-mode-for-h264_nvenc-and-hevc_nvenc.158363/


---

# Laisser faire le job. Plafond raisonnable pour QS02

Pour “laisser faire” (CQ/VBR NVENC) tout en évitant des pics trop élevés pour le QS02 (lecture 4K@60 HDR10/HLG), un plafond simple et efficace est de **limiter seulement les pointes** via `-maxrate`/`-bufsize` et laisser `-cq` piloter le reste. La cible audio reste AC3 5.1 pour la HT‑S40R (Dolby Digital) + AAC stéréo pour le casque.[^4_1][^4_2][^4_3]

## Plafond “QS02” (heuristique)

Valeurs par défaut proposées (à ajuster si tu constates des saccades réseau/décodage) :

- HDR : `maxrate=45M`, `bufsize=90M`
- SDR : `maxrate=25M`, `bufsize=50M`

Ces plafonds gardent l’approche “qualité d’abord” (CQ) tout en évitant les fichiers avec des pics type UHD Blu-ray très élevés, parfois problématiques sur dongles/players.

## Patch Python (ajout auto-ceiling)

Modifs minimales à appliquer à ton script (ajout d’un preset “qs02” qui auto-renseigne `maxrate/bufsize` si l’utilisateur ne les donne pas).

**1) Ajoute un argument CLI :**

```python
ap.add_argument(
    "--ceiling",
    choices=["none", "qs02"],
    default="qs02",
    help="Bitrate ceiling preset. qs02 sets sensible maxrate/bufsize if not provided."
)
```

**2) Dans `main()`, juste après `mode, trc = detect_mode(...)`, remplace l’appel à `build_ffmpeg_cmd` par ceci :**

```python
maxrate = args.maxrate
bufsize = args.bufsize

if args.ceiling == "qs02":
    if maxrate is None:
        maxrate = "45M" if mode == "HDR" else "25M"
    if bufsize is None:
        bufsize = "90M" if mode == "HDR" else "50M"

cmd = build_ffmpeg_cmd(
    ffmpeg_bin, inp, out_path, mode, trc, a,
    gpu=args.gpu, preset=args.preset, cq=args.cq,
    maxrate=maxrate, bufsize=bufsize,
    keep_subs=args.keep_subs, overwrite=args.overwrite,
)
```

Aucun autre changement n’est requis : ton script garde `-rc:v vbr -cq:v N -b:v 0`, et le plafond ne sert qu’à couper les pics.

## Utilisation

- Auto (plafond QS02 activé par défaut) :

```bash
python transcode_auto_nvenc.py "Films/*.mkv" -o out --keep-subs
```

- Désactiver le plafond (full “laisse faire CQ”) :

```bash
python transcode_auto_nvenc.py film.mkv -o out --ceiling none
```

- Forcer un plafond custom :

```bash
python transcode_auto_nvenc.py film.mkv -o out --maxrate 35M --bufsize 70M
```

Tu vises plutôt des fichiers “streamables” (Wi‑Fi) ou lecture locale (USB/partage LAN) sur le QS02 ? Cela change beaucoup le plafond raisonnable.
<span style="display:none">[^4_10][^4_11][^4_12][^4_13][^4_14][^4_15][^4_16][^4_17][^4_18][^4_19][^4_20][^4_21][^4_22][^4_4][^4_5][^4_6][^4_7][^4_8][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://www.benq.eu/en-eu/accessory/projectoraccessory/certified-android-tv-dongle-qs02.html

[^4_2]: https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/specifications

[^4_3]: https://helpguide.sony.net/mdr/2984/v1/en/contents/TP1001856790.html

[^4_4]: https://www.reddit.com/r/MoonlightStreaming/comments/1b01eed/what_bitrate_is_needed_to_stream_4k120_with_hdr/

[^4_5]: https://infomir.store/saving-data-optimal-hd-and-4k-streaming-settings-on-mobile-networks/

[^4_6]: https://forum.jellyfin.org/t-need-help-understanding-the-affect-bitrate-has-on-quality

[^4_7]: https://emby.media/community/index.php?%2Ftopic%2F86728-4k-playback-quality-media-bitrate-exceeds-limit%2F

[^4_8]: https://community.sony.co.uk/t5/android-tv/android-tv-1-very-poor-network-performance/td-p/2271949

[^4_9]: https://www.reddit.com/r/LGOLED/comments/1f8xeli/high_bitrate_videos/

[^4_10]: https://www.benq.eu/en-uk/accessory/projectoraccessory/certified-android-tv-dongle-qs02.html

[^4_11]: https://community.adobe.com/t5/premiere-pro-discussions/recently-uploaded-4k-videos-are-limited-to-1080p-on-tv-chromecast-but-are-4k-on-pc-phone/m-p/15588650

[^4_12]: https://www.benq.com/en-us/projector/accessory/certified-android-tv-dongle-qs02.html

[^4_13]: https://github.com/jellyfin/jellyfin-androidtv/issues/3451

[^4_14]: https://www.provantage.com/benq-qs02~7BEN90VU.htm

[^4_15]: https://forums.plex.tv/t/apple-4k-hdr-prores-hevc-main-10-video-playback-issue-different-experiences-on-different-players/932197

[^4_16]: https://www.digitec.ch/en/s1/product/benq-qs02-android-10-streaming-box-53035806

[^4_17]: https://forum.libreelec.tv/thread/4382-best-settings-for-4k-hdr-playback/

[^4_18]: https://www.sotel.de/en/Home-Theater-TV/Accessories-Video-TV/Video-Accessories/Digital-Projection-Accessories/BenQ-QS02-HDMI-4K-Ultra-HD-Android-White.html

[^4_19]: https://www.benq.com/en-us/projector/accessory/certified-android-tv-dongle-qs02/specifications.html

[^4_20]: https://www.provantage.com/benq-qs02~4BEN90VU.htm

[^4_21]: https://www.jumbo-computer.com/en/products/benq-qs02-google-android-tv-dongle

[^4_22]: https://www.vali.bg/en/product/33144/print


---

# Streamable wifi. Met à jour le script. Simplifie le aussi. Pas besoin des arguments lignes de commande. Les choix seront faits en modifiant le script.

Pour du **streaming Wi‑Fi** vers le QS02, le plus stable est de garder un encodage NVENC “qualité” (`cq`) mais avec un plafond de pics via `maxrate/bufsize`, typiquement ~25 Mbps en 4K (ordre de grandeur cohérent avec les recommandations UHD grand public). Le script ci‑dessous auto-détecte SDR/HDR via `ffprobe` JSON et sort un MKV HEVC adapté, avec AC3 5.1 (HT‑S40R) + AAC stéréo (casque).[^5_1][^5_2][^5_3][^5_4]

## Choix Wi‑Fi (valeurs par défaut)

- HDR (PQ/HLG) : `MAXRATE_HDR = "25M"`, `BUFSIZE_HDR = "50M"` pour limiter les pointes et éviter les buffers sur Wi‑Fi.[^5_1]
- SDR : `MAXRATE_SDR = "15M"`, `BUFSIZE_SDR = "30M"` pour un rendu propre et très “streamable”.[^5_1]
- Le QS02 annonce la lecture 4K HDR (HDR10/HLG) et HEVC 10-bit, donc on reste en HEVC Main10 en HDR.[^5_5]


## Script (à copier tel quel)

```python
#!/usr/bin/env python3
"""
Auto transcode for QS02 streaming over Wi‑Fi:
- Detect SDR vs HDR (PQ/HLG) using ffprobe JSON.
- Encode video with NVIDIA NVENC: HEVC 8-bit (SDR) / HEVC 10-bit (HDR).
- Create 2 audio tracks:
  - Track 0: AC3 (Dolby Digital) 5.1 if possible (for Sony HT‑S40R via HDMI ARC/eARC chain)
  - Track 1: AAC stereo (for headphones / general compatibility)
- Output: MKV

Edit the CONFIG section only.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

# =========================
# CONFIG (EDIT HERE)
# =========================
INPUT_GLOBS = [
    r"./in/**/*.mkv",
    r"./in/**/*.mp4",
]

OUT_DIR = Path("./out")

# NVENC tuning (quality-first + Wi‑Fi ceiling)
NVENC_PRESET = "slow"     # "slow" | "medium" | "fast"
NVENC_CQ = 19             # lower = better quality, larger = smaller files

MAXRATE_HDR = "25M"       # Wi‑Fi friendly ceiling for 4K HDR peaks
BUFSIZE_HDR = "50M"

MAXRATE_SDR = "15M"       # Wi‑Fi friendly ceiling for 4K SDR peaks
BUFSIZE_SDR = "30M"

GPU_INDEX = 0
KEEP_SUBS = True
OVERWRITE = False

# Audio targets
AC3_BITRATE = "640k"
AAC_BITRATE = "192k"

# =========================
# INTERNALS
# =========================
HDR_TRCS = {"smpte2084", "arib-std-b67"}  # PQ / HLG


def run_capture(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def require_bin(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"ERROR: '{name}' not found in PATH")
    return path


def ffmpeg_has_hevc_nvenc(ffmpeg: str) -> bool:
    rc, out, _ = run_capture([ffmpeg, "-hide_banner", "-encoders"])
    return rc == 0 and "hevc_nvenc" in out


def ffprobe_streams(ffprobe: str, input_file: Path) -> dict:
    cmd = [
        ffprobe, "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(input_file),
    ]
    rc, out, err = run_capture(cmd)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed for {input_file}\n{err}")
    return json.loads(out)


def pick_first(streams: list[dict], codec_type: str) -> dict | None:
    for s in streams:
        if s.get("codec_type") == codec_type:
            return s
    return None


def pick_best_audio(streams: list[dict]) -> dict | None:
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    if not audios:
        return None
    # Prefer more channels (e.g., 6ch over 2ch)
    audios.sort(key=lambda s: int(s.get("channels") or 0), reverse=True)
    return audios[^5_0]


def detect_hdr(video_stream: dict) -> tuple[bool, str]:
    trc = (video_stream.get("color_transfer") or video_stream.get("color_trc") or "").strip()
    if trc in HDR_TRCS:
        return True, trc
    # Heuristic fallback: 10-bit + bt2020 often implies HDR.
    pix_fmt = (video_stream.get("pix_fmt") or "")
    prim = (video_stream.get("color_primaries") or "")
    csp = (video_stream.get("color_space") or "")
    if pix_fmt.endswith("10le") and (prim == "bt2020" or csp in {"bt2020nc", "bt2020c"}):
        return True, "smpte2084"
    return False, "bt709"


def build_cmd(ffmpeg: str, inp: Path, outp: Path, *, is_hdr: bool, trc: str, astream: dict | None) -> list[str]:
    cmd = [ffmpeg, "-hide_banner"]
    cmd += ["-y" if OVERWRITE else "-n"]
    cmd += ["-hwaccel", "cuda"]
    cmd += ["-i", str(inp)]

    # Map video
    cmd += ["-map", "0:v:0"]

    # Map audio twice (AC3 + AAC), if present
    if astream is not None:
        aidx = int(astream["index"])
        cmd += ["-map", f"0:a:{aidx}", "-map", f"0:a:{aidx}"]

    # Subs (optional)
    if KEEP_SUBS:
        cmd += ["-map", "0:s?"]

    cmd += ["-map_metadata", "0", "-map_chapters", "0"]

    # --- Video: HEVC NVENC ---
    cmd += ["-c:v", "hevc_nvenc", "-gpu", str(GPU_INDEX)]
    cmd += ["-preset", NVENC_PRESET]
    cmd += ["-rc:v", "vbr", "-cq:v", str(NVENC_CQ), "-b:v", "0"]

    # Wi‑Fi ceiling (cap peaks only)
    if is_hdr:
        cmd += ["-maxrate:v", MAXRATE_HDR, "-bufsize:v", BUFSIZE_HDR]
    else:
        cmd += ["-maxrate:v", MAXRATE_SDR, "-bufsize:v", BUFSIZE_SDR]

    # Safe-ish quality helpers
    cmd += ["-spatial_aq", "1", "-temporal_aq", "1", "-aq-strength", "8", "-rc-lookahead", "32"]

    if is_hdr:
        cmd += ["-profile:v", "main10", "-pix_fmt", "p010le"]
        cmd += ["-color_primaries", "bt2020", "-colorspace", "bt2020nc", "-color_trc", trc]
        transfer_num = "18" if trc == "arib-std-b67" else "16"  # HLG=18, PQ=16
        cmd += ["-bsf:v", f"hevc_metadata=colour_primaries=9:transfer_characteristics={transfer_num}:matrix_coefficients=9"]
    else:
        cmd += ["-profile:v", "main", "-pix_fmt", "yuv420p"]
        cmd += ["-color_primaries", "bt709", "-colorspace", "bt709", "-color_trc", "bt709"]

    # --- Audio ---
    if astream is not None:
        src_codec = (astream.get("codec_name") or "").lower()
        src_ch = int(astream.get("channels") or 0)

        # Track 0: AC3 for soundbar
        if src_codec == "ac3" and src_ch in {2, 6}:
            cmd += ["-c:a:0", "copy"]
        else:
            ac_ch = "6" if src_ch >= 6 else "2"
            cmd += ["-c:a:0", "ac3", "-b:a:0", AC3_BITRATE, "-ac:a:0", ac_ch]

        # Track 1: AAC stereo for headphones
        if src_codec == "aac" and src_ch == 2:
            cmd += ["-c:a:1", "copy"]
        else:
            cmd += ["-c:a:1", "aac", "-b:a:1", AAC_BITRATE, "-ac:a:1", "2"]

    # --- Subs ---
    if KEEP_SUBS:
        cmd += ["-c:s", "copy"]

    cmd += [str(outp)]
    return cmd


def iter_inputs(globs: list[str]) -> list[Path]:
    files: list[Path] = []
    for g in globs:
        files.extend(Path().glob(g))
    # unique + stable order
    uniq = []
    seen = set()
    for f in sorted({p.resolve() for p in files}):
        if f not in seen and f.is_file():
            uniq.append(f)
            seen.add(f)
    return uniq


def main() -> int:
    ffmpeg = require_bin("ffmpeg")
    ffprobe = require_bin("ffprobe")

    if not ffmpeg_has_hevc_nvenc(ffmpeg):
        raise SystemExit("ERROR: ffmpeg does not expose 'hevc_nvenc' (NVENC not available).")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inputs = iter_inputs(INPUT_GLOBS)

    if not inputs:
        print("No input files found. Put media under ./in/ or edit INPUT_GLOBS.")
        return 0

    for inp in inputs:
        probe = ffprobe_streams(ffprobe, inp)
        streams = probe.get("streams", [])

        v = pick_first(streams, "video")
        if not v:
            print(f"SKIP (no video): {inp}")
            continue

        a = pick_best_audio(streams)
        is_hdr, trc = detect_hdr(v)

        tag = "HDR" if is_hdr else "SDR"
        outp = OUT_DIR / f"{inp.stem}.qs02.wifi.{tag}.mkv"

        cmd = build_cmd(ffmpeg, inp, outp, is_hdr=is_hdr, trc=trc, astream=a)

        print(f"\nIN : {inp}")
        print(f"OUT: {outp}")
        print(f"MODE: {tag} (trc={trc})")
        print("CMD:", " ".join(cmd))

        p = subprocess.run(cmd)
        if p.returncode != 0:
            print(f"FAILED: {inp}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```


## Critique + alternative

- Critique: un plafond “Wi‑Fi safe” (25M HDR / 15M SDR) privilégie la fluidité, mais peut lisser les scènes très complexes (grain + mouvement), surtout si la source est un rip UHD très lourd.[^5_1]
- Alternative (si ton Wi‑Fi est excellent en 5 GHz proche, ou si tu passes en Ethernet via adaptateur) : monter `MAXRATE_HDR` vers 35–45M et `BUFSIZE_HDR` vers 70–90M tout en gardant `NVENC_CQ` identique.[^5_5]

Tu streams via Jellyfin/Plex (transfert HTTP adaptatif) ou lecture directe réseau (SMB/NFS) depuis un client Android TV ? Cela peut faire varier le plafond optimal.
<span style="display:none">[^5_10][^5_11][^5_12][^5_13][^5_14][^5_15][^5_16][^5_17][^5_18][^5_19][^5_20][^5_21][^5_22][^5_23][^5_24][^5_6][^5_7][^5_8][^5_9]</span>

<div align="center">⁂</div>

[^5_1]: https://help.netflix.com/en/node/306

[^5_2]: https://www.ffmpeg.org/ffprobe-all.html

[^5_3]: https://www.sony.com/electronics/support/sound-bars-home-theater-systems-sound-bars-surround-speakers/ht-s40r/specifications

[^5_4]: https://helpguide.sony.net/mdr/2984/v1/en/contents/TP1001856790.html

[^5_5]: https://www.benq.eu/en-eu/accessory/projectoraccessory/certified-android-tv-dongle-qs02.html

[^5_6]: https://www.highspeedinternet.com/resources/best-internet-for-netflix

[^5_7]: https://www.reddit.com/r/HomeNetworking/comments/180pog3/what_are_the_upload_download_speeds_for_netflix/

[^5_8]: https://www.reviews.org/internet-service/internet-speed-for-netflix/

[^5_9]: https://www.airband.co.uk/what-speed-broadband-do-i-need-for-netflix/

[^5_10]: https://www.reddit.com/r/hometheater/comments/1d10lqh/whats_the_minimum_4k_streaming_bitrate/

[^5_11]: https://digis.ru/distribution/proektory-aksessuary/benq_125735/?bxajaxid=3f268ada337b23636fd1e58120d64049

[^5_12]: https://www.swoop.com.au/blog/what-internet-speed-do-i-need-for-netflix/

[^5_13]: https://www.nearstream.us/blog/what-is-bitrate-for-video-and-streaming

[^5_14]: https://pokde.net/review/benq-w4000i-home-theater-4k-projector-review

[^5_15]: https://www.reddit.com/r/4kTV/comments/pb7mmj/netflix_4k_internet_speed/

[^5_16]: https://www.reddit.com/r/PleX/comments/12ausrr/average_bitrate_for_a_4k_hdr_movie/

[^5_17]: https://www.mylemon.at/artikel/benq/9h_jsc77_17e/x500i.html

[^5_18]: https://www.highspeedinternet.com/resources/how-much-speed-do-i-need-to-watch-netflix-and-hulu

[^5_19]: https://www.optimum.com/articles/internet/internet-speed-for-live-streaming

[^5_20]: https://www.manualpdf.in/benq/x3100i/manual

[^5_21]: https://www.uswitch.com/broadband/guides/broadband-for-streaming/

[^5_22]: https://inorain.com/blog/4k-streaming-bandwidth

[^5_23]: https://device.report/fccid/jvpqs02

[^5_24]: https://www.reddit.com/r/netflix/comments/17cgise/100mbps_connection_but_netflix_stream_doesnt/


---

# Oui je stresm avev jellyfin client serveur

Avec Jellyfin, l’objectif est de **Direct Play** (pas de transcodage) ; sinon le serveur ré-encode via FFmpeg dès que conteneur/codec/audio/sous-titres dépassent les capacités ou une limite de débit.[^6_1]
Du coup, pour du “streamable Wi‑Fi”, le plus fiable est : (1) encoder tes fichiers avec un plafond de pics (maxrate/bufsize) + (2) régler dans Jellyfin une limite de débit **au moins égale** à ce plafond, sinon tu risques le cas “ContainerBitrateExceedsLimit → Transcode”.[^6_2]

## Réglage Jellyfin (à faire)

- **Client Jellyfin Android TV (QS02)** : fixe “Max streaming bitrate” (évite “Auto” si tu vois des transcodes surprises), sinon Jellyfin peut décider que le débit dépasse la limite et transcoder.[^6_2]
- **Serveur Jellyfin** : évite de mettre une “Internet streaming bitrate limit” plus basse que tes fichiers, sinon tu forces le transcodage côté serveur.[^6_3]

Valeur pratique (cohérente avec le script ci-dessous) : mets **30 Mbps** en max streaming bitrate côté client (marge au-dessus de 25M HDR).

## Script Python simplifié (config dans le fichier)

Copie-colle tel quel dans `transcode_qs02_wifi.py`, mets tes fichiers dans `./in/`, lance `python transcode_qs02_wifi.py`.

```python
#!/usr/bin/env python3
"""
QS02 + Jellyfin Wi‑Fi friendly transcoder (NVIDIA RTX 4070 / NVENC)

- Auto-detect SDR vs HDR (PQ/HLG) via ffprobe JSON.
- Encode HEVC NVENC:
    SDR: 8-bit Rec.709
    HDR: 10-bit (P010) + BT.2020 + PQ/HLG tags + hevc_metadata bsf
- Audio:
    Track 0: AC3 (Dolby Digital) 5.1 if possible else 2.0  (Sony HT‑S40R friendly)
    Track 1: AAC stereo (headphones / general compatibility)
- Output MKV.

Edit only the CONFIG section.
"""

from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path

# =========================
# CONFIG (EDIT HERE)
# =========================
IN_DIR = Path("./in")
OUT_DIR = Path("./out")

VIDEO_EXTS = {".mkv", ".mp4", ".mov", ".m4v"}

GPU_INDEX = 0
NVENC_PRESET = "slow"   # slow|medium|fast
NVENC_CQ = 19           # lower=better quality, higher=smaller

# Wi‑Fi ceilings (chosen to avoid huge peaks and stay Jellyfin-friendly)
MAXRATE_HDR = "25M"
BUFSIZE_HDR = "50M"
MAXRATE_SDR = "15M"
BUFSIZE_SDR = "30M"

# If True, copies subs; can still cause Jellyfin to transcode depending on subtitle type/client.
KEEP_SUBS = False

OVERWRITE = False

AC3_BITRATE = "640k"
AAC_BITRATE = "192k"

# =========================
# INTERNALS
# =========================
HDR_TRCS = {"smpte2084", "arib-std-b67"}  # PQ / HLG

def run_capture(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr

def require_bin(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"ERROR: '{name}' not found in PATH")
    return path

def ffmpeg_has_hevc_nvenc(ffmpeg: str) -> bool:
    rc, out, _ = run_capture([ffmpeg, "-hide_banner", "-encoders"])
    return rc == 0 and "hevc_nvenc" in out

def ffprobe_json(ffprobe: str, input_file: Path) -> dict:
    rc, out, err = run_capture([
        ffprobe, "-v", "error",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(input_file)
    ])
    if rc != 0:
        raise RuntimeError(f"ffprobe failed for {input_file}\n{err}")
    return json.loads(out)

def first_stream(streams: list[dict], codec_type: str) -> dict | None:
    for s in streams:
        if s.get("codec_type") == codec_type:
            return s
    return None

def best_audio_stream(streams: list[dict]) -> dict | None:
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    if not audios:
        return None
    audios.sort(key=lambda s: int(s.get("channels") or 0), reverse=True)
    return audios[^6_0]

def detect_hdr(video: dict) -> tuple[bool, str]:
    trc = (video.get("color_transfer") or video.get("color_trc") or "").strip()
    if trc in HDR_TRCS:
        return True, trc

    # Fallback heuristic: 10-bit + bt2020 often indicates HDR.
    pix_fmt = (video.get("pix_fmt") or "")
    prim = (video.get("color_primaries") or "")
    csp = (video.get("color_space") or "")
    if pix_fmt.endswith("10le") and (prim == "bt2020" or csp in {"bt2020nc", "bt2020c"}):
        return True, "smpte2084"

    return False, "bt709"

def build_ffmpeg_cmd(ffmpeg: str, inp: Path, outp: Path, *, is_hdr: bool, trc: str, astream: dict | None) -> list[str]:
    cmd = [ffmpeg, "-hide_banner", "-y" if OVERWRITE else "-n"]
    cmd += ["-hwaccel", "cuda", "-i", str(inp)]

    # map video
    cmd += ["-map", "0:v:0"]

    # map audio twice (AC3 + AAC) if present
    if astream is not None:
        aidx = int(astream["index"])
        cmd += ["-map", f"0:a:{aidx}", "-map", f"0:a:{aidx}"]

    # optional subs
    if KEEP_SUBS:
        cmd += ["-map", "0:s?"]

    cmd += ["-map_metadata", "0", "-map_chapters", "0"]

    # ---- Video NVENC HEVC ----
    cmd += ["-c:v", "hevc_nvenc", "-gpu", str(GPU_INDEX)]
    cmd += ["-preset", NVENC_PRESET]
    cmd += ["-rc:v", "vbr", "-cq:v", str(NVENC_CQ), "-b:v", "0"]
    cmd += ["-spatial_aq", "1", "-temporal_aq", "1", "-aq-strength", "8", "-rc-lookahead", "32"]

    if is_hdr:
        cmd += ["-maxrate:v", MAXRATE_HDR, "-bufsize:v", BUFSIZE_HDR]
        cmd += ["-profile:v", "main10", "-pix_fmt", "p010le"]
        cmd += ["-color_primaries", "bt2020", "-colorspace", "bt2020nc", "-color_trc", trc]
        # lock metadata in bitstream (HLG=18, PQ=16)
        transfer_num = "18" if trc == "arib-std-b67" else "16"
        cmd += ["-bsf:v", f"hevc_metadata=colour_primaries=9:transfer_characteristics={transfer_num}:matrix_coefficients=9"]
    else:
        cmd += ["-maxrate:v", MAXRATE_SDR, "-bufsize:v", BUFSIZE_SDR]
        cmd += ["-profile:v", "main", "-pix_fmt", "yuv420p"]
        cmd += ["-color_primaries", "bt709", "-colorspace", "bt709", "-color_trc", "bt709"]

    # ---- Audio ----
    if astream is not None:
        src_codec = (astream.get("codec_name") or "").lower()
        src_ch = int(astream.get("channels") or 0)

        # Track 0: AC3 (soundbar)
        if src_codec == "ac3" and src_ch in {2, 6}:
            cmd += ["-c:a:0", "copy"]
        else:
            ac_ch = "6" if src_ch >= 6 else "2"
            cmd += ["-c:a:0", "ac3", "-b:a:0", AC3_BITRATE, "-ac:a:0", ac_ch]

        # Track 1: AAC stereo (headphones)
        if src_codec == "aac" and src_ch == 2:
            cmd += ["-c:a:1", "copy"]
        else:
            cmd += ["-c:a:1", "aac", "-b:a:1", AAC_BITRATE, "-ac:a:1", "2"]

    # ---- Subs ----
    if KEEP_SUBS:
        cmd += ["-c:s", "copy"]

    cmd += [str(outp)]
    return cmd

def iter_media_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    return sorted({p.resolve() for p in files})

def main() -> int:
    ffmpeg = require_bin("ffmpeg")
    ffprobe = require_bin("ffprobe")

    if not ffmpeg_has_hevc_nvenc(ffmpeg):
        raise SystemExit("ERROR: ffmpeg does not expose 'hevc_nvenc' (NVENC unavailable).")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = iter_media_files(IN_DIR)
    if not files:
        print(f"No media found in {IN_DIR.resolve()}")
        return 0

    for inp in files:
        probe = ffprobe_json(ffprobe, inp)
        streams = probe.get("streams", [])

        v = first_stream(streams, "video")
        if not v:
            print(f"SKIP (no video): {inp}")
            continue

        a = best_audio_stream(streams)
        is_hdr, trc = detect_hdr(v)

        tag = "HDR" if is_hdr else "SDR"
        outp = OUT_DIR / f"{inp.stem}.qs02.wifi.{tag}.mkv"

        if outp.exists() and not OVERWRITE:
            print(f"SKIP (exists): {outp}")
            continue

        cmd = build_ffmpeg_cmd(ffmpeg, inp, outp, is_hdr=is_hdr, trc=trc, astream=a)

        print(f"\nIN  : {inp}")
        print(f"OUT : {outp}")
        print(f"MODE: {tag} (trc={trc})")
        p = subprocess.run(cmd)
        if p.returncode != 0:
            print(f"FAILED: {inp}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```


## Ajustement “Jellyfin-first” (important)

- Si tu vois dans le dashboard Jellyfin que ça transcoding pour raison “bitrate/container”, augmente côté **client** la limite de streaming (ex. 30–40 Mbps) plutôt que de remonter `MAXRATE_HDR`, sinon tu te bats contre Jellyfin.[^6_2]
- Les sous-titres peuvent déclencher transcodage (burn-in), donc `KEEP_SUBS=False` est volontaire pour maximiser Direct Play; active-le seulement si tu sais que tes subs sont compatibles côté client.[^6_1]

Tu veux que le script génère aussi une **version 1080p “mobile”** (genre 6–8 Mbps) dans un second dossier, pour lecture fluide sur Wi‑Fi faible / hors maison ?
<span style="display:none">[^6_10][^6_11][^6_12][^6_13][^6_14][^6_15][^6_16][^6_17][^6_18][^6_19][^6_20][^6_4][^6_5][^6_6][^6_7][^6_8][^6_9]</span>

<div align="center">⁂</div>

[^6_1]: https://jellyfin.org/docs/general/clients/codec-support/

[^6_2]: https://github.com/jellyfin/jellyfin-androidtv/issues/2601

[^6_3]: https://www.reddit.com/r/jellyfin/comments/ub9u8d/how_to_set_bit_rate_with_internal_player_on/

[^6_4]: https://www.reddit.com/r/jellyfin/comments/jguynt/working_out_bitrate_limits_for_streaming/

[^6_5]: https://www.reddit.com/r/jellyfin/comments/d1tnpu/increase_the_max_bitrate_setting_in_the_android/

[^6_6]: https://github.com/jellyfin/jellyfin-androidtv/issues/2579

[^6_7]: https://www.rapidseedbox.com/blog/jellyfin-transcoding

[^6_8]: https://github.com/jellyfin/jellyfin-androidtv/issues/990

[^6_9]: https://github.com/jellyfin/jellyfin-androidtv/issues/1160

[^6_10]: https://github.com/jellyfin/jellyfin/issues/12469

[^6_11]: https://github.com/jellyfin/jellyfin-androidtv/issues/2055

[^6_12]: https://jellyfin.org/docs/general/post-install/transcoding/

[^6_13]: https://www.reddit.com/r/jellyfin/comments/u0m0wh/looking_for_a_bit_of_guidance_hevc_directplay_and/

[^6_14]: https://www.reddit.com/r/jellyfin/comments/ngund1/android_tv_sony_wont_directstream_high_bitrate/

[^6_15]: https://www.reddit.com/r/jellyfin/comments/t7nghp/how_can_i_force_certain_users_to_always_transcode/

[^6_16]: https://github.com/jellyfin/jellyfin-android/issues/1445

[^6_17]: https://github.com/jellyfin/jellyfin-android/issues/718

[^6_18]: https://www.reddit.com/r/jellyfin/comments/1pj5xu4/way_to_limit_transcode_bitrate/

[^6_19]: https://www.reddit.com/r/jellyfin/comments/ue7z6r/4k_hevc_wont_play_or_transcode_on_android_tv/

[^6_20]: https://www.reddit.com/r/jellyfin/comments/1132x50/force_jellyfin_to_transcode_av1_instead_of_direct/


---

# Le script est très bien. Simplifie le encore plus et documente le pour permettre de le modifier facilement si besoin. Explique aussi la raison de chaque valeur avec des alternatives justifiées.

Pour Jellyfin en Wi‑Fi, l’approche la plus stable est d’encoder des fichiers “Direct Play friendly” (codec/bitrate prévisible) afin d’éviter que le client déclenche un transcodage côté serveur.
C’est particulièrement important en HDR, car si Jellyfin transcode une source HDR, il doit tonemapper vers SDR et ne “passe” pas les métadonnées HDR telles quelles, ce qui dégrade vite le rendu.

## Pourquoi ces choix

Jellyfin cherche à faire du Direct Play quand conteneur/vidéo/audio/sous‑titres sont compatibles, sinon il passe par FFmpeg (Direct Stream / Transcode).[^7_1]
Les sous‑titres sont un déclencheur fréquent de transcodage (burn‑in), donc le script les désactive par défaut pour maximiser le Direct Play sur Android TV.[^7_1]
Côté matériel, le QS02 annonce 4K@60 et HDR10+/HDR10/HLG (donc on encode HEVC 10‑bit en HDR), et côté audio la HT‑S40R accepte Dolby Digital (AC3) et LPCM 2ch sur HDMI ARC.[^7_2][^7_3]

## Script ultra-simplifié

```python
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
IN_DIR  = Path("./in")
OUT_DIR = Path("./out")
VIDEO_EXTS = {".mkv", ".mp4", ".m4v", ".mov"}

GPU_INDEX = 0

# NVENC qualité:
# - NVENC_CQ plus bas = meilleure qualité (fichier + gros), plus haut = + petit.
#   Valeurs courantes: 18 (très propre), 19-21 (bon "streamable"), 22+ (agressif).
NVENC_PRESET = "slow"     # alternatives: "medium" si tu veux aller plus vite.
NVENC_CQ     = 19

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
    return a[^7_0]

def is_hdr(video):
    trc = (video.get("color_transfer") or video.get("color_trc") or "").strip()
    if trc in HDR_TRCS:
        return True, trc
    pix = (video.get("pix_fmt") or "")
    prim = (video.get("color_primaries") or "")
    csp  = (video.get("color_space") or "")
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
    cmd += ["-c:v", "hevc_nvenc", "-gpu", str(GPU_INDEX),
            "-preset", NVENC_PRESET, "-rc:v", "vbr", "-cq:v", str(NVENC_CQ), "-b:v", "0",
            "-spatial_aq", "1", "-temporal_aq", "1", "-aq-strength", "8", "-rc-lookahead", "32"]

    if hdr:
        cmd += ["-maxrate:v", MAXRATE_HDR, "-bufsize:v", BUFSIZE_HDR,
                "-profile:v", "main10", "-pix_fmt", "p010le",
                "-color_primaries", "bt2020", "-colorspace", "bt2020nc", "-color_trc", trc]
        transfer_num = "18" if trc == "arib-std-b67" else "16"  # HLG=18, PQ=16
        cmd += ["-bsf:v", f"hevc_metadata=colour_primaries=9:transfer_characteristics={transfer_num}:matrix_coefficients=9"]
    else:
        cmd += ["-maxrate:v", MAXRATE_SDR, "-bufsize:v", BUFSIZE_SDR,
                "-profile:v", "main", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-colorspace", "bt709", "-color_trc", "bt709"]

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
    ffmpeg  = need("ffmpeg")
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
```


## Raison des valeurs (et alternatives)

- `MAXRATE_HDR=25M / BUFSIZE_HDR=50M`: limite les pics pour un flux Wi‑Fi plus stable; si tu vois du buffering, descends (20M/40M), si ton Wi‑Fi est solide et que Jellyfin reste en Direct Play, monte (30–35M / 60–70M).
- `NVENC_CQ=19`: bon compromis “qualité perceptible / taille / débit moyen”; pour plus de qualité monte vers 18, pour plus petit monte vers 21–23 (mais risques d’artefacts sur scènes bruitées).
- `KEEP_SUBS=False`: réduit les risques de transcodage, car Jellyfin peut brûler les sous‑titres dans la vidéo selon le format et le client.[^7_1]


## Audio (pourquoi 2 pistes)

AC3 5.1 est choisi car la HT‑S40R accepte Dolby Digital sur HDMI ARC (et LPCM 2ch), donc AC3 est le choix “home cinema compatible” pour éviter des surprises.[^7_3]
AAC stéréo est ajoutée pour les usages casque; le WH‑1000XM6 supporte AAC (ainsi que SBC/LDAC en “Classic Audio” et LC3 en LE Audio), ce qui en fait une piste de secours très compatible.[^7_4]

Si tu veux, une variante du script peut aussi **forcer un plafond global Jellyfin** en générant des fichiers “HDR only” à 20M (encore plus safe Wi‑Fi) et des “SDR only” à 12M pour les séries, avec un simple switch de deux constantes.

<div align="center">⁂</div>

[^7_1]: https://www.benq.com/en-us/projector/gaming/x300g/spec.html

[^7_2]: https://www.benq.eu/en-eu/accessory/projectoraccessory/certified-android-tv-dongle-qs02.html

[^7_3]: https://www.benq.com/en-ap/projector/gaming/x300g/spec.html

[^7_4]: https://www.benq.com/en-ap/projector/gaming/x300g.html


---

# Comment favoriser la piste audio française et les sous-titres si besoin seulement.

Pour favoriser l’audio français et n’activer des sous‑titres *que si nécessaire*, il faut agir à deux niveaux : (1) côté Jellyfin (préférences langue + mode sous‑titres) et (2) dans tes fichiers (tags de langue + “default/forced” sur les pistes), car Jellyfin et les lecteurs s’appuient beaucoup sur ces métadonnées.[^8_1][^8_2]

## Côté Jellyfin (le plus important)

Dans Jellyfin (profil utilisateur / client Android TV), règle la **langue audio préférée** sur Français et le mode sous‑titres sur un mode “intelligent”/“selon besoin” (souvent nommé *Smart*), afin que les sous‑titres ne s’activent pas quand l’audio est déjà en français.[^8_3][^8_2]
Garde à l’esprit que les sous‑titres peuvent déclencher un Direct Stream ou un transcodage (burn‑in) selon le format et les capacités du client, donc “sous‑titres seulement si besoin” aide aussi à préserver le Direct Play.[^8_1]

## Dans les fichiers (rendre le choix automatique fiable)

Le plus robuste est d’avoir **une piste audio FR marquée `default`** et des sous‑titres “forced” (pour passages en langue étrangère) marqués `forced`, car beaucoup de lecteurs (dont Android TV apps) priorisent ces flags quand ils existent.[^8_2][^8_4]
Avec ffmpeg, tu peux sélectionner/marquer une piste par langue via les métadonnées `language=fra` et définir les dispositions `default/forced` avec `-disposition`.[^8_4][^8_5][^8_6]

## Comment modifier ton script

### 1) Favoriser l’audio FR (et fallback sur AAC casque)

Option simple (recommandée) : **garder tes 2 pistes de sortie** (AC3 + AAC) mais **tagger leur langue** et mettre l’AC3 en `default` si c’est la piste “home cinema” que tu veux par défaut.[^8_5][^8_6]
Ajoute dans ta fonction `ffmpeg_cmd(...)`, juste après la section audio (après avoir défini `-c:a:0 ...` et `-c:a:1 ...`) :

```python
cmd += [
  "-metadata:s:a:0", "language=fra",
  "-disposition:a:0", "default",
  "-metadata:s:a:1", "language=fra",
  "-disposition:a:1", "none",
]
```

Si tu préfères que **le casque** prenne par défaut (rare en salon), inverse `default` entre `a:0` et `a:1`.[^8_5]

### 2) Sous-titres “si besoin seulement”

Le plus efficace est d’**inclure une piste “forced”** (souvent SRT/PGS “Forced”) et de la marquer `forced` (sans la mettre `default`), car beaucoup de lecteurs affichent alors uniquement ces sous‑titres quand ils existent.[^8_2][^8_4]
Si tu actives `KEEP_SUBS=True`, tu peux aussi forcer les flags (attention : il faut connaître l’index du sous‑titre, donc c’est plus simple si tu n’en gardes qu’un) ; exemple de principe :

```python
cmd += [
  "-metadata:s:s:0", "language=fra",
  "-disposition:s:0", "forced",
]
```

Techniquement, `-disposition` sert bien à définir les flags `default/forced` des pistes, y compris sous‑titres.[^8_4]

## Variante plus “pro” (sélection par langue à l’encodage)

Si tes sources contiennent plusieurs pistes, la meilleure approche est de **mapper explicitement l’audio FR** (au lieu de “best_audio”) en utilisant la sélection par métadonnée de langue (`-map 0:m:language:fra`), puis de garder un fallback si absent.[^8_5]
Souhaites-tu que le script choisisse “fra > fre > fr” et, si aucune piste FR n’existe, qu’il prenne automatiquement l’anglais en secours ?
<span style="display:none">[^8_10][^8_11][^8_12][^8_13][^8_14][^8_15][^8_16][^8_17][^8_18][^8_19][^8_20][^8_21][^8_22][^8_7][^8_8][^8_9]</span>

<div align="center">⁂</div>

[^8_1]: https://jellyfin.org/docs/general/clients/codec-support/

[^8_2]: https://github.com/jellyfin/jellyfin-androidtv/issues/2883

[^8_3]: https://www.reddit.com/r/jellyfin/comments/v6vnla/default_language_for_subs_and_audio_on_android_tv/

[^8_4]: https://stackoverflow.com/questions/73772765/how-to-force-by-default-subtitles-ffmpeg

[^8_5]: https://stackoverflow.com/questions/40937172/mapping-streams-by-language-in-ffmpeg

[^8_6]: https://wiki.sharewiz.net/doku.php?id=ffmpeg%3Aencoding%3Aset_language

[^8_7]: https://jellyfin.org/docs/general/server/plugins/

[^8_8]: https://www.reddit.com/r/jellyfin/comments/i0jbcd/default_language_for_subs_and_audio/

[^8_9]: https://github.com/jellyfin/jellyfin-androidtv/issues/562

[^8_10]: https://github.com/jellyfin/jellyfin-media-player/issues/749

[^8_11]: https://www.reddit.com/r/ffmpeg/comments/xjz1ky/only_copy_audio_language_from_audio_metadata/

[^8_12]: https://www.reddit.com/r/jellyfin/comments/ba1jn2/androidtv_default_audiosub_language/

[^8_13]: https://www.reddit.com/r/ffmpeg/comments/12hyhe2/select_default_audio_and_subtitles/

[^8_14]: https://www.reddit.com/r/jellyfin/comments/knvb9f/is_it_possible_to_change_audio_track_to_change/

[^8_15]: https://www.reddit.com/r/PleX/comments/m3swvt/force_external_subtitles_despite_the_video_having/

[^8_16]: https://github.com/jellyfin/jellyfin-androidtv/issues/230

[^8_17]: https://stackoverflow.com/questions/57177713/ffmpeg-map-audio-and-subtitle-stream-of-different-specific-language-only

[^8_18]: https://stackoverflow.com/questions/61349864/how-can-i-insert-an-empty-subtitle

[^8_19]: https://forum.jellyfin.org/t-default-audio-language

[^8_20]: https://www.reddit.com/r/ffmpeg/comments/s2xin7/map_first_stream_of_a_specific_language/

[^8_21]: https://forums.plex.tv/t/how-do-i-automatically-load-forced-subtitles-but-not-normal-english-subtitles/141314

[^8_22]: https://www.reddit.com/r/jellyfin/comments/1oif059/jellyfin_android_tv_language_selection_option/

