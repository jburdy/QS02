# Parametres FFmpeg - QS02 Video Normaliser

Ce document explique et justifie tous les parametres FFmpeg utilises dans `QS02_vid_normaliser.py`.

## Parametres generaux

### `-hide_banner`
**Valeur:** Toujours present  
**Justification:** Masque la banniere d'information de FFmpeg pour reduire le bruit dans les logs. Utile pour un affichage plus propre lors de l'execution.

### `-y` / `-n`
**Valeur:** `-y` si `OVERWRITE=True`, sinon `-n`  
**Justification:** 
- `-y`: Ecrit par-dessus un fichier existant sans demander confirmation
- `-n`: Refuse d'ecraser un fichier existant (securite)
Le comportement est controle par la variable `OVERWRITE` dans la config.

### `-hwaccel cuda`
**Valeur:** `cuda`  
**Justification:** Active l'acceleration materielle CUDA pour le decodage video. Utilise le GPU NVIDIA pour decoder la video source, ce qui est beaucoup plus rapide que le decodage CPU. Necessaire pour tirer parti de la carte graphique RTX 4070.

### `-i <fichier_source>`
**Valeur:** Chemin vers le fichier video source  
**Justification:** Specifie le fichier d'entree a traiter.

## Mapping des streams

### `-map 0:v:0`
**Valeur:** Premier stream video du fichier source  
**Justification:** Selectionne le premier stream video pour l'encodage. On ne garde qu'une seule piste video (la principale).

### `-map 0:a:<index>` (2 fois)
**Valeur:** Index du meilleur stream audio (detecte automatiquement)  
**Justification:** Le meme stream audio source est mappe deux fois pour creer deux pistes audio dans la sortie:
- Track 0: AC3 (pour barre de son HT-S40R)
- Track 1: AAC stereo (pour casques/compatibilite universelle)

### `-map 0:s?` (conditionnel)
**Valeur:** Tous les streams de sous-titres si `KEEP_SUBS=True`  
**Justification:** Copie les sous-titres du fichier source. Le `?` rend le mapping optionnel (ne plante pas si aucun sous-titre). Desactive par defaut pour maximiser les chances de "Direct Play" dans Jellyfin.

### `-map_metadata 0`
**Valeur:** Copie toutes les metadonnees du fichier source  
**Justification:** Preserve les metadonnees (titre, auteur, date, etc.) du fichier source dans le fichier de sortie.

### `-map_chapters 0`
**Valeur:** Copie tous les chapitres du fichier source  
**Justification:** Preserve les marqueurs de chapitres pour permettre la navigation dans le fichier.

## Parametres video - Codec NVENC

### `-c:v hevc_nvenc`
**Valeur:** `hevc_nvenc`  
**Justification:** Utilise l'encodeur HEVC (H.265) materiel NVIDIA. Beaucoup plus rapide que l'encodage logiciel (x265) tout en offrant une excellente qualite. Ideal pour transcoder rapidement de gros volumes de videos.

### `-gpu <index>`
**Valeur:** `GPU_INDEX` (par defaut: 0)  
**Justification:** Specifie quel GPU NVIDIA utiliser pour l'encodage. Utile si plusieurs GPU sont disponibles dans le systeme.

### `-preset <valeur>`
**Valeur:** `NVENC_PRESET` (par defaut: "slow")  
**Justification:** Controle le compromis vitesse/qualite de l'encodage:
- `slow`: Meilleure qualite, encodage plus lent (recommandee)
- `medium`: Compromis vitesse/qualite
- `fast`: Encodage plus rapide, qualite legerement inferieure

### `-rc:v vbr`
**Valeur:** `vbr` (Variable Bitrate)  
**Justification:** Mode de controle de debit variable. Permet au codec d'ajuster le bitrate selon la complexite de chaque scene. Plus efficace que CBR (Constant Bitrate) pour la qualite visuelle.

### `-cq:v <valeur>`
**Valeur:** `NVENC_CQ` (par defaut: 20)  
**Justification:** Constant Quality factor. Controle la qualite visuelle:
- Valeurs plus basses (18-19) = meilleure qualite, fichiers plus gros
- Valeurs moyennes (20-21) = bon compromis pour streaming Wi-Fi
- Valeurs plus hautes (22+) = fichiers plus petits, qualite reduite
C'est le parametre principal qui controle la qualite finale.

### `-b:v 0`
**Valeur:** `0`  
**Justification:** Desactive le bitrate cible explicite. Avec `-cq:v`, le bitrate est controle par la qualite constante (CQ), pas par un bitrate fixe. Le `0` indique a FFmpeg d'utiliser uniquement le mode CQ.

### `-spatial_aq 1`
**Valeur:** `1` (active)  
**Justification:** Active la quantification adaptative spatiale. Le codec ajuste la quantisation selon la complexite spatiale de chaque frame. Ameliore la qualite visuelle en allouant plus de bits aux zones complexes.

### `-temporal_aq 1`
**Valeur:** `1` (active)  
**Justification:** Active la quantification adaptative temporelle. Le codec ajuste la quantisation selon les differences entre frames successives. Ameliore la qualite dans les scenes avec beaucoup de mouvement.

### `-aq-strength 8`
**Valeur:** `8`  
**Justification:** Force de la quantification adaptative (0-15). Valeur moyenne qui equilibre qualite et taille de fichier. Plus elevee = meilleure qualite mais fichiers plus gros.

### `-rc-lookahead 32`
**Valeur:** `32` frames  
**Justification:** Nombre de frames a analyser a l'avance pour optimiser l'encodage. Permet au codec de mieux repartir les bits entre les frames. Plus eleve = meilleure qualite mais plus de memoire utilisee. 32 est un bon compromis.

## Parametres video - Bitrate (Wi-Fi friendly)

### `-maxrate:v <valeur>`
**Valeur:** 
- HDR: `MAXRATE_HDR` (par defaut: "25M")
- SDR: `MAXRATE_SDR` (par defaut: "15M")  
**Justification:** Plafond de bitrate maximum. Limite les "pics" de debit pour eviter les buffers lors du streaming Wi-Fi. Avec VBR + CQ, le bitrate moyen sera inferieur, mais les pointes sont plafonnees.

### `-bufsize:v <valeur>`
**Valeur:**
- HDR: `BUFSIZE_HDR` (par defaut: "50M")
- SDR: `BUFSIZE_SDR` (par defaut: "30M")  
**Justification:** Taille du buffer de rate control. Doit etre environ 2x le maxrate pour permettre au codec de gerer les variations de debit. Plus grand = plus de flexibilite mais plus de latence potentielle.

## Parametres video - HDR

### `-profile:v main10` (HDR uniquement)
**Valeur:** `main10` pour HDR  
**Justification:** Profile HEVC Main10 necessaire pour encoder en 10-bit. Requis pour preserver la profondeur de couleur HDR (10 bits par canal).

### `-pix_fmt p010le` (HDR uniquement)
**Valeur:** `p010le` pour HDR  
**Justification:** Format pixel 10-bit planar YUV avec ordre little-endian. Format standard pour HDR 10-bit. Preserve toute la dynamique HDR.

### `-color_primaries bt2020` (HDR uniquement)
**Valeur:** `bt2020` pour HDR  
**Justification:** Primaires de couleur BT.2020 (Rec.2020). Gamut de couleur etendu utilise pour HDR/UHD. Beaucoup plus large que BT.709 (SDR).

### `-colorspace bt2020nc` (HDR uniquement)
**Valeur:** `bt2020nc` pour HDR  
**Justification:** Espace de couleur BT.2020 non-constant luminance. Standard pour HDR10. Le "nc" indique le mode non-constant luminance.

### `-color_trc <valeur>` (HDR uniquement)
**Valeur:** 
- `smpte2084` pour HDR10 (PQ - Perceptual Quantizer)
- `arib-std-b67` pour HLG (Hybrid Log-Gamma)  
**Justification:** Caracteristiques de transfert (transfer characteristics). Definit la courbe de transfert pour le mapping HDR:
- PQ (SMPTE ST 2084): Standard HDR10, optimise pour ecrans HDR
- HLG: Compatible avec les ecrans SDR et HDR

### `-bsf:v hevc_metadata=...` (HDR uniquement)
**Valeur:** `hevc_metadata=colour_primaries=9:transfer_characteristics=<16|18>:matrix_coefficients=9`  
**Justification:** Bitstream filter qui injecte les metadonnees HDR directement dans le flux HEVC:
- `colour_primaries=9`: BT.2020 (valeur standardisee)
- `transfer_characteristics=16`: PQ (SMPTE ST 2084) ou `18`: HLG
- `matrix_coefficients=9`: BT.2020 non-constant luminance
Ces metadonnees sont essentielles pour que les lecteurs affichent correctement les couleurs HDR.

## Parametres video - SDR

### `-profile:v main` (SDR uniquement)
**Valeur:** `main` pour SDR  
**Justification:** Profile HEVC Main 8-bit. Suffisant pour SDR qui n'a besoin que de 8 bits par canal.

### `-pix_fmt yuv420p` (SDR uniquement)
**Valeur:** `yuv420p` pour SDR  
**Justification:** Format pixel YUV 4:2:0 planaire 8-bit. Format standard pour SDR. Compatible avec tous les lecteurs.

### `-color_primaries bt709` (SDR uniquement)
**Valeur:** `bt709` pour SDR  
**Justification:** Primaires de couleur BT.709 (Rec.709). Standard pour SDR/HDTV. Gamut de couleur standard pour la television HD.

### `-colorspace bt709` (SDR uniquement)
**Valeur:** `bt709` pour SDR  
**Justification:** Espace de couleur BT.709. Standard pour SDR.

### `-color_trc bt709` (SDR uniquement)
**Valeur:** `bt709` pour SDR  
**Justification:** Caracteristiques de transfert BT.709 (gamma 2.4). Standard pour SDR.

## Parametres audio - Track 0 (AC3)

### `-c:a:0 copy` ou `-c:a:0 ac3`
**Valeur:** `copy` si deja AC3 avec canaux compatibles, sinon `ac3`  
**Justification:** 
- `copy`: Si la source est deja AC3 avec 2 ou 6 canaux, on copie sans re-encoder (gain de temps et qualite)
- `ac3`: Sinon, on encode en AC3 (Dolby Digital). Format standard pour les barres de son via ARC/HDMI.

### `-b:a:0 640k`
**Valeur:** `AC3_BITRATE` (par defaut: "640k")  
**Justification:** Bitrate AC3 de 640 kbps. Standard pour AC3 5.1. Bon compromis qualite/taille. Les barres de son comme la HT-S40R supportent bien ce format et ce bitrate.

### `-ac:a:0 <2|6>`
**Valeur:** `6` si source >= 6 canaux, sinon `2`  
**Justification:** Nombre de canaux audio:
- `6`: 5.1 surround (si la source le permet)
- `2`: Stereo (si la source est stereo ou mono)
La barre de son HT-S40R supporte les deux configurations.

## Parametres audio - Track 1 (AAC Stereo)

### `-c:a:1 aac`
**Valeur:** `aac`  
**Justification:** Encode toujours en AAC pour la deuxieme piste. AAC est le format audio le plus universellement supporte (casques Bluetooth, smartphones, TV, etc.).

### `-b:a:1 192k`
**Valeur:** `AAC_BITRATE` (par defaut: "192k")  
**Justification:** Bitrate AAC de 192 kbps. Excellent compromis qualite/taille pour du stereo. Qualite transparente pour la plupart des utilisateurs.

### `-ac:a:1 2`
**Valeur:** `2` (toujours stereo)  
**Justification:** Downmix toujours en stereo pour la compatibilite maximale. Les casques (comme les XM6) et la plupart des appareils mobiles sont stereo.

## Parametres sous-titres (conditionnel)

### `-c:s copy` (si `KEEP_SUBS=True`)
**Valeur:** `copy`  
**Justification:** Copie les sous-titres sans re-encoder. Preserve le format original. Desactive par defaut pour maximiser les chances de "Direct Play" dans Jellyfin (certains formats de sous-titres peuvent declencher un transcodage).

## Fichier de sortie

### `<chemin_sortie>`
**Valeur:** Chemin vers le fichier .mkv de sortie  
**Justification:** Format MKV (Matroska) choisi pour sa flexibilite et son support des metadonnees HDR. Format container ideal pour HEVC avec HDR.

## Resume des choix techniques

### Pourquoi NVENC HEVC?
- Encodage materiel tres rapide (RTX 4070)
- Excellente qualite avec CQ
- Support natif HDR 10-bit

### Pourquoi deux pistes audio?
- AC3 5.1: Pour la barre de son HT-S40R via HDMI ARC
- AAC Stereo: Pour casques Bluetooth et compatibilite universelle

### Pourquoi plafonner le bitrate?
- Streaming Wi-Fi: Evite les buffers lors des pointes de debit
- VBR + CQ: Qualite constante avec bitrate moyen raisonnable
- Maxrate/Bufsize: Limite les pics pour un streaming fluide

### Pourquoi des metadonnees HDR explicites?
- Tags dans le flux: Garantit la compatibilite avec tous les lecteurs
- BT.2020 + PQ/HLG: Standards HDR correctement identifies
- Direct Play: Jellyfin peut lire directement sans transcodage

### Pourquoi pas de sous-titres par defaut?
- Direct Play: Certains formats de sous-titres declenchent le transcodage dans Jellyfin
- Flexibilite: L'utilisateur peut activer `KEEP_SUBS=True` si necessaire
