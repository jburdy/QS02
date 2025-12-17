# Spécifications Techniques & Analyse : BenQ QS02 (X300G)

**Date :** 17 Décembre 2025  
**Contexte :** Module Android TV intégré au projecteur X300G  
**Type :** Dongle Streaming HDMI (Certifié Google)

## 1. Vue d'ensemble (Executive Summary)
Le QS02 n'est pas un accessoire générique mais une unité de calcul dédiée, optimisée pour l'intégration mécanique dans le X300G. Il privilégie l'efficience énergétique et la connectivité moderne (AV1, Wi-Fi 6) à la puissance brute de calcul.

## 2. Spécifications Matérielles (Hardware)

| Composant | Spécification Technique | Notes Ingénierie |
| :--- | :--- | :--- |
| **SoC** | **Amlogic S905Y4** | Quad-core Cortex-A35 @ 2.0 GHz (12nm). Architecture efficiente (basse conso/chauffe). |
| **GPU** | ARM Mali-G31 MP2 | Supporte OpenGL ES 3.2. Suffisant pour UI 4K @ 60fps. |
| **VPU (Vidéo)** | Amlogic Video Engine 10 | Décodage matériel **AV1**, VP9, H.265, H.264. Support HDR10, HDR10+, HLG. |
| **RAM** | **2 Go** LPDDR4 | Le standard strict pour Android TV. Limite le multitâche lourd. |
| **Stockage** | **16 Go** eMMC | Capacité supérieure à la moyenne (souvent 8 Go), permet le cache local. |
| **Réseau** | **Wi-Fi 6** (802.11ax) | 2x2 MIMO. Crucial pour le streaming 4K à haut débit (>50 Mbps) sans fil. |
| **Bluetooth** | Version 5.0 | Pour télécommande unifiée et périphériques audio (A2DP). |
| **I/O** | 1x Mini-HDMI (Sortie) | Format propriétaire pour l'intégration interne. |
| **OS** | Android TV 10 | Certifié Google (Play Store officiel). Mise à jour OTA supportée. |

## 3. Intégration Système (X300G)
*   **Facteur de forme :** Conception "Dongle" spécifique pour insertion dans la trappe arrière du X300G.
*   **Alimentation :** Via câble USB interne (pas de brique externe requise).
*   **Contrôle :** HDMI-CEC complet. La télécommande du projecteur contrôle directement l'OS Android via Bluetooth (appairage unique).
*   **Certification :** Netflix Natif (4K HDR), Prime Video, Disney+, etc.

## 4. Analyse Critique

### ✅ Points Forts (Pros)
*   **Support AV1 :** Avantage technique majeur sur les box plus anciennes (ex: Shield 2019). L'AV1 est le codec cible pour YouTube/Netflix 4K, offrant une meilleure qualité à débit égal.
*   **Connectivité Wi-Fi 6 :** Essentiel pour un projecteur "portable" souvent loin du routeur. Garantit la bande passante pour des flux 4K HDR sans latence.
*   **Intégration "Invisible" :** Zéro câble apparent, solution WAF (Wife Acceptance Factor) élevée.

### ⚠️ Limitations (Cons)
*   **SoC Entrée de gamme :** Le Cortex-A35 est orienté efficience, pas performance. Suffisant pour le streaming, mais limite pour l'émulation (RetroArch) au-delà des consoles 16-32 bits.
*   **RAM 2 Go :** Risque de rechargement des applications si on bascule fréquemment entre des apps lourdes (ex: Kodi <-> Plex).
*   **Audio Passthrough :** Limité par les specs Android TV standard (pas de bitstream TrueHD/DTS-HD MA garanti vers ampli externe sans configuration complexe, bien que le matériel le supporte théoriquement).

## 5. Comparatif Rapide

| Feature | **BenQ QS02** | **Nvidia Shield TV Pro** | **Google Chromecast 4K** |
| :--- | :--- | :--- | :--- |
| **Processeur** | Amlogic S905Y4 | Tegra X1+ | Amlogic S905X3 |
| **RAM** | 2 Go | **3 Go** | 2 Go |
| **Codec AV1** | **Oui** | Non | Non |
| **Wi-Fi** | **Wi-Fi 6** | Wi-Fi 5 (ac) | Wi-Fi 5 (ac) |
| **Upscaling IA** | Non | **Oui** | Non |

## 6. Verdict
Pour un usage "Consommation de média" (Streaming, Plex local, Canal+), le **QS02 est techniquement plus moderne** que beaucoup de box externes grâce à l'AV1 et le Wi-Fi 6. Inutile de le remplacer sauf besoin spécifique de puissance brute (Serveur Plex, Emulation GameCube+).
