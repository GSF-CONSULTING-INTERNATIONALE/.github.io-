---
name: video-motion-design
description: Produire ou modifier un motion design commenté (animation HTML + voix-off de synthèse Kokoro + sous-titres, export MP4 pour les réseaux sociaux) pour une analyse du site gsfconsultinginternational.com, en remplacement de l'infographie. À utiliser pour toute nouvelle animation, toute retouche de texte ou de scène, toute régénération de la voix ou tout export MP4.
---

# Motion design commenté (site GSF Consulting International)

Chaîne éprouvée sur l'analyse « Lakana 360 » (`_posts/2026-10-07-lakana-360-…`). Elle découle de la compétence du même nom du dépôt `wadagni-verite/wadagni-verite` (chaîne MP4 + Kokoro) ; ici l'animation est **intégrée à la page en HTML**, le MP4 n'est qu'un export pour les réseaux sociaux. Tout est reproductible dans l'environnement cloud, sans logiciel de montage.

## Ligne éditoriale
- Chaque affirmation à l'écran vient de l'article validé : ne rien ajouter, ne jamais citer un chiffre de mémoire.
- Les faits rapportés par une source (rapport, presse) gardent leur conditionnel et leur attribution (« selon Anthropic », « aurait »). Pas de qualification juridique que l'article n'emploie pas.
- Une idée par scène, texte court à l'écran (couleurs : cyan = idée forte, rouge = risque, or = repère).
- Ne pas retirer une scène ou une phrase dictée par l'éditeur sans demande.

## Fichiers
- `_includes/motion-design.html` : lecteur (canevas 1280×720 mis à l'échelle, voix `<audio preload="none">`, barre de lecture, bouton CC). Rien ne se charge avant le clic. Expose `root.__mxSeek(t)` pour l'export.
- `css/style.css` : bloc « MOTION DESIGN COMMENTÉ » (classes `.mx-*` : `mx-tag`, `mx-huge`, `mx-big`, `mx-mid`, `mx-card`, `mx-chip`, `mx-risk`, `mx-req`, `mx-verb`, `mx-q`, `mx-brand`…).
- `_motion-src/<nom>/` (non publié) : `scenes.html` (scènes `<section class="mx-scene" data-first="N">`, N = index de la 1re cue ; éléments `.mx-el data-cue="k" data-d="délai en s"`, positionnés en absolu), `cues.json` (`[sous-titre, texte lu facultatif]`), `build_voix.py`.
- `uploads/motion/<nom>/` (publié) : `scenes.html` (copie), `timeline.json`, `voix.mp3`, `voix.fr.vtt`, `<nom>.mp4`.
- `_motion-src/render.js` : export MP4. `cloudcannon.config.yml` : snippet `motion_gsf`.

## Procédure
1. **Script** : écrire les cues (une phrase ≈ une cue, ≤ 170 caractères de sous-titre) et les scènes. Durée cible 2–3 min. Chaque élément apparaît à sa cue (+ `data-d`) ; vérifier que `data-d` < durée de la cue.
2. **Mise en page** : tout contenu au-dessus de y ≈ 530 (le sous-titre occupe le bas, jusqu'à 3 lignes) ; vérifier qu'aucune carte ne déborde ni ne chevauche une autre (les textes courts !).
3. **Voix** : `python3 -I _motion-src/<nom>/build_voix.py <modèles> uploads/motion/<nom>` puis `cp _motion-src/<nom>/scenes.html uploads/motion/<nom>/`. Écrit `voix.mp3`, `timeline.json` (scènes recalées sur la voix), `voix.fr.vtt`.
4. **Contrôle visuel** : `jekyll build`, serveur statique (`python3 -m http.server` dans `_site`), puis captures Playwright en positionnant la lecture sur `.mx-seek` (événement `input`) ou via `__mxSeek(t)`. Regarder chaque scène à `fin − 0,6 s`.
5. **Intégration** : dans l'article, `{% include motion-design.html src="/uploads/motion/<nom>" title="…" caption="…" %}` (ou snippet CloudCannon « motion_gsf »), suivi d'un `<details class="mx-transcript">` listant les sous-titres (même texte que `timeline.json`).
6. **MP4** (en arrière-plan, 3–6 min) : `NODE_PATH=$(dirname $(readlink -f $(npm root -g)/playwright)) node _motion-src/render.js <url_page_construite> uploads/motion/<nom>/voix.mp3 uploads/motion/<nom>/<nom>.mp4`. `ONLY=12,60` ne produit que des images de contrôle (`still-*.png`, à supprimer).
7. Commit, push, PR (seulement si l'éditeur la demande).

## Voix-off (Kokoro)
- `pip install kokoro-onnx soundfile`. Modèles (seuls GitHub *releases* et PyPI sont joignables ; Hugging Face est bloqué) : `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx` → `kokoro.onnx` et `…/voices-v1.0.bin` → `voices.bin`.
- Voix `ff_siwis`, vitesse 1,1. La synthèse dure ~5 min pour 2 min 35 : la lancer en arrière-plan.
- **On ne peut pas écouter l'audio** : vérifier la durée, `volumedetect`, et prévenir l'éditeur d'écouter les noms propres et sigles. Les corrections se font dans le texte lu de `cues.json` (graphie phonétique : « V P N », « K Y C », « sim », nombres en lettres, « intelligence artificielle » pour « IA »).

## Pièges rencontrés
- **`pkill -f motif`** tue aussi le shell qui contient le motif (exit 144) : tuer par PID (`pgrep -f` puis `kill`).
- `jekyll build` échoue avec « from ASCII-8BIT to UTF-8 » : `export LANG=C.UTF-8 LC_ALL=C.UTF-8`. Lancer via `bundle exec ruby -e 'require "jekyll"; Jekyll::Commands::Build.process({"destination"=>"/tmp/…/_site"})'` (l'exécutable `jekyll` n'est pas sur le PATH).
- `pip download` laisse des `.whl` dans le répertoire courant : ne pas l'exécuter dans le dépôt.
- Le contenu de `{% include %}` passe par kramdown (`parse_block_html: true`) : pas de ligne vide dans le balisage ni dans le `<script>` de l'include.
- Le sous-titre est en `cqw` : le cadre doit rester `container-type: inline-size`.
- Entre deux scènes l'écran passe brièvement au noir (fondu croisé 0,45 s) : voulu.
- Le Chromium de test n'a pas H.264/AAC : vérifier le MP4 avec `ffprobe` (`h264` + `aac`), pas par lecture.
- **Écrire ≠ brancher** : après avoir produit un média, vérifier que l'article pointe bien dessus.
