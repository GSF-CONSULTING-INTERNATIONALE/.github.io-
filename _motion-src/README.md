# Motion designs commentés (animation HTML + voix-off)

Un dossier par animation : `_motion-src/<nom>/` (non publié par Jekyll).

- `scenes.html` : les scènes (`<section class="mx-scene" data-first="N">`, N = index de la première cue). Chaque élément `.mx-el` apparaît quand sa cue (`data-cue`) commence, avec un délai optionnel `data-d` (secondes).
- `cues.json` : `[sous-titre, texte lu (facultatif)]` par cue. La graphie phonétique (« V P N », « sim ») va dans le texte lu.
- `build_voix.py` : synthèse Kokoro `ff_siwis`, calage des scènes sur la voix.

Régénération (modèles Kokoro `kokoro-v1.0.int8.onnx` → `kokoro.onnx` et `voices-v1.0.bin` → `voices.bin`, depuis les releases GitHub de `thewh1teagle/kokoro-onnx`) :

    pip install kokoro-onnx soundfile
    python3 -I _motion-src/<nom>/build_voix.py <dossier_modèles> uploads/motion/<nom>
    cp _motion-src/<nom>/scenes.html uploads/motion/<nom>/

Intégration dans un article : snippet CloudCannon « motion_gsf » ou
`{% include motion-design.html src="/uploads/motion/<nom>" title="…" %}`.
