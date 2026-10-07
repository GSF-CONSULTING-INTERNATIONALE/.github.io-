"""Voix-off (Kokoro ff_siwis) + chronologie pour l'animation « Lakana 360 ».
Entrées  : cues.json  [[sous-titre, texte lu (facultatif)], ...] et scenes.html (data-first = 1re cue de chaque scène).
Sorties  : voix.mp3, timeline.json, voix.fr.vtt (dans <dossier_sortie>).
Usage    : python3 -I build_voix.py <dossier_modèles> <dossier_sortie>"""
import re, sys, json, os, subprocess, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
models, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
cues = [(c[0], c[1] if len(c) > 1 else c[0]) for c in json.load(open(os.path.join(here, 'cues.json'), encoding='utf-8'))]
firsts = [int(x) for x in re.findall(r'data-first="(\d+)"', open(os.path.join(here, 'scenes.html'), encoding='utf-8').read())]
assert firsts and firsts[0] == 0 and firsts == sorted(firsts) and firsts[-1] < len(cues)
SPEED, PRE, GAP, SCENE_GAP, POST = 1.1, 0.8, 0.45, 0.9, 1.6
k = Kokoro(os.path.join(models, 'kokoro.onnx'), os.path.join(models, 'voices.bin'))
def chunk(text, maxc=165):
    o, cur = [], ''
    for ph in re.split(r'(?<=[.!?])\s+', text):
        if cur and len(cur) + 1 + len(ph) > maxc: o.append(cur); cur = ph
        else: cur = (cur + ' ' + ph).strip()
    return o + [cur]
wav, sr = [], 24000
for _, spoken in cues:
    parts = []
    for p in chunk(spoken):
        x, sr = k.create(p, voice='ff_siwis', speed=SPEED, lang='fr-fr'); parts.append(x.astype(np.float32))
        parts.append(np.zeros(int(0.2 * sr), dtype=np.float32))
    wav.append(np.concatenate(parts[:-1]))
t, timed = PRE, []
for i, x in enumerate(wav):
    if i in firsts[1:]: t += SCENE_GAP - GAP
    d = len(x) / sr; timed.append((t, t + d)); t += d + GAP
total = t - GAP + POST
track = np.zeros(int((total + 0.5) * sr), dtype=np.float32)
for (a, _), x in zip(timed, wav): track[int(a * sr):int(a * sr) + len(x)] += x
sf.write('/tmp/claude-0/lakana-voix.wav', track, sr)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/claude-0/lakana-voix.wav', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '72k', os.path.join(out, 'voix.mp3')], check=True)
scenes = []
for n, f in enumerate(firsts):
    s = 0.0 if n == 0 else timed[f][0] - 0.45
    e = total if n == len(firsts) - 1 else timed[firsts[n + 1]][0] - 0.45
    scenes.append({'s': round(s, 2), 'e': round(e, 2), 'first': f})
json.dump({'total': round(total, 2), 'scenes': scenes,
           'cues': [{'s': round(a, 2), 'e': round(b, 2), 't': cues[i][0]} for i, (a, b) in enumerate(timed)]},
          open(os.path.join(out, 'timeline.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ts = lambda x: f"{int(x//3600):02d}:{int(x%3600//60):02d}:{x%60:06.3f}"
open(os.path.join(out, 'voix.fr.vtt'), 'w', encoding='utf-8').write('WEBVTT\n\n' + '\n'.join(f"{i+1}\n{ts(a)} --> {ts(b)}\n{cues[i][0]}\n" for i, (a, b) in enumerate(timed)))
print('durée', round(total, 1), 's ;', len(cues), 'cues ;', len(scenes), 'scènes')
