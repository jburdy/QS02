# Specifications Techniques — BenQ QS02 (X300G)

**Date :** 17 Decembre 2025  
**Contexte :** Module Android TV integre au projecteur X300G  
**Type :** Dongle Streaming HDMI (Certifie Google)

## Vue d'ensemble

Le QS02 n'est pas un accessoire generique mais une unite de calcul dediee, optimisee pour l'integration mecanique dans le X300G. Il privilegie l'efficience energetique et la connectivite moderne (AV1, Wi-Fi 6) a la puissance brute de calcul.

## Specifications techniques

### Specifications materielles (Hardware)

| Composant | Specification technique | Notes |
|---|---|---|
| **SoC** | **Amlogic S905Y4** | Quad-core Cortex-A35 @ 2.0 GHz (12nm). Architecture efficiente (basse conso/chauffe). |
| **GPU** | ARM Mali-G31 MP2 | Supporte OpenGL ES 3.2. Suffisant pour UI 4K @ 60fps. |
| **VPU (Video)** | Amlogic Video Engine 10 | Decodage materiel **AV1**, VP9, H.265, H.264. Support HDR10, HDR10+, HLG. |
| **RAM** | **2 Go** LPDDR4 | Le standard strict pour Android TV. Limite le multitache lourd. |
| **Stockage** | **16 Go** eMMC | Capacite superieure a la moyenne (souvent 8 Go), permet le cache local. |
| **Reseau** | **Wi-Fi 6** (802.11ax) | 2x2 MIMO. Crucial pour le streaming 4K a haut debit (>50 Mbps) sans fil. |
| **Bluetooth** | Version 5.0 | Pour telecommande unifiee et peripheriques audio (A2DP). |
| **I/O** | 1x Mini-HDMI (Sortie) | Format proprietaire pour l'integration interne. |
| **OS** | Android TV 10 | Certifie Google (Play Store officiel). Mise a jour OTA supportee. |

### Integration systeme (X300G)

| Aspect | Detail |
|---|---|
| **Facteur de forme** | Conception "Dongle" specifique pour insertion dans la trappe arriere du X300G |
| **Alimentation** | Via cable USB interne (pas de brique externe requise) |
| **Controle** | HDMI-CEC complet. La telecommande du projecteur controle directement l'OS Android via Bluetooth (appairage unique) |
| **Certification** | Netflix Natif (4K HDR), Prime Video, Disney+, etc. |

## Limitations importantes

### ⚠️ Points a considerer

- **SoC Entree de gamme :** Le Cortex-A35 est oriente efficience, pas performance. Suffisant pour le streaming, mais limite pour l'emulation (RetroArch) au-dela des consoles 16-32 bits.
- **RAM 2 Go :** Risque de rechargement des applications si on bascule frequemment entre des apps lourdes (ex: Kodi <-> Plex).
- **Audio Passthrough :** Limite par les specs Android TV standard (pas de bitstream TrueHD/DTS-HD MA garanti vers ampli externe sans configuration complexe, bien que le materiel le supporte theoriquement).

## Points forts

- **Support AV1 :** Avantage technique majeur sur les box plus anciennes (ex: Shield 2019). L'AV1 est le codec cible pour YouTube/Netflix 4K, offrant une meilleure qualite a debit egal.
- **Connectivite Wi-Fi 6 :** Essentiel pour un projecteur "portable" souvent loin du routeur. Garantit la bande passante pour des flux 4K HDR sans latence.
- **Integration "Invisible" :** Zero cable apparent, solution WAF (Wife Acceptance Factor) elevee.

## Notes techniques

### Comparatif rapide

| Feature | **BenQ QS02** | **Nvidia Shield TV Pro** | **Google Chromecast 4K** |
|---|---|---|---|
| **Processeur** | Amlogic S905Y4 | Tegra X1+ | Amlogic S905X3 |
| **RAM** | 2 Go | **3 Go** | 2 Go |
| **Codec AV1** | **Oui** | Non | Non |
| **Wi-Fi** | **Wi-Fi 6** | Wi-Fi 5 (ac) | Wi-Fi 5 (ac) |
| **Upscaling IA** | Non | **Oui** | Non |

### Verdict

Pour un usage "Consommation de media" (Streaming, Plex local, Canal+), le **QS02 est techniquement plus moderne** que beaucoup de box externes grace a l'AV1 et le Wi-Fi 6. Inutile de le remplacer sauf besoin specifique de puissance brute (Serveur Plex, Emulation GameCube+).
