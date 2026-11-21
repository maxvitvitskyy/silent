# Витягує вшиті в mp3 обкладинки з SILENT_PLAYLISTS/READY у tools/playlists/covers/
# і прив'язує їх до треків за тим самим ключем, що й сторінка: normKey(виконавець)|normKey(назва).
import csv, hashlib, json, os, re, subprocess, sys, unicodedata
from pathlib import Path

SRC = Path('/Users/maxvitvitskyy/SILENT_PLAYLISTS')
READY = SRC / 'READY'
HERE = Path(__file__).resolve().parent
OUT = HERE / 'covers'
SIZE = 240

def norm(s):
    s = unicodedata.normalize('NFC', s)
    return re.sub(r'\s+', ' ', s.lower()).strip()

def key(a, t):
    return norm(a) + '|' + norm(t)

# Рядки таблиці (та сама структура, що читає сторінка)
rows = []
with open(SRC / 'tracks.csv', encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        a, t = (r.get('Виконавець') or '').strip(), (r.get('Назва') or '').strip()
        if a and t:
            rows.append((a, t))

# Ключі, що їх сторінка бере з таблиці (з дублями #n, як у buildTracks)
seen, ids = {}, {}
for a, t in rows:
    k = key(a, t)
    if k in seen:
        seen[k] += 1
        k2 = k + '#' + str(seen[k])
    else:
        seen[k] = 1
        k2 = k
    ids.setdefault(k2, (a, t))

# Файли READY: «Виконавець - Назва.mp3»
files = sorted(p for p in READY.iterdir() if p.suffix.lower() == '.mp3')
by_name = {}
for p in files:
    stem = p.stem
    if ' - ' not in stem:
        continue
    a, t = stem.split(' - ', 1)
    by_name.setdefault(key(a, t), []).append(p)

OUT.mkdir(exist_ok=True)
mapping, missing, nocover = {}, [], []
for tid, (a, t) in ids.items():
    cands = by_name.get(key(a, t))
    if not cands:
        missing.append(tid)
        continue
    src = cands[0]
    fn = hashlib.sha1(tid.encode('utf-8')).hexdigest()[:12] + '.jpg'
    dst = OUT / fn
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-map', '0:v:0', '-frames:v', '1',
           '-vf', f'crop=min(iw\\,ih):min(iw\\,ih),scale={SIZE}:{SIZE}', '-q:v', '4', str(dst)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not dst.exists() or dst.stat().st_size == 0:
        nocover.append(tid)
        continue
    mapping[tid] = 'covers/' + fn

(HERE / 'covers' / 'map.json').write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding='utf-8')
print('рядків з ключем:', len(ids))
print('з обкладинкою:', len(mapping))
print('без файлу в READY:', len(missing))
for m in missing: print('  -', m)
print('без обкладинки:', len(nocover))
for m in nocover: print('  -', m)
print('файлів у READY без рядка:', len(files) - sum(1 for k in by_name if k in ids))

# Вписуємо мапу в сторінку між маркерами
html = (HERE / 'index.html').read_text(encoding='utf-8')
block = '/*COVERS:START*/const COVER_FILES=' + json.dumps(mapping, ensure_ascii=False) + ';/*COVERS:END*/'
new, n = re.subn(r'/\*COVERS:START\*/.*?/\*COVERS:END\*/', lambda _: block, html, flags=re.S)
assert n == 1, 'маркери COVERS не знайдено'
(HERE / 'index.html').write_text(new, encoding='utf-8')
print('мапу вписано в index.html')
