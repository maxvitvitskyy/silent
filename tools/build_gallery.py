#!/usr/bin/env python3
"""Галерея: мозаїка у два ряди з чергуванням вертикаль → блок → вертикаль.

Ритм у стрічці: T, W/W, T, S/S, T, W/W, … — між кожними двома вертикалями
стоїть горизонтальний блок, тож ні вертикалі, ні горизонталі ніде не йдуть
підряд, і два однакові блоки теж не сусідять.

Геометрія (колонка 300, рядок 235, геп 14) дає три пропорції плиток:
  T (1 кол × 2 ряд) = 300 / 484 = 0.620
  W (2 кол × 1 ряд) = 614 / 235 = 2.613
  S (1 кол × 1 ряд) = 300 / 235 = 1.277
Кожен кадр ріжеться тут-таки рівно під свою пропорцію, з окремою точкою по
горизонталі й вертикалі, підібраною під те, що в кадрі головне. Браузеру
дорізати вже нічого — саме тому герої більше нікуди не виїжджають.
"""
import base64, io, json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAL = os.path.join(ROOT, 'images', 'gal')
OUT = HERE                      # сюди лягає tiles.html — вставити в index.html

omap = {int(k): v for k, v in json.load(open(f'{OUT}/orig_map.json')).items()}
omap.update({                     # кадри, які користувач доклав пізніше
    26: 'Згенероване зображення 1 (11).png',
    27: 'Зображення Codex 31 серп. 2026 р., 15_59_18.png',
    28: 'SILENT+DISCO+LIVERPOOL36.webp',
    29: '0c05a6e0e6ade80e3522765c14f394c7054bcc54.webp',
    30: 'original.avif',
    31: 'silentparty-girl.webp',
})

COL, ROW, GAP = 300, 235, 14
SHAPE = {
    'tall': (COL / (2 * ROW + GAP), 600, 968),
    'wide': ((2 * COL + GAP) / ROW, 1228, 470),
    'sq':   (COL / ROW,             600, 470),
}

# n: (форма, focal_x, focal_y, alt). focal 0.5 — центр; менше — тримаємо
# лівий бік / верх кадру, більше — правий / низ.
PLAN = {
    # ── вертикалі: композиція будується вгору, героя різати не можна ──
    6:  ('tall', 0.50, 0.50, 'Танці серед колон'),
    7:  ('tall', 0.50, 0.50, 'Йога-сет на світанку біля моря'),
    8:  ('tall', 0.50, 0.50, 'Кінопоказ просто неба'),
    9:  ('tall', 0.50, 0.50, 'Гості в залі музею'),
    11: ('tall', 0.50, 0.50, 'Навушник на столі'),
    12: ('tall', 0.52, 0.50, 'Перший танець молодят'),
    15: ('tall', 0.56, 0.50, 'Пара в обіймах серед гостей'),
    16: ('tall', 0.44, 0.50, 'Дві подруги сміються'),
    17: ('tall', 0.50, 0.50, 'Сет на заході сонця'),
    20: ('tall', 0.55, 0.38, 'Навушники для гостей на вході'),
    31: ('tall', 0.52, 0.42, 'Гостя озирається на танцполі'),
    # ── горизонталі: панорами й загальні плани, де людей багато ──
    1:  ('wide', 0.50, 0.50, 'Дівчина танцює серед вогнів'),
    3:  ('wide', 0.50, 0.42, 'Компанія танцює разом'),
    4:  ('wide', 0.50, 0.50, 'Дах із панорамою нічного міста'),
    5:  ('wide', 0.50, 0.50, 'Ряди навушників перед подією'),
    18: ('wide', 0.50, 0.40, 'Розмова в синьому світлі'),
    19: ('wide', 0.50, 0.50, 'Вечірка на даху над містом'),
    26: ('wide', 0.50, 0.46, 'Захід сонця над пляжним танцполом'),
    # Кадр майже увесь — порожнє небо над лазерами, а зала внизу вузькою смугою.
    # Тому єдиний у наборі, кому точка кадрування стоїть в самому низу: інакше
    # у смугу потрапляли самі промені, без людей і без сцени.
    28: ('wide', 0.50, 1.00, 'Лазери над залою в навушниках'),
    29: ('wide', 0.50, 0.46, 'Дискокуля над залою'),
    30: ('wide', 0.50, 0.44, 'Щільний танцпол у фіолетовому світлі'),
    # ── прямокутники: компактні кадри й деталі ──
    2:  ('sq', 0.50, 0.34, 'Руки вгору на танцполі'),
    10: ('sq', 0.50, 0.50, 'Навушник зблизька'),
    13: ('sq', 0.50, 0.50, 'Повний двір гостей'),
    14: ('sq', 0.50, 0.58, 'Сервірований стіл із навушниками'),
    21: ('sq', 0.50, 0.50, 'Ранкове тренування на вулиці'),
    22: ('sq', 0.50, 0.36, 'Гостя вибирає свій канал'),
    23: ('sq', 0.50, 0.45, 'Юрба перед сценою'),
    24: ('sq', 0.50, 0.50, 'Вечірка за склом, тиша назовні'),
    25: ('sq', 0.50, 0.55, 'Танці у дворі надвечір'),
    27: ('sq', 0.50, 0.55, 'Святковий стіл у рожевому світлі'),
}

# Порядок читання стрічки. Вертикаль, далі блок із двох кадрів один над одним,
# знову вертикаль — і так далі; блоки W/W і S/S чергуються між собою.
ORDER = [12, 4, 26, 7, 2, 14, 16, 28, 3, 9, 22, 13, 20, 29, 5, 6, 23, 24,
         15, 30, 18, 11, 21, 27, 8, 1, 19, 17, 10, 25, 31]

assert set(PLAN) == set(omap) == set(ORDER), 'плани й порядок мають збігатися'
assert len(ORDER) == 31 and len(set(ORDER)) == 31

def crop(im, ratio, fx, fy):
    w, h = im.size
    if w / h > ratio:                       # кадр ширший за плитку — ріжемо боки
        nw = round(h * ratio)
        x = max(0, min(w - nw, round((w - nw) * fx)))
        return im.crop((x, 0, x + nw, h))
    nh = round(w / ratio)                   # кадр вищий — ріжемо по висоті
    y = max(0, min(h - nh, round((h - nh) * fy)))
    return im.crop((0, y, w, y + nh))

def lqip(im):
    t = im.copy(); t.thumbnail((24, 24), Image.LANCZOS)
    b = io.BytesIO(); t.save(b, 'WEBP', quality=50, method=6)
    return base64.b64encode(b.getvalue()).decode()

for f in os.listdir(GAL):                   # прибрати попередній набір плиток
    if f[:2].isdigit() and f.endswith('.webp'):
        os.remove(os.path.join(GAL, f))

CLS = {'tall': 'g-tall', 'wide': 'g-wide', 'sq': 'g-sq'}
rows, kept = [], {}
for n in ORDER:
    shape, fx, fy, alt = PLAN[n]
    ratio, ow, oh = SHAPE[shape]
    im = Image.open(os.path.join(GAL, omap[n])).convert('RGB')
    c = crop(im, ratio, fx, fy)
    kept[n] = (c.width * c.height) / (im.width * im.height)
    c.resize((ow, oh), Image.LANCZOS).save(
        os.path.join(GAL, f'{n:02d}_{shape}.webp'), 'WEBP', quality=80, method=6)
    rows.append(
        f'        <figure class="gallery-item {CLS[shape]}">\n'
        f'          <img src="images/gal/{n:02d}_{shape}.webp"'
        f' style="--lqip:url(data:image/webp;base64,{lqip(c)})"'
        f' width="{ow}" height="{oh}" loading="lazy" decoding="async" alt="{alt}">\n'
        f'          <div class="gallery-scrim"></div>\n'
        f'        </figure>')

# ---- перевірка упаковки: два рядки, без дірок ----
SPAN = {'tall': (1, 2), 'wide': (2, 1), 'sq': (1, 1)}
fill, kinds = [0, 0], []
for n in ORDER:
    cw, ch = SPAN[PLAN[n][0]]
    kinds.append({'tall': 'V', 'wide': 'H', 'sq': 'S'}[PLAN[n][0]])
    if ch == 2:
        assert fill[0] == fill[1], f'дірка перед #{n}: {fill}'
        fill[0] += cw; fill[1] += cw
    else:
        r = 0 if fill[0] <= fill[1] else 1
        fill[r] += cw
assert fill[0] == fill[1], f'незакрита дірка в кінці: {fill}'

# ---- перевірка чергування блоків ----
blocks, i = [], 0
while i < len(kinds):
    if kinds[i] == 'V':
        blocks.append('V'); i += 1
    else:
        assert i + 1 < len(kinds) and kinds[i + 1] == kinds[i], f'непарний блок на {i}'
        blocks.append(kinds[i] * 2); i += 2
for a, b in zip(blocks, blocks[1:]):
    assert a != b, f'два однакові блоки поспіль: {a} {b}'

print('блоки:', ' '.join(blocks))
print('колонок %d, ширина копії ≈ %dpx' % (fill[0], fill[0] * COL + (fill[0] - 1) * GAP))
print('пропорції: T %.3f  W %.3f  S %.3f' % tuple(SHAPE[s][0] for s in ('tall', 'wide', 'sq')))
print('найсильніше обрізані:', ', '.join(
    f'#{n} лишилось {v*100:.0f}%' for n, v in sorted(kept.items(), key=lambda kv: kv[1])[:4]))
open(f'{OUT}/tiles.html', 'w').write('\n'.join(rows) + '\n')
tot = sum(os.path.getsize(os.path.join(GAL, f'{n:02d}_{PLAN[n][0]}.webp')) for n in PLAN)
print('плиток %d, вага %.1f МБ' % (len(ORDER), tot / 1e6))
