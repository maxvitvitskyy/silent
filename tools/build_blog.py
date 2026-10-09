#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Збирає сторінку блогу /blog/ із blog_src/posts.json.

Шапка, меню, підвал, форма й скрипти беруться з experiences/index.html при кожній збірці,
тож блог не розходиться з рештою сайту (меню в нас продубльоване по сторінках, тут його
копіювати вручну не треба).

Статуси матеріалів у posts.json:
  soon      заглушка: картка без посилання, мітка «Скоро», сторінки статті нема;
  draft     сторінка статті /blog/<slug>/ збирається (з blog_src/<slug>.json) з noindex, але в
            списку лишається заглушкою без посилання, у sitemap не входить: так шаблон можна
            дивитись наживо, не публікуючи його;
  published стаття готова: картка веде на сторінку, noindex зникає (у sitemap додаємо руками).
Шаблон статті (затверджений 06.10.2026, варіант «Лайм-акцент і таймлайн»): .art-* у assets/site.css.

Поки в блозі немає жодної опублікованої статті, сторінка має noindex і не потрапляє в sitemap.
"""
import html, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PAGE = os.path.join(ROOT, 'experiences', 'index.html')
POSTS = os.path.join(ROOT, 'blog_src', 'posts.json')
OUT_DIR = os.path.join(ROOT, 'blog')
SITE = 'https://silent.org.ua'

TITLE = 'Блог SILENT: ідеї та поради для тихих вечірок'
DESC = 'Як провести свято без шуму, чим здивувати гостей і де silent disco рятує вечір: весілля, корпоративи, дні народження.'


def esc(s):
    return html.escape(s, quote=True)


_TINT_CACHE = {}


def tint(image_url):
    """Основний колір фото для легкого підсвічування картки: середній по насичених, не темних пікселях,
    ще трохи підсилений. Повертає 'r,g,b' для CSS-змінної --tint (порожньо, якщо фото нема або нема Pillow)."""
    if image_url in _TINT_CACHE:
        return _TINT_CACHE[image_url]
    out = ''
    try:
        import colorsys
        from PIL import Image
        im = Image.open(os.path.join(ROOT, image_url.lstrip('/'))).convert('RGB').resize((48, 48))
        acc = [0.0, 0.0, 0.0]
        wsum = 0.0
        allp = [0.0, 0.0, 0.0]
        for r, g, b in im.getdata():
            h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            allp[0] += r; allp[1] += g; allp[2] += b
            w = sat * v if (sat > 0.28 and v > 0.28) else 0
            if w:
                acc[0] += r * w; acc[1] += g * w; acc[2] += b * w; wsum += w
        n = 48 * 48
        base = [c / wsum for c in acc] if wsum else [c / n for c in allp]
        h, sat, v = colorsys.rgb_to_hsv(*[c / 255 for c in base])
        sat = max(sat, 0.55)
        v = max(v, 0.78)
        out = ','.join(str(round(c * 255)) for c in colorsys.hsv_to_rgb(h, sat, v))
    except Exception:
        out = ''
    _TINT_CACHE[image_url] = out
    return out


def ttl(p):
    """Назва статті в списках блогу: для опублікованої це посилання на статтю (клікабельний заголовок), для заглушки просто текст."""
    if p['status'] != 'published':
        return esc(p['title'])
    return '<a class="blog-title-link" href="/blog/%s/">%s</a>' % (p['slug'], esc(p['title']))


def card(p, cats):
    """Картка в загальній сітці. Заглушка: <article> без посилання."""
    cat = cats[p['category']]
    media = ('<div class="uc-media"><img src="%s" alt="%s" loading="lazy" decoding="async" width="768" height="432"></div>'
             % (esc(p['image']), esc(p['alt'])))
    if p['status'] != 'published':
        foot = '<span class="blog-soon">Скоро</span>'
        head, tail = '', ''
    else:
        foot = '<a class="uc-order" href="/blog/%s/">Читати</a>' % p['slug']
        head, tail = '', ''
    tn = tint(p['image'])
    style = ' style="--tint:%s"' % tn if tn else ''
    return ('        <article class="uc-card blog-card%s" data-cat="%s"%s>\n          %s\n'
            '          <div class="uc-body">\n            <span class="blog-cat">%s</span>\n'
            '            <h3>%s</h3>\n            <p>%s</p>\n            %s\n          </div>\n        </article>\n'
            % (' is-soon' if p['status'] != 'published' else '', p['category'], style, media, esc(cat),
               ttl(p), esc(p['excerpt']), foot))


# ---- Mega-меню «Блог» у шапці (нове 08.10.2026) ----
# Три частини: «Вибір редакції» (велика фото-картка), «Свіже» (список останніх) і «Добірка» (чотири картки
# з обкладинками) + кнопка «Усі статті». Генерується з posts.json і вставляється між маркерами
# BLOG-MEGA:START/END у шапку кожної української сторінки (меню в нас продубльоване по файлах). В англійську
# версію не потрапляє: блог поки лише українською (build_en.py вирізає цей блок перед перекладом).
MEGA_PAGES = ['index.html', 'privacy/index.html', 'experiences/index.html', 'experiences/corporate/index.html',
              'experiences/wedding/index.html', 'experiences/birthday/index.html', 'experiences/silent-disco/index.html', 'faq/index.html']
MEGA_START = '<!-- BLOG-MEGA:START (генерує tools/build_blog.py, руками не правити) -->'
MEGA_END = '<!-- BLOG-MEGA:END -->'
_SV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
MEGA_ICONS = {
    'new': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'pick': '<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>',
    'wedding': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    'corporate': '<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>',
    'quiet': '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    'birthday': '<rect x="3.5" y="9" width="17" height="11" rx="1.5"/><path d="M12 9v11M3.5 13h17"/><path d="M12 9c-2.5 0-4-1-4-2.5S9.5 3.5 12 9zm0 0c2.5 0 4-1 4-2.5S14.5 3.5 12 9z"/>',
    'price': '<path d="M20 12.5 12.5 20a1.5 1.5 0 0 1-2.12 0L3.5 13.1V4.5h8.6l7.9 7.9a1.5 1.5 0 0 1 0 2.1z"/><circle cx="8" cy="9" r="1.2"/>',
    'format': '<path d="M4 13v-1a8 8 0 0 1 16 0v1"/><rect x="2.5" y="13" width="4" height="6" rx="1.5"/><rect x="17.5" y="13" width="4" height="6" rx="1.5"/>',
}
_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'


def ordered_posts(posts):
    """Порядок матеріалів для сторінки блогу, «Свіже», «Добірки» й mega-меню: спершу готові статті від найновішої
    (за date_iso зі статті blog_src/<slug>.json; за однакової дати новіший той, що нижче в posts.json: нові статті дописуємо в кінець), потім заглушки
    й чернетки в порядку файла. Нову статтю достатньо додати в posts.json зі статусом published і створити
    blog_src/<slug>.json: вона сама стане першою у «Свіже» й у списку, а найстаріші випадуть із кількох слотів."""
    def day(p):
        f = os.path.join(ROOT, 'blog_src', p['slug'] + '.json')
        if p['status'] != 'published' or not os.path.exists(f):
            return 0
        try:
            return int(json.load(io.open(f, encoding='utf-8')).get('date_iso', '0').replace('-', ''))
        except Exception:
            return 0
    idx = {id(p): i for i, p in enumerate(posts)}
    return sorted(posts, key=lambda p: (0 if p['status'] == 'published' else 1, -day(p), -idx[id(p)] if p['status'] == 'published' else idx[id(p)]))


def blog_mega_html(data):
    cats = {c['id']: c['name'] for c in data['categories']}
    posts = ordered_posts(data['posts'])
    feat = next((p for p in posts if p.get('featured')), posts[0])
    rest = [p for p in posts if p is not feat]
    fresh = rest[:4]
    # «Добірка»: спершу готові статті (щоб було що відкрити), далі заглушки з решти списку
    older = [p for p in rest if p['status'] == 'published' and p not in fresh]
    stubs = [p for p in rest if p['status'] != 'published' and p not in fresh]
    pick = (older + stubs + [p for p in rest if p not in older + stubs])[:4]
    ic = lambda k: '<span class="nav-mega-icon" aria-hidden="true">%s</span>' % (_SV % MEGA_ICONS[k])
    live = lambda p: p['status'] == 'published'
    vis = ('<div class="nav-mega-visual-text"><span class="nav-mega-badge">Вибір редакції</span>'
           '<div class="nav-mega-title"><span class="t-lead">%s</span><span class="t-sub">%s</span></div></div>'
           % (esc(feat['title']), esc(feat.get('menu_sub', feat['excerpt']))))
    if live(feat):
        col1 = ('<a href="/blog/%s/" class="nav-mega-visual">\n                <img src="%s" alt="" loading="lazy">\n                %s\n'
                '                <span class="nav-mega-cta">Читати статтю%s</span>\n              </a>' % (feat['slug'], esc(feat['image']), vis, _ARROW))
    else:
        col1 = ('<div class="nav-mega-visual is-soon">\n                <img src="%s" alt="" loading="lazy">\n                %s\n'
                '                <span class="nav-mega-cta nav-mega-soon">Скоро</span>\n              </div>' % (esc(feat['image']), vis))

    def q(p):
        cat = esc(cats[p['category']])
        if live(p):
            return ('<a href="/blog/%s/" class="nav-mega-q"><span class="nav-blog-cat">%s</span><span class="nav-blog-t">%s</span></a>'
                    % (p['slug'], cat, esc(p['title'])))
        return ('<span class="nav-mega-q is-soon"><span class="nav-blog-cat">%s<em>Скоро</em></span><span class="nav-blog-t">%s</span></span>'
                % (cat, esc(p['title'])))
    col2 = ('<div class="nav-mega-card">\n                <div class="nav-mega-cat-head">%s<a href="/blog/" class="nav-mega-cat">Свіже</a></div>\n'
            '                <div class="nav-mega-qs">\n                  %s\n                </div>\n              </div>'
            % (ic('new'), '\n                  '.join(q(p) for p in fresh)))

    def mini(p):
        tag = ('a href="/blog/%s/"' % p['slug']) if live(p) else 'span'
        end = 'a' if live(p) else 'span'
        return ('<%s class="nav-blog-card%s"><span class="nav-blog-thumb"><img src="%s" alt="" loading="lazy">%s</span>'
                '<span class="nav-blog-cat">%s</span><span class="nav-blog-t">%s</span></%s>'
                % (tag, '' if live(p) else ' is-soon', esc(p['image']), '' if live(p) else '<em>Скоро</em>',
                   esc(cats[p['category']]), esc(p['title']), end))
    col3 = ('<div class="nav-mega-card">\n                <div class="nav-mega-cat-head">%s<a href="/blog/#topics" class="nav-mega-cat">Добірка</a></div>\n'
            '                <div class="nav-blog-cards">\n                  %s\n                </div>\n'
            '                <a href="/blog/" class="nav-mega-all">Усі статті%s</a>\n              </div>'
            % (ic('pick'), '\n                  '.join(mini(p) for p in pick), _ARROW))
    # Пункти для мобільного меню (JS читає .nav-mega-topics; на десктопі блок прихований). Не теми (вони дублюють
    # «Тихі враження» й «Питання»), а те, що є лише в блозі: вибір редакції й найновіша стаття, підпис = назва статті.
    mob = []
    if live(feat):
        mob.append(('pick', 'Вибір редакції', feat))
    newest = next((p for p in posts if live(p) and p is not feat), None)
    if newest:
        mob.append(('new', 'Найновіше', newest))
    # «Найчитаніше»: лише за ручною позначкою "popular": true у posts.json (дані про читання беруться з GA4 власником);
    # без позначки пункту нема, щоб не називати найчитанішою статтю без підстав.
    top = next((p for p in posts if p.get('popular') and live(p)), None)
    if top:
        mob.append(('format', 'Найчитаніше', top))
    topics = ''.join('<div class="nav-mega-cat-head">%s<a href="/blog/%s/" class="nav-mega-cat" data-sub="%s">%s</a></div>'
                     % (ic(k), p['slug'], esc(p['title']), lab) for k, lab, p in mob)
    return ('    <div class="nav-item-mega nav-item-mega--blog">\n'
            '      <a href="/blog/" class="nav-mega-trigger">Блог</a>\n'
            '      <div class="nav-mega-panel">\n        <div class="nav-mega-grid">\n'
            '            <div class="nav-mega-col">\n              %s\n            </div>\n'
            '            <div class="nav-mega-col">\n              %s\n            </div>\n'
            '            <div class="nav-mega-col">\n              %s\n            </div>\n'
            '        </div>\n        <div class="nav-mega-topics" hidden>%s</div>\n      </div>\n    </div>' % (col1, col2, col3, topics))


def inject_blog_mega(data):
    html_ = blog_mega_html(data)
    for rel in MEGA_PAGES:
        path = os.path.join(ROOT, rel)
        s = io.open(path, encoding='utf-8').read()
        a, b = s.find(MEGA_START), s.find(MEGA_END)
        if a < 0 or b < 0:
            sys.exit('blog: у %s немає маркерів BLOG-MEGA' % rel)
        new = s[:a] + MEGA_START + '\n' + html_ + '\n    ' + s[b:]
        if new != s:
            io.open(path, 'w', encoding='utf-8').write(new)


def build(preview=False):
    data = json.load(io.open(POSTS, encoding='utf-8'))
    cats = {c['id']: c['name'] for c in data['categories']}
    posts = ordered_posts(data['posts'])
    for p in posts:
        if p['category'] not in cats:
            sys.exit('blog: невідома тема %r у %s' % (p['category'], p['slug']))
        if p['status'] not in ('soon', 'draft', 'published'):
            sys.exit('blog: невідомий статус %r у %s' % (p['status'], p['slug']))
        if p['status'] in ('draft', 'published') and not os.path.exists(os.path.join(ROOT, 'blog_src', p['slug'] + '.json')):
            sys.exit('blog: немає blog_src/%s.json для статті зі статусом %s' % (p['slug'], p['status']))
    published = [p for p in posts if p['status'] == 'published']
    inject_blog_mega(data)   # шапка всіх сторінок, зокрема experiences/index.html, з якої беремо меню для блогу

    src = io.open(SRC_PAGE, encoding='utf-8').read()
    pre = src[:src.index('<title>')]
    js0 = src.index('<script>\n(function(){\n  var r = document.documentElement;')
    css_end = src.index('\n', src.index('<link rel="stylesheet" href="../assets/site.css')) + 1
    head_assets = src[js0:css_end]
    body0 = src.index('<body id="top"')
    main0 = src.index('<main id="main"')
    nav_block = src[body0:main0]
    form_block = src[src.index('<section class="form-section" id="book">'):src.index('</main>')]
    tail = src[src.index('</main>'):]
    tail_flip = tail   # для /blog/: Flip потрібен фільтру тем (та сама анімація, що в каталозі); у статтях він не потрібен
    tail = re.sub(r'<!-- Flip[^\n]*\n(?:[^\n]*\n)??<script src="\.\./assets/vendor/Flip\.min\.js[^"]*"></script>\n', '', tail)
    tail = re.sub(r'<script src="\.\./assets/vendor/Flip\.min\.js[^"]*"></script>\n', '', tail)
    for blk in (nav_block, tail):
        pass
    sw = '<a href="/en/experiences/" hreflang="en" lang="en">EN</a>'
    nav_block = nav_block.replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')
    tail = tail.replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')
    tail_flip = tail_flip.replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')

    shared = dict(pre=pre, head_assets=head_assets, nav_block=nav_block, form_block=form_block, tail=tail)
    url = SITE + '/blog/'
    robots = '' if published else '<meta name="robots" content="noindex, follow">\n'
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Blog', '@id': url + '#webpage', 'url': url, 'name': TITLE, 'description': DESC,
             'inLanguage': 'uk-UA', 'isPartOf': {'@id': SITE + '/#website'}, 'publisher': {'@id': SITE + '/#organization'},
             'breadcrumb': {'@id': url + '#breadcrumb'}},
            {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Головна', 'item': SITE + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Блог', 'item': url}]},
        ],
    }
    head = (pre + '<title>%s</title>\n<meta name="description" content="%s">\n%s'
            '<meta name="theme-color" content="#0a0a0b">\n'
            '<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
            '<link rel="icon" type="image/png" href="/favicon-48x48.png" sizes="48x48">\n'
            '<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">\n'
            '<meta property="og:type" content="website">\n<meta property="og:site_name" content="SILENT">\n'
            '<meta property="og:locale" content="uk_UA">\n<meta property="og:title" content="%s">\n'
            '<meta property="og:description" content="%s">\n<meta property="og:url" content="%s">\n'
            '<meta property="og:image" content="%s/images/blog/og-blog.jpg">\n'
            '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            '<link rel="canonical" href="%s">\n'
            % (esc(TITLE), esc(DESC), robots, esc(TITLE), esc(DESC), url, SITE, url)
            + head_assets
            + '<script type="application/ld+json">\n%s\n</script>\n</head>\n'
            % json.dumps(ld, ensure_ascii=False, indent=2))

    feat = next((p for p in posts if p.get('featured')), posts[0])
    latest = [p for p in posts if p is not feat][:4]
    counts = {}
    for p in posts:
        counts[p['category']] = counts.get(p['category'], 0) + 1

    def meta(p):
        if p['status'] != 'published':
            return '<span class="blog-soon">Скоро</span>'
        return '<a class="blog-read" href="/blog/%s/">Читати</a>' % p['slug']

    # Картка «Вибір редакції» повторює плашку з mega-меню: бейдж, заголовок і підзаголовок угорі, лаймова кнопка на всю ширину внизу.
    arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    cta = ('<a class="blog-read blog-hero-cta" href="/blog/%s/">Читати статтю%s</a>' % (feat['slug'], arrow)) if feat['status'] == 'published' \
        else '<span class="blog-hero-cta is-soon">Скоро</span>'
    hero = ('    <article class="blog-hero-card%s">\n'
            '      <img src="%s" alt="%s" width="768" height="432">\n'
            '      <div class="blog-hero-shade" aria-hidden="true"></div>\n'
            '      <div class="blog-hero-text">\n'
            '        <span class="blog-badge">Вибір редакції</span>\n'
            '        <h2>%s</h2>\n        <p>%s</p>\n      </div>\n      %s\n    </article>\n'
            % (' is-soon' if feat['status'] != 'published' else '', esc(feat['image']), esc(feat['alt']),
               ttl(feat), esc(feat['excerpt']), cta))
    items = ''.join(
        '        <li class="blog-latest-item%s">\n          <span class="blog-num" aria-hidden="true">%02d</span>\n'
        '          <div>\n            <span class="blog-cat">%s</span>\n            <h3>%s</h3>\n            %s\n          </div>\n        </li>\n'
        % (' is-soon' if p['status'] != 'published' else '', i + 1, esc(cats[p['category']]), ttl(p), meta(p))
        for i, p in enumerate(latest))
    latest_html = ('    <aside class="blog-latest glass-panel" aria-labelledby="blogLatestTitle">\n'
                   '      <h2 id="blogLatestTitle" class="blog-latest-title">Свіже</h2>\n      <ol class="blog-latest-list">\n%s      </ol>\n    </aside>\n' % items)
    chips = ('      <button type="button" class="blog-chip is-on" data-cat="all" aria-pressed="true">Усі <span>%d</span></button>\n' % len(posts)
             + ''.join('      <button type="button" class="blog-chip" data-cat="%s" aria-pressed="false">%s <span>%d</span></button>\n'
                       % (c['id'], esc(c['name']), counts.get(c['id'], 0)) for c in data['categories'] if counts.get(c['id'])))
    cards = ''.join(card(p, cats) for p in posts)

    main = ('<main id="main" tabindex="-1">\n\n<section class="blog-head">\n'
            '  <!-- Той самий контейнер, що в шапці /experiences/: скрипт монтує в .uc-aurora шлейф за курсором, .aurora-liquid дає градієнт. -->\n'
            '  <div class="uc-aurora" aria-hidden="true">\n    <div class="aurora-liquid"></div>\n  </div>\n  <div class="wrap">\n'
            '    <p class="exp-crumb"><a href="/">Головна</a> <span aria-hidden="true">&middot;</span> <span class="crumb-now">Блог</span></p>\n'
            '    <div class="blog-head-row">\n'
            '      <h1 class="blog-title">Блог SILENT</h1>\n'
            '      <p class="blog-lead">Як провести свято без шуму, чим здивувати гостей і де silent disco рятує вечір.</p>\n'
            '    </div>\n'
            '  </div>\n</section>\n\n'
            '<section class="blog-top">\n  <div class="wrap blog-top-grid">\n%s%s  </div>\n</section>\n\n'
            '<section class="blog-all" id="topics">\n  <div class="wrap">\n'
            '    <div class="blog-bar">\n      <h2 class="blog-bar-title">За темами</h2>\n'
            '      <div class="blog-filter" role="group" aria-label="Теми статей">\n%s      </div>\n    </div>\n'
            '    <div class="blog-grid">\n%s    </div>\n  </div>\n</section>\n\n'
            '<section class="block exp-close">\n  <div class="wrap">\n    <div class="band band-bare reveal">\n'
            '      <h2>Плануєте захід?</h2>\n      <p>Залиште заявку: перевіримо дату й порахуємо вартість для вашої події.</p>\n'
            '    </div>\n  </div>\n</section>\n\n%s'
            % (hero, latest_html, chips, cards, form_block))
    out = head + nav_block + main + tail_flip
    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8').write(out)
    print('blog/index.html зібрано: %d матеріалів (%d опубліковано, решта заглушки)' % (len(posts), len(published)))
    for p in posts:
        if p['status'] in ('draft', 'published'):
            build_article(p, data, cats, posts, shared, card)


def inline(text):
    """Текст абзацу: екранування + посилання у вигляді [[/шлях/|підпис]]."""
    out = esc(text)
    def link(m):
        href = m.group(1)
        ext = ' rel="noopener" target="_blank"' if href.startswith('http') else ''
        return '<a href="%s"%s>%s</a>' % (href, ext, m.group(2))
    return re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', link, out)


ART_ICONS = {
    'calm': '<path d="M8 3h8l-1 7a3 3 0 0 1-6 0z"/><path d="M12 13v8M8 21h8"/>',
    'active': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    'mixed': '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15.5 14.4c2.8.2 5.5 2 5.5 5.6"/>',
    'unusual': '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 17v4M17 19h4"/>',
    'person': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>',
    'star': '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    'gift': '<rect x="3.5" y="9" width="17" height="11" rx="1.5"/><path d="M12 9v11M3.5 13h17"/><path d="M12 9c-2.5 0-4-1-4-2.5S9.5 3.5 12 9zm0 0c2.5 0 4-1 4-2.5S14.5 3.5 12 9z"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'film': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 9h18M3 15h18M8 5v14M16 5v14"/>',
    'versus': '<path d="M4 8h12M12 4l4 4-4 4"/><path d="M20 16H8M12 12l-4 4 4 4"/>',
}


def article_blocks(blocks):
    """Тіло статті з блоків article.json (схема власника від 06.10.2026):
    text  заголовок + текст у дві рівні колонки (cols: [ліва, права] зливаються в один потік, що CSS ділить на дві вирівняні колонки; або cards: [{t,d}] для карток із нумерацією);
    pair  фото ліворуч і яскрава лаймова плашка з головною думкою праворуч, однакової висоти."""
    out = []
    for b in blocks:
        t = b['type']
        if t == 'text':
            # Заголовок розділу окремим рядком зверху (не ширший за одну колонку), під ним дві явні рівні колонки,
            # які починаються на одній лінії; текст розкладено вручну так, щоб вони були рівні за висотою.
            if b.get('cards'):
                # Кроки: окремі картки в дві колонки (без ефекту стопки), нумерація лічильником у CSS.
                # Вигляд карток можна міняти по блоках, не чіпаючи дизайн-систему: layout "cols" = вертикальні картки в ряд,
                # marks "icons" = тематична іконка (поле ic у картці, ключі в ART_ICONS) замість номера. Без цього: номери, дві колонки.
                use_icons = b.get('marks') == 'icons'
                def mark(x):
                    if use_icons and x.get('ic') in ART_ICONS:
                        return '<span class="art-ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>' % ART_ICONS[x['ic']]
                    return '<i class="art-n" aria-hidden="true"></i>'
                items = ''.join('<li>%s<b>%s</b><span>%s</span></li>' % (mark(x), esc(x['t']), inline(x['d'])) for x in b['cards'])
                lead = '<p class="art-cards-lead">%s</p>' % inline(b['lead']) if b.get('lead') else ''
                out.append('<section class="art-blk"><div class="art-cols"><h2>%s</h2>%s<ol class="art-cards%s">%s</ol></div></section>'
                           % (esc(b['title']), lead, ' is-cols' if b.get('layout') == 'cols' else '', items))
                continue
            # Звичайний текстовий блок: ОДИН потік у дві CSS-колонки з вирівнюванням, заголовок першим елементом потоку (у лівій колонці),
            # (column-fill: balance): колонки починаються на одному рівні, закінчуються на одному, а абзац сам
            # переходить між ними, де треба. Тому ручного розкладання по колонках більше нема: left/right просто зливаються.
            items = [it for col in b['cols'] for it in col]
            html = ''
            for it in items:
                if 'p' in it:
                    html += '<p>%s</p>' % inline(it['p'])
                elif 'steps' in it:
                    html += '<ol class="art-steps" style="counter-reset: st %d">%s</ol>' % (it.get('start', 1) - 1, ''.join(
                        '<li><b>%s</b><span>%s</span></li>' % (esc(x['t']), inline(x['d'])) for x in it['steps']))
                else:
                    sys.exit('blog: невідомий елемент колонки %r' % it)
            out.append('<section class="art-blk"><div class="art-flow"><h2>%s</h2>%s</div></section>' % (esc(b['title']), html))
        elif t == 'pair':
            im = b['image']
            out.append('<div class="art-pair"><figure class="art-pair-img"><img src="%s" alt="%s" loading="lazy" decoding="async" width="1200" height="900"></figure>'
                       '<blockquote class="art-key"><div class="band-aurora" aria-hidden="true"><div class="aurora-liquid"></div></div><p>%s</p></blockquote></div>' % (esc(im['src']), esc(im['alt']), esc(b['quote'])))
        elif t == 'table':
            # Порівняльна таблиця (одна на статтю): заголовок і вступ як у блоку з картками, нижче таблиця на ширину тексту.
            head = ''.join('<th scope="col">%s</th>' % esc(h) for h in b['head'])
            # marks: ['no', 'yes'] (за колонками після підпису рядка) додає червоний хрестик чи лаймову галочку; підпис колонки лишається в комірці
            # для мобільної версії, де рядок стає карткою (див. «Порівняльна таблиця» в site.css).
            marks = b.get('marks', [])
            def cell(i, c):
                m = marks[i] if i < len(marks) else ''
                return '<td%s><span class="art-cell-l">%s</span>%s</td>' % ((' class="is-%s"' % m) if m else '', esc(b['head'][i + 1]), inline(c))
            rows = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (esc(r[0]), ''.join(cell(i, c) for i, c in enumerate(r[1:]))) for r in b['rows'])
            lead = '<p class="art-cards-lead">%s</p>' % inline(b['lead']) if b.get('lead') else ''
            out.append('<section class="art-blk"><div class="art-cols"><h2>%s</h2>%s<div class="art-table-wrap"><table class="art-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div></div></section>'
                       % (esc(b['title']), lead, head, rows))
        elif t == 'photos':
            # Ряд із двох-трьох фото на ширину тексту (без плашки з цитатою), для живих кадрів посеред статті.
            n = len(b['images'])
            def _wh(src):
                from PIL import Image
                try:
                    return Image.open(os.path.join(ROOT, src.lstrip('/'))).size
                except Exception:
                    return (1200, 900)
            figs = ''.join('<figure><img src="%s" alt="%s" loading="lazy" decoding="async" width="%d" height="%d"%s></figure>'
                           % ((esc(im['src']), esc(im['alt'])) + _wh(im['src']) + (((' style="object-position: %s"' % esc(im['pos'])) if im.get('pos') else ''),))
                           for im in b['images'])
            out.append('<div class="art-photos is-%d">%s</div>' % (n, figs))
        else:
            sys.exit('blog: невідомий тип блоку %r' % t)
    return '\n'.join(out)


SHARE_ICONS = {
    'telegram': '<path d="M21.2 4.5 2.9 11.4a.5.5 0 0 0 .04.94l4.6 1.44 1.77 5.3a.5.5 0 0 0 .88.14l2.5-2.9 4.6 3.4a.5.5 0 0 0 .78-.3l3.05-14a.5.5 0 0 0-.66-.58z"/><path d="m8 13.2 8.5-5.700"/>',
    'facebook': '<path d="M14 8.500h2.800V4.500H14A4.500 4.500 0 0 0 9.500 9v2H6.800v4h2.700v5.500h4V15h2.900l.8-4h-3.700V9a.5.5 0 0 1 .5-.5z"/>',
    'x': '<path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>',
    'threads': '<path d="M17.500 9.500C16.800 6.800 14.800 5.200 12 5.200 8.500 5.200 6.200 7.800 6.200 12S8.500 18.800 12 18.800c3 0 5-1.600 5-4 0-2.200-1.700-3.300-4-3.300-1.800 0-3 .8-3 2.100 0 1.100.9 1.900 2.200 1.900 1.900 0 2.800-1.300 2.800-3.700V10"/>',
    'viber': '<path d="M5 6.500A2.500 2.500 0 0 1 7.500 4h9A2.500 2.500 0 0 1 19 6.500v6A2.500 2.500 0 0 1 16.500 15H12l-4 4v-4H7.500A2.500 2.500 0 0 1 5 12.500z"/><path d="M9.500 8.500c0 3 2 5 5 5"/>',
    'linkedin': '<rect x="4" y="4" width="16" height="16" rx="2.500"/><path d="M8.500 10.500V16M8.500 8v.01M12 16v-3.500a2 2 0 0 1 4 0V16M12 10.500V16"/>',
    'instagram': '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.600"/><path d="M16.800 7.200v.01"/>',
    'whatsapp': '<path d="M5 19l1.200-3.600A7.500 7.500 0 1 1 9 18z"/><path d="M9.600 9.400c.5 2 2.400 3.900 4.400 4.400l1-1.200-1.800-.8-.7.700c-.9-.4-1.700-1.200-2.100-2.100l.7-.7-.8-1.800z"/>',
    'link': '<path d="M10 14a4 4 0 0 0 5.700 0l3-3A4 4 0 0 0 13 5.300l-1 1"/><path d="M14 10a4 4 0 0 0-5.700 0l-3 3A4 4 0 0 0 11 18.700l1-1"/>',
    'share': '<circle cx="6" cy="12" r="2.500"/><circle cx="18" cy="6" r="2.500"/><circle cx="18" cy="18" r="2.500"/><path d="m8.200 10.800 7.600-3.600M8.200 13.200l7.600 3.600"/>',
}


def share_block(url, title):
    """Плашка «Поділитися статтею» наприкінці статті. Це звичайні посилання (працюють без JS); site.js лише додає копіювання
    адреси й системне вікно поширення на телефоні. Сторіс в Instagram із веб-сторінки відкрити не можна: це дає лише застосунок,
    тож на телефоні для цього є кнопка «Поділитися» з системним меню."""
    from urllib.parse import quote
    u, tt = quote(url, safe=''), quote(title, safe='')
    both = quote(title + ' ' + url, safe='')
    nets = [('telegram', 'Telegram', 'https://t.me/share/url?url=%s&text=%s' % (u, tt)),
            ('viber', 'Viber', 'viber://forward?text=%s' % both),
            ('whatsapp', 'WhatsApp', 'https://wa.me/?text=%s' % both),
            ('threads', 'Threads', 'https://www.threads.net/intent/post?text=%s' % both),
            ('x', 'X', 'https://twitter.com/intent/tweet?url=%s&text=%s' % (u, tt)),
            ('linkedin', 'LinkedIn', 'https://www.linkedin.com/sharing/share-offsite/?url=%s' % u)]
    # X: справжній логотип суцільною заливкою (в решти мереж контурні іконки)
    ic = lambda k: ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">%s</svg>' % SHARE_ICONS[k]) if k == 'x' else \
        ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % SHARE_ICONS[k])
    links = ''.join('<a class="art-share-btn" href="%s" target="_blank" rel="noopener noreferrer" title="%s" aria-label="Поділитися в %s" data-cta="share-%s">%s<span>%s</span></a>' % (esc(h), n, n, k, ic(k), n)
                    for k, n, h in nets)
    return ('  <aside class="art-share" aria-label="Поділитися статтею" data-url="%s" data-title="%s">\n'
            '    <span class="art-share-label">Поділитися</span>\n'
            '    <div class="art-share-row">%s'
            '<button type="button" class="art-share-btn art-share-native" data-share="native" title="Поділитися" aria-label="Поділитися" hidden>%s<span>Поділитися</span></button>'
            '<button type="button" class="art-share-btn art-share-copy" data-share="copy" title="Скопіювати посилання" aria-label="Скопіювати посилання">%s<span data-label>Скопіювати посилання</span></button></div>\n'
            '    <p class="art-share-hint" role="status" aria-live="polite" hidden></p>\n'
            '  </aside>\n' % (esc(url), esc(title), links, ic('share'), ic('link')))


def build_article(p, data, cats, posts, shared, card_fn):
    """Сторінка однієї статті /blog/<slug>/index.html із blog_src/<slug>.json."""
    a = json.load(io.open(os.path.join(ROOT, 'blog_src', p['slug'] + '.json'), encoding='utf-8'))
    slug = p['slug']
    url = '%s/blog/%s/' % (SITE, slug)
    published = p['status'] == 'published'
    plain_title = re.sub(r'<[^>]+>', '', a['headline'])
    meta_desc = a.get('meta', a['subtitle'])
    page_title = a.get('seo_title') or (plain_title + ' | Блог SILENT')
    robots = '' if published else '<meta name="robots" content="noindex, follow">\n'
    img = SITE + a.get('og', a['cover']['src'])   # окрема OG-картка 1200×630, якщо є (tools/make_og.py), інакше фото обкладинки
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'BlogPosting', '@id': url + '#article', 'mainEntityOfPage': url, 'headline': plain_title,
             'description': meta_desc, 'inLanguage': 'uk-UA', 'image': img,
             'author': {'@id': SITE + '/#organization'}, 'publisher': {'@id': SITE + '/#organization'},
             'isPartOf': {'@id': SITE + '/blog/#webpage'}},
            {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Головна', 'item': SITE + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Блог', 'item': SITE + '/blog/'},
                {'@type': 'ListItem', 'position': 3, 'name': plain_title, 'item': url}]},
        ],
    }
    if published:
        ld['@graph'][0]['datePublished'] = a.get('date_iso', a['date'])
        ld['@graph'][0]['dateModified'] = a.get('modified_iso', a.get('date_iso', a['date']))
    ld['@graph'].append({'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'\[\[[^|\]]+\|([^\]]+)\]\]', r'\1', f['a'])}} for f in a['faq']]})
    assets = shared['head_assets'].replace('../assets/', '../../assets/')
    head = (shared['pre'] + '<title>%s</title>\n<meta name="description" content="%s">\n%s'
            '<meta name="theme-color" content="#0a0a0b">\n'
            '<link rel="icon" href="/favicon.ico" sizes="48x48">\n'
            '<link rel="icon" type="image/png" href="/favicon-48x48.png" sizes="48x48">\n'
            '<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">\n'
            '<meta property="og:type" content="article">\n<meta property="og:site_name" content="SILENT">\n'
            '<meta property="og:locale" content="uk_UA">\n<meta property="og:title" content="%s">\n'
            '<meta property="og:description" content="%s">\n<meta property="og:url" content="%s">\n'
            '<meta property="og:image" content="%s">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:type" content="image/jpeg">\n<meta property="og:image:alt" content="%s">\n'
            '<meta property="article:published_time" content="%s">\n<meta property="article:modified_time" content="%s">\n'
            '<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="%s">\n<meta name="twitter:description" content="%s">\n'
            '<meta name="twitter:image" content="%s">\n<meta name="twitter:image:alt" content="%s">\n<link rel="canonical" href="%s">\n'
            % (esc(page_title), esc(meta_desc), robots, esc(page_title), esc(meta_desc), url, esc(img), esc(a['cover']['alt']),
               esc(a.get('date_iso', '')), esc(a.get('modified_iso', a.get('date_iso', ''))),
               esc(page_title), esc(meta_desc), esc(img), esc(a['cover']['alt']), url)
            + assets + '<script type="application/ld+json">\n%s\n</script>\n</head>\n'
            % json.dumps(ld, ensure_ascii=False, indent=2))
    sw = '<a href="/en/experiences/" hreflang="en" lang="en">EN</a>'
    nav_block = shared['nav_block'].replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')
    tail = shared['tail'].replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')
    # сторінка статті на рівень глибше за /blog/: скрипти внизу теж мають іти через ../../
    tail = tail.replace('src="../assets/', 'src="../../assets/')
    nav_block = nav_block.replace('src="../assets/', 'src="../../assets/')

    tags = ''.join('<span class="art-tag%s">%s</span>' % (' is-main' if i == 0 else '', esc(t)) for i, t in enumerate(a['tags']))
    cover = ('<header class="art-cover">\n  <img class="art-cover-img" src="%s" alt="%s" width="1600" height="1067" fetchpriority="high">\n'
             '  <div class="art-cover-shade" aria-hidden="true"></div>\n  <div class="wrap art-cover-in">\n'
             '    <p class="art-tags">%s</p>\n    <h1 class="art-title">%s</h1>\n    <p class="art-sub">%s</p>\n'
             '    <p class="art-meta"><span class="art-by"><img class="art-ava" src="/images/favicon.png" alt="" width="35" height="35"><b>%s</b></span>'
             '<span class="art-dot" aria-hidden="true">&middot;</span>'
             '<span class="art-when"><span>%s</span><span aria-hidden="true">&middot;</span><span>%s</span></span></p>\n  </div>\n</header>\n'
             % (esc(a['cover']['src']), esc(a['cover']['alt']), tags,
                # у заголовку дозволений лише <em> для лаймового акценту
                esc(a['headline']).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>'),
                esc(a['subtitle']), esc(a['author']), esc(a['date']), esc(a['read'])))
    plus = ('<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>')
    def faq_item(i, f):
        return ('<div class="faq-item"><div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="faqA-a%d">'
                '<h3>%s</h3>%s</div><div class="faq-a" id="faqA-a%d" role="region"><p>%s</p></div></div>'
                % (i, esc(f['q']), plus, i, inline(f['a'])))
    half = (len(a['faq']) + 1) // 2
    cols = [a['faq'][:half], a['faq'][half:]]
    faq = '<div class="faq-list">' + ''.join(
        '<div class="faq-col">' + ''.join(faq_item(i + 1 + (half if c else 0), f) for i, f in enumerate(col)) + '</div>'
        for c, col in enumerate(cols)) + '</div>'
    by_slug = {x['slug']: x for x in posts}
    stale = [r for r in a_related if r not in by_slug] if (a_related := a.get('related', [])) else []
    if stale:
        sys.exit('blog: у %s у related є слаги, яких нема в posts.json (прибрана заглушка?): %s' % (slug, ', '.join(stale)))
    rel = ''.join(card_fn(by_slug[r], cats) for r in a['related'] if r in by_slug)
    # CTA статті: за замовчуванням калькулятор; у статті можна задати свій блок "cta": {title, text, button, href, track}
    cta = dict(title='Плануєте захід? Порахуйте бюджет до заявки.', text='Калькулятор покаже орієнтир, а форма перевірить, чи вільна дата.',
               button='Порахувати вартість', href='/#price', track='blog-article-price')
    cta.update(a.get('cta', {}))
    body = ('<main id="main" tabindex="-1">\n' + cover +
            '<div class="wrap art-body">\n'
            '  <p class="art-lead">%s</p>\n%s\n%s'
            '  <aside class="art-cta"><div><h2>%s</h2><p>%s</p></div>'
            '<a class="art-cta-btn" href="%s" data-cta="%s">%s</a></aside>\n'
            '  <section class="art-faq faq" aria-labelledby="artFaq"><h2 id="artFaq">Питання, які ставлять найчастіше</h2>'
            '%s</section>\n'
            '  <section class="art-related" aria-labelledby="artRel"><h2 id="artRel">Читайте також</h2>'
            '<div class="blog-grid">\n%s</div></section>\n'
            '  <p class="art-ask">Лишилися питання? Напишіть нам у <a href="https://t.me/silent_ukraine" target="_blank" rel="noopener noreferrer">Telegram</a> '
            'або на <a href="mailto:hello.silent.ua@gmail.com">пошту</a>: відповімо протягом дня.</p>\n</div>\n\n%s'
            % (esc(a['lead']), article_blocks(a['blocks']), share_block(url, plain_title), esc(cta['title']), esc(cta['text']), esc(cta['href']), esc(cta['track']), esc(cta['button']), faq, rel, shared['form_block']))
    out = head + nav_block + body + tail
    d = os.path.join(OUT_DIR, slug)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
    print('blog/%s/index.html зібрано (%s)' % (slug, p['status']))


if __name__ == '__main__':
    build()
