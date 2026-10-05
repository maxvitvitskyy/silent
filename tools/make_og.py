#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерує OG-зображення сторінки (1200×630) у стилі сайту за затвердженим зразком.

Запуск:  python3 tools/make_og.py corporate        (читає tools/og/corporate.json)

Макет затверджено власником 05.10.2026 (корпоративи): логотип сайту (знак із навушниками + слово SILENT. без плашки) зліва,
заголовок Unbounded капсом у два рядки, підзаголовок Manrope (кілька абзаців: масив
масивів рядків), лаймові пігулки-факти шрифтом Unbounded стовпчиком; праворуч три великі фото (одне високе + два), відступи 16px однакові
(зверху, знизу, справа й між фото). Фото беруться з images/<тека сторінки>/ без обрізання
людей: високе фото ~0.55 (вертикаль), два менші ~0.75. Рендерить справжній Chrome
(headless) із тими самими Google Fonts, що й сайт, тому потрібен інтернет і Google Chrome.

Для нової сторінки: скопіювати tools/og/corporate.json у tools/og/<slug>.json, змінити
заголовок, підзаголовок, пігулки (<b>…</b> = лаймове слово) і три фото.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = json.load(open(os.path.join(ROOT, 'tools', 'og', sys.argv[1] + '.json'), encoding='utf-8'))
    html = open(os.path.join(ROOT, 'tools', 'og', 'template.html'), encoding='utf-8').read()
    file_url = lambda p: 'file://' + os.path.join(ROOT, p)
    rep = {
        '{{MARK}}': file_url('images/silent-mark.webp'),
        '{{HEADING}}': ''.join('<span>%s</span>' % l for l in spec['heading']),
        '{{SUBTITLE}}': ''.join('<p>%s</p>' % '<br>'.join(par) for par in spec['subtitle']),
        '{{PILLS}}': ''.join('<span class="pill">%s</span>' % p for p in spec['pills']),
    }
    for key in ('big', 'top', 'bottom'):
        rep['{{%s}}' % key.upper()] = file_url(spec[key]['src'])
        rep['{{%s_POS}}' % key.upper()] = spec[key].get('pos', '50% 50%')
    for k, v in rep.items():
        html = html.replace(k, v)
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, 'og.html'); png = os.path.join(tmp, 'og.png')
        open(page, 'w', encoding='utf-8').write(html)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--allow-file-access-from-files', '--window-size=1200,630',
                        '--virtual-time-budget=8000', '--screenshot=' + png, 'file://' + page],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        out = os.path.join(ROOT, spec['out'])
        Image.open(png).convert('RGB').save(out, quality=86, optimize=True, progressive=True)
    print('%s: %d КБ' % (spec['out'], os.path.getsize(out) // 1024))

if __name__ == '__main__':
    main()
