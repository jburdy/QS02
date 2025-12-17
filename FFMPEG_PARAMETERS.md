# Parametres FFmpeg - QS02 Video Normaliser (AV1 NVENC)

Ce document explique et justifie tous les parametres FFmpeg utilises dans `QS02_vid_normaliser.py` pour l'encodage AV1 via NVENC.

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

### `-c:v av1_nvenc`
**Valeur:** `av1_nvenc`  
**Justification:** Utilise l'encodeur AV1 materiel NVIDIA. Beaucoup plus rapide que l'encodage logiciel (libaom) tout en offrant une excellente qualite et une meilleure compression que HEVC. Ideal pour transcoder rapidement de gros volumes de videos avec une meilleure efficacite de compression.

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

### `-b:v <valeur>`
**Valeur:** 
- HDR: `BITRATE_HDR` (par defaut: "12M")
- SDR: `BITRATE_SDR` (par defaut: "8M")  
**Justification:** Bitrate cible pour l'encodage VBR. AV1 NVENC utilise un mode VBR avec bitrate cible plutot qu'un mode CQ. Le bitrate cible controle la qualite moyenne:
- HDR 4K: 12-15M recommandé pour une bonne qualité
- SDR 4K: 8-10M recommandé pour une bonne qualité
Le codec ajustera le bitrate autour de cette cible selon la complexité de la scène.

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

### `-pix_fmt p010le` (HDR uniquement)
**Valeur:** `p010le` pour HDR  
**Justification:** Format pixel 10-bit planar YUV avec ordre little-endian. Format standard pour HDR 10-bit. Preserve toute la dynamique HDR. AV1 supporte nativement le 10-bit sans besoin de profil specifique.

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
AV1 supporte nativement ces metadonnees HDR via les parametres de couleur standards, sans besoin de bitstream filter specifique.

## Parametres video - SDR

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
**Justification:** Format MKV (Matroska) choisi pour sa flexibilite et son support des metadonnees HDR. Format container ideal pour AV1 avec HDR.

## Resume des choix techniques

### Pourquoi NVENC AV1?
- Encodage materiel tres rapide (RTX 4070)
- Meilleure compression que HEVC pour une qualite equivalente
- Support natif HDR 10-bit
- Format moderne avec meilleur support a long terme

### Pourquoi deux pistes audio?
- AC3 5.1: Pour la barre de son HT-S40R via HDMI ARC
- AAC Stereo: Pour casques Bluetooth et compatibilite universelle

### Pourquoi plafonner le bitrate?
- Streaming Wi-Fi: Evite les buffers lors des pointes de debit
- VBR avec bitrate cible: Qualite constante avec bitrate moyen controle
- Maxrate/Bufsize: Limite les pics pour un streaming fluide

### Pourquoi des metadonnees HDR explicites?
- Tags dans le flux: Garantit la compatibilite avec tous les lecteurs
- BT.2020 + PQ/HLG: Standards HDR correctement identifies
- Direct Play: Jellyfin peut lire directement sans transcodage
- AV1 supporte nativement ces metadonnees sans bitstream filter specifique

### Pourquoi pas de sous-titres par defaut?
- Direct Play: Certains formats de sous-titres declenchent le transcodage dans Jellyfin
- Flexibilite: L'utilisateur peut activer `KEEP_SUBS=True` si necessaire
