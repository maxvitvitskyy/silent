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

def _reel_row(word, top, raw, questions=False):
    """Один розмитий рядок барабана. Формули взято з initReel() у site.js, щоб картка
    збігалась із віджетом у герої /experiences/ (слова) і /faq/ (питання): нахил рядка =
    raw*TILT/VIS градусів (вище центру проти годинникової, нижче за), зсув ліворуч по дузі
    -R*(1-cos), сусіди прозоріші й розмитіші до краю. raw — рядків від центру зі знаком.
    Питання лежать у пігулках (обводка + ледь помітна заливка), як на сторінці."""
    import math
    VIS, LINE = 4.5, 62
    RADIUS, TILT = (120, 16) if questions else (62, 22)
    a = abs(raw); t = min(a / VIS, 1.15)
    edge = max(0, 0.92 - 0.7 * t)
    fade = 1 + (0.92 - 0.7 / VIS - 1) * a if a < 1 else edge
    alpha = 0.6 * fade
    blur = LINE * (0.08 + 0.12 * t) * min(1, a)
    bow = -RADIUS * (1 - math.cos(raw / VIS * math.pi / 2))
    xf = 'translateX(%.1fpx) rotate(%.2fdeg)' % (bow, raw * TILT / VIS)
    if questions:
        return ('<div class="row q" style="top:%dpx"><span class="w" style="opacity:%.3f;filter:blur(%.2fpx);transform:%s">%s</span></div>'
                % (top, min(1, 0.4 + alpha), blur * 0.2, xf, word))
    sh = max(0, min(1, (blur - 0.3) / 2))
    return ('<div class="row" style="top:%dpx"><span class="w" style="color:rgba(255,255,255,%.3f);'
            'text-shadow:0 0 %.2fpx rgba(255,255,255,%.3f);transform:%s">%s</span></div>'
            % (top, alpha * (1 - sh), blur, min(1, alpha * (0.4 + 1.1 * sh)), xf, word))


def _cloud(reel):
    """Хмара питань, як у герої /faq/ (initQuestionCloud у site.js, CSS .exp-cloud): картка
    ЦІЛКОМ заповнена рядками пігулок, уся хмара нахилена на -7°, краї розчиняє горизонтальна
    маска. Середній рядок різкий, вищі й нижчі тьмяніші й розмитіші; питання біля центру
    картки в середньому рядку підсвічене лаймом. Зсув рядків і центрування робить скрипт у
    самій сторінці (потрібні реальні ширини шрифту), тому Chrome має дочекатись fonts.ready."""
    qs, n, count = reel['questions'], len(reel['questions']), 9
    mid = (count - 1) / 2
    rows = ''
    for r in range(count):
        d = abs(r - mid)
        a = 1 if d == 0 else max(0.2, 0.62 - 0.14 * (d - 1))
        blur = 0 if d == 0 else min(3.6, 0.9 + 0.9 * d)
        sh = max(0, min(1, (blur - 0.3) / 2))
        shift = (r * 4 + (r % 2) * 2) % n
        spans = ''.join('<span>%s</span>' % qs[(k + shift) % n] for _ in range(2) for k in range(n))
        style = ('--c:rgba(255,255,255,%.3f);--ts:%s;--bd:rgba(255,255,255,%.3f)'
                 % (a * (1 - sh), ('0 0 %.2fpx rgba(255,255,255,%.3f)' % (blur, min(1, a * (0.4 + 1.1 * sh)))) if blur else 'none', 0.14 * a))
        rows += '<div class="crow%s" data-r="%d" style="%s">%s</div>' % (' mid' if d == 0 else '', r, style, spans)
    js = """<script>document.fonts.ready.then(function(){
var st=document.querySelector('.stage'),cx=st.offsetWidth/2,C=%s;
[].forEach.call(st.querySelectorAll('.crow'),function(row){
 var r=+row.dataset.r,sp=[].slice.call(row.children),x=-((r*211+90)%%900);
 if(row.classList.contains('mid')){var t=sp.filter(function(s){return s.textContent===C})[0];
  x=-(t.offsetLeft+t.offsetWidth/2-cx);t.classList.add('hot');}
 row.style.transform='translateX('+x+'px)';});});</script>""" % _json_s(reel['center'])
    return '<div class="cloudwin"><div class="stage">%s</div></div>%s' % (rows, js)


def _json_s(v):
    return json.dumps(v, ensure_ascii=False)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    spec = json.load(open(os.path.join(ROOT, 'tools', 'og', sys.argv[1] + '.json'), encoding='utf-8'))
    html = open(os.path.join(ROOT, 'tools', 'og', spec.get('template', 'template.html')), encoding='utf-8').read()
    file_url = lambda p: 'file://' + os.path.join(ROOT, p)
    rep = {
        '{{MARK}}': file_url('images/silent-mark.webp'),
        '{{HEADING}}': ''.join('<span>%s</span>' % l for l in spec['heading']),
        '{{SUBTITLE}}': ''.join('<p>%s</p>' % '<br>'.join(par) for par in spec.get('subtitle', [])),
        '{{BG}}': file_url(spec['bg']['src']) if 'bg' in spec else '',
        '{{BG_POS}}': spec['bg'].get('pos', '50% 50%') if 'bg' in spec else '',
        '{{PILLS}}': ''.join('<span class="pill%s">%s</span>' % (' cta' if p.startswith('!') else '', p.lstrip('!')) for p in spec['pills']),
    }
    rep['{{EXTRA_CSS}}'] = spec.get('css', '')
    if 'reel' in spec:
        # Скляна «карусель» як у герої каталогу: по центру чіткий рядок «SILENT. <слово>»,
        # вище й нижче слова розмиваються й повертаються дедалі більше (як колода карток).
        above, below = spec['reel'].get('above', []), spec['reel'].get('below', [])
        if spec['reel'].get('mode') == 'cloud':
            rep['{{REEL}}'] = _cloud(spec['reel'])
            above = below = []
        questions = spec['reel'].get('mode') == 'questions'
        pitch, mid = (58, 299 - 29) if questions else (62, 299 - 31)
        rows = ''
        for k, w in enumerate(reversed(above), 1):
            rows += _reel_row(w, mid - k * pitch, -k, questions)
        if questions:
            rows += '<div class="row q c" style="top:%dpx"><span class="w">%s</span></div>' % (mid, spec['reel']['center'])
        else:
            rows += ('<div class="row c" style="top:%dpx"><span class="lead">SILENT<b>.</b></span><span class="w">%s</span></div>'
                     % (mid, spec['reel']['center']))
        for k, w in enumerate(below, 1):
            rows += _reel_row(w, mid + k * pitch, k, questions)
        if spec['reel'].get('mode') != 'cloud':
            rep['{{REEL}}'] = rows
    for key in ('big', 'top', 'bottom'):
        if key not in spec:
            continue
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
