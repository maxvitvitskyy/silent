#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Оптимізує фото з inbox/<сторінка>/ у WebP для сайту.

Запуск:  python3 tools/optimize_images.py corporate [--max 1600] [--quality 82]

Що робить: бере зображення з inbox/<slug>/ (не зі вкладених тек, зокрема _done/),
виправляє поворот за EXIF, стискає по довшій стороні до --max, зберігає WebP без
метаданих у images/<тека сторінки>/, а оригінал переносить у inbox/<slug>/_done/.
Нічого не видаляє. Уже наявний файл з таким ім'ям НЕ перезаписує (додає суфікс -2, -3…).
"""
import argparse, os, re, shutil, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# slug сторінки → тека зображень на сайті (за замовчуванням images/<slug>/)
OUT_DIR = {'corporate': 'corp'}
EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.avif', '.tif', '.tiff')

# Українська → латиниця, щоб «Тест Фото» став test-foto, а не безіменним img.
UA = dict(zip('абвгґдеєжзиіїйклмнопрстуфхцчшщьюя', ['a','b','v','h','g','d','e','ye','zh','z','y','i','yi','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','yu','ya']))
UA['ё'] = 'yo'; UA['ы'] = 'y'; UA['э'] = 'e'; UA['ъ'] = ''

def slugify(name):
    name = ''.join(UA.get(c, c) for c in name.lower())
    s = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
    return s or 'img'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--max', type=int, default=1600)
    ap.add_argument('--quality', type=int, default=82)
    a = ap.parse_args()

    src = os.path.join(ROOT, 'inbox', a.slug)
    if not os.path.isdir(src):
        sys.exit('немає теки inbox/%s' % a.slug)
    out = os.path.join(ROOT, 'images', OUT_DIR.get(a.slug, a.slug))
    done = os.path.join(src, '_done')
    os.makedirs(out, exist_ok=True)

    try:
        import pillow_heif; pillow_heif.register_heif_opener()
    except Exception:
        pass

    files = sorted(f for f in os.listdir(src)
                   if os.path.isfile(os.path.join(src, f)) and f.lower().endswith(EXTS))
    if not files:
        print('inbox/%s порожня — нічого оптимізувати' % a.slug); return
    os.makedirs(done, exist_ok=True)
    total_in = total_out = 0
    for f in files:
        path = os.path.join(src, f)
        try:
            im = Image.open(path); im = ImageOps.exif_transpose(im)
        except Exception as e:
            print('ПРОПУЩЕНО %s: %s' % (f, e)); continue
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGBA' if 'A' in im.getbands() else 'RGB')
        w, h = im.size
        k = min(1.0, a.max / max(w, h))
        if k < 1:
            im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        base = slugify(os.path.splitext(f)[0]); name = base + '.webp'; n = 2
        while os.path.exists(os.path.join(out, name)):
            name = '%s-%d.webp' % (base, n); n += 1
        dst = os.path.join(out, name)
        im.save(dst, 'WEBP', quality=a.quality, method=6)
        sz_in, sz_out = os.path.getsize(path), os.path.getsize(dst)
        total_in += sz_in; total_out += sz_out
        shutil.move(path, os.path.join(done, f))
        print('%-32s %5dx%-5d  %6d КБ -> %-28s %4d КБ' % (f[:32], im.width, im.height, sz_in // 1024, name, sz_out // 1024))
    print('Разом: %d КБ -> %d КБ, файли в images/%s/' % (total_in // 1024, total_out // 1024, OUT_DIR.get(a.slug, a.slug)))

if __name__ == '__main__':
    main()
