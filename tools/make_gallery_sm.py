#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Малі копії для стрічки-колажу у геро сторінок досвідів (.gallery-columns).

Навіщо: плитки колажу показуються шириною ~250–450 px, а в розмітці стояли
повнорозмірні знімки (1122×1402, 130–280 КБ кожен, по 6 на сторінку). Вони
вантажаться одразу (геро над згином), ділять смугу зі стилями й скриптами,
від яких залежить поява тексту, і саме вони тягли LCP сторінок досвідів
(Lighthouse mobile: charity LCP 8,8 с, 3 МБ картинок). Тут для кожного знімка
з колажу робиться копія `<ім'я>-sm.webp` шириною 640 px (запас під retina)
і src у розмітці переписується на неї, а width/height — під нові пропорції.

Ідемпотентно: уже переписані src (…-sm.webp) пропускаються, наявні копії не
перегенеруються. Оригінали не чіпаємо, їх використовують інші блоки сторінок.
Викликається з tools/build_en.py першим кроком збірки; руками: python3 tools/make_gallery_sm.py
"""
import glob, io, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SM_W = 640
BLOCK = re.compile(r'(<div class="gallery-columns"[^>]*>)(.*?)(</div>\s*</div>\s*</div>)', re.S)
IMG = re.compile(r'<img\b([^>]*?)\bsrc="([^"]+\.webp)"([^>]*)>')


def make_sm(page_dir, src):
    src_path = os.path.normpath(os.path.join(page_dir, src))
    if src_path.endswith('-sm.webp') or not os.path.exists(src_path):
        return None
    sm_path = src_path[:-5] + '-sm.webp'
    with Image.open(src_path) as im:
        w, h = im.size
        if w <= SM_W + 80:       # уже малий: копія нічого не дасть
            return None
        nh = round(h * SM_W / w)
        if not os.path.exists(sm_path):
            im.convert('RGB').resize((SM_W, nh), Image.LANCZOS).save(sm_path, 'WEBP', quality=78, method=6)
    return os.path.basename(sm_path), SM_W, nh


def run():
    pages = [p for p in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)
             if os.sep + 'en' + os.sep not in p[len(ROOT):] and 'inbox' not in p and 'tools' not in p]
    changed = 0
    for page in sorted(pages):
        text = io.open(page, encoding='utf-8').read()
        if 'gallery-columns' not in text:
            continue
        page_dir = os.path.dirname(page)

        def fix_block(m):
            def fix_img(im):
                pre, src, post = im.group(1), im.group(2), im.group(3)
                r = make_sm(page_dir, src)
                if not r:
                    return im.group(0)
                name, w, h = r
                new_src = src[:-5] + '-sm.webp'
                pre = re.sub(r'\bwidth="\d+"', 'width="%d"' % w, pre)
                pre = re.sub(r'\bheight="\d+"', 'height="%d"' % h, pre)
                return '<img%ssrc="%s"%s>' % (pre, new_src, post)
            return m.group(1) + IMG.sub(fix_img, m.group(2)) + m.group(3)

        new = BLOCK.sub(fix_block, text)
        if new != text:
            io.open(page, 'w', encoding='utf-8').write(new)
            changed += 1
    return changed


if __name__ == '__main__':
    print('make_gallery_sm: змінено сторінок', run())
