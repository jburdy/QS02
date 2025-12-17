# Spécifications : Normaliseur Vidéo QS02 (Wi-Fi Friendly)

Ce document décrit les spécifications techniques et les directives de fonctionnement du script `QS02_vid_normaliser.py`. Ce script a pour but d'automatiser le transcodage de fichiers vidéo pour une lecture optimale sur le dongle **BenQ QS02** via **Jellyfin**, dans un environnement contraint par le Wi-Fi.

## 1. Contexte et Objectifs

*   **Cible de lecture** : Dongle BenQ QS02 (Android TV) connecté au projecteur X300G.
*   **Contrainte principale** : Streaming via **Wi-Fi**. Les fichiers bruts (Remux 4K) ont des pics de débit trop élevés (>100 Mbps) qui provoquent du *buffering*.
*   **Objectif** : Produire des fichiers "Direct Play friendly" pour Jellyfin, garantissant :
    1.  Une fluidité parfaite en Wi-Fi (lissage des pics de bitrate).
    2.  Le maintien du HDR (HDR10/HLG) et de la qualité visuelle.
    3.  Une compatibilité audio universelle (Home Cinéma 5.1 + Casque Stéréo).

## 2. Environnement Matériel Requis

*   **Encodage** : PC avec GPU NVIDIA (Architecture Turing ou plus récente recommandée, ex: RTX 4070) supportant NVENC HEVC.
*   **Logiciels** : 
    *   Python 3.13+
    *   FFmpeg (compilé avec support `hevc_nvenc`)
    *   FFprobe
*   **Périphériques Audio Cibles** :
    *   **Sony HT-S40R** (via HDMI ARC) : Nécessite du **Dolby Digital (AC3)** 5.1.
    *   **Sony WH-1000XM6** (Casque Bluetooth) : Nécessite de l'**AAC** Stéréo.

## 3. Spécifications de Traitement Vidéo

Le script utilise `hevc_nvenc` pour un encodage rapide et efficace.

### 3.1. Détection HDR/SDR
Le script analyse les métadonnées (`color_transfer` / `color_trc`) via `ffprobe` avant encodage.
*   **HDR détecté** si : Transfert `smpte2084` (PQ) ou `arib-std-b67` (HLG).
*   **SDR** : Tout autre cas (ou défaut).

### 3.2. Paramètres d'Encodage (NVENC)

| Paramètre | Valeur SDR | Valeur HDR | Justification |
| :--- | :--- | :--- | :--- |
| **Codec** | `hevc_nvenc` | `hevc_nvenc` | Standard 4K efficace supporté par QS02. |
| **Profile** | `main` | `main10` | 10-bit obligatoire pour HDR. |
| **Pix Fmt** | `yuv420p` | `p010le` | Format pixel 8-bit vs 10-bit. |
| **Colorimetrie** | BT.709 | BT.2020 / BT.2020nc | Espace couleur standard vs large gamut. |
| **Transfert** | BT.709 | SMPTE2084 (PQ) ou HLG | Courbe gamma vs HDR. |
| **Metadata** | - | `hevc_metadata` BSF | Force l'écriture des métadonnées HDR dans le flux pour déclencher le mode HDR du projecteur. |

### 3.3. Gestion du Débit (Rate Control)
Utilisation du mode **VBR** piloté par la qualité (`-cq`), mais avec un **plafond strict** (`-maxrate`, `-bufsize`) pour le Wi-Fi.

*   **Qualité cible** : `CQ = 19` (Preset `slow`).
*   **Plafonds (Wi-Fi Friendly)** :
    *   **HDR** : Maxrate **25 Mbps** / Bufsize **50 Mbps**.
    *   **SDR** : Maxrate **15 Mbps** / Bufsize **30 Mbps**.
    *   *Note : Ces valeurs permettent de conserver une qualité élevée tout en écrêtant les pics de débit qui saturent le Wi-Fi.*

## 4. Spécifications de Traitement Audio

Le script génère systématiquement **deux pistes audio** pour couvrir tous les cas d'usage sans transcodage à la volée.

### Piste 1 : Home Cinéma (Priorité Barre de son)
*   **Format** : **AC3** (Dolby Digital).
*   **Canaux** : **5.1** (Downmix automatique si source 7.1, copie si source 2.0/5.1 AC3).
*   **Bitrate** : **640 kbps**.
*   **Usage** : Assure le son Surround sur la Sony HT-S40R via HDMI ARC (qui ne supporte pas toujours l'E-AC3 ou le LPCM multicanal).

### Piste 2 : Compatibilité / Casque
*   **Format** : **AAC** (Low Complexity).
*   **Canaux** : **Stéréo (2.0)**.
*   **Bitrate** : **192 kbps**.
*   **Usage** : Lecture sur casque Bluetooth (XM6), tablette, ou TV secondaire.

## 5. Gestion des Sous-titres et Conteneur

*   **Conteneur** : **MKV** (`.mkv`). Supporte les chapitres et métadonnées complexes.
*   **Sous-titres** : 
    *   Par défaut : **Désactivés** (`KEEP_SUBS = False`).
    *   *Raison* : Les sous-titres (PGS/ASS) forcent souvent Jellyfin à faire du "Burn-in" (transcodage vidéo complet) sur Android TV, ce qui briserait le HDR et la fluidité. Le but est le **Direct Play** pur.

## 6. Logique du Script (`QS02_vid_normaliser.py`)

1.  **Initialisation** : Vérification de la présence de `ffmpeg`, `ffprobe` et du support NVENC. Création du dossier `./out`.
2.  **Scan** : Recherche récursive des fichiers vidéo dans `./in`.
3.  **Boucle de traitement** :
    *   Vérification si le fichier de sortie existe déjà (Skip si oui).
    *   **Probe** : Extraction des streams vidéo et audio.
    *   **Décision** :
        *   Sélection du premier flux vidéo.
        *   Sélection du "meilleur" flux audio (celui avec le plus de canaux).
        *   Détection du mode HDR/SDR.
    *   **Construction de la commande** : Assemblage des arguments FFmpeg selon les specs ci-dessus.
    *   **Exécution** : Lancement du processus FFmpeg.
4.  **Sortie** : Fichier nommé `{nom_source}.qs02.wifi.{SDR|HDR}.mkv`.

## 7. Configuration Rapide

Les variables suivantes en tête de script permettent d'ajuster le comportement sans toucher au code logique :

*   `IN_DIR` / `OUT_DIR` : Dossiers de travail.
*   `NVENC_CQ` : Ajustement global de la qualité (plus bas = meilleure qualité, plus lourd).
*   `MAXRATE_HDR` / `SDR` : À ajuster selon la performance réelle du réseau Wi-Fi.
*   `KEEP_SUBS` : Passer à `True` seulement si les clients supportent les sous-titres sans transcodage (ex: SRT simple).

