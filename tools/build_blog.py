#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Збирає сторінку блогу /blog/ із blog_src/posts.json.

Шапка, меню, підвал, форма й скрипти беруться з experiences/index.html при кожній збірці,
тож блог не розходиться з рештою сайту (меню в нас продубльоване по сторінках, тут його
копіювати вручну не треба).

Перший етап: усі матеріали мають status "soon" (заглушки): картка виглядає як справжня,
але без посилання, з міткою «Скоро». Коли стаття готова, у posts.json статус міняємо на
"published" і кладемо blog_src/<slug>.md (збірка статей додається разом із першою статтею).

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


def card(p, cats):
    """Картка в загальній сітці. Заглушка: <article> без посилання."""
    cat = cats[p['category']]
    media = ('<div class="uc-media"><img src="%s" alt="%s" loading="lazy" decoding="async" width="768" height="432"></div>'
             % (esc(p['image']), esc(p['alt'])))
    if p['status'] == 'soon':
        foot = '<span class="blog-soon">Скоро</span>'
        head, tail = '', ''
    else:
        foot = '<a class="uc-order" href="/blog/%s/">Читати</a>' % p['slug']
        head, tail = '', ''
    return ('        <article class="uc-card blog-card%s" data-cat="%s">\n          %s\n'
            '          <div class="uc-body">\n            <span class="blog-cat">%s</span>\n'
            '            <h3>%s</h3>\n            <p>%s</p>\n            %s\n          </div>\n        </article>\n'
            % (' is-soon' if p['status'] == 'soon' else '', p['category'], media, esc(cat),
               esc(p['title']), esc(p['excerpt']), foot))


def build(preview=False):
    data = json.load(io.open(POSTS, encoding='utf-8'))
    cats = {c['id']: c['name'] for c in data['categories']}
    posts = data['posts']
    for p in posts:
        if p['category'] not in cats:
            sys.exit('blog: невідома тема %r у %s' % (p['category'], p['slug']))
        if p['status'] == 'published' and not os.path.exists(os.path.join(ROOT, 'blog_src', p['slug'] + '.md')):
            sys.exit('blog: немає blog_src/%s.md для опублікованої статті' % p['slug'])
    published = [p for p in posts if p['status'] == 'published']
    if published:
        sys.exit('blog: збірка сторінок статей ще не додана (додається разом із першою статтею)')

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
    tail = re.sub(r'<!-- Flip[^\n]*\n(?:[^\n]*\n)??<script src="\.\./assets/vendor/Flip\.min\.js[^"]*"></script>\n', '', tail)
    tail = re.sub(r'<script src="\.\./assets/vendor/Flip\.min\.js[^"]*"></script>\n', '', tail)
    for blk in (nav_block, tail):
        pass
    sw = '<a href="/en/experiences/" hreflang="en" lang="en">EN</a>'
    nav_block = nav_block.replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')
    tail = tail.replace(sw, '<a href="/en/" hreflang="en" lang="en">EN</a>')

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
            '<meta property="og:image" content="%s/images/og/og-experiences.jpg">\n'
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
        return '<span class="blog-soon">Скоро</span>' if p['status'] == 'soon' else ''

    hero = ('    <article class="blog-hero-card%s">\n'
            '      <img src="%s" alt="%s" width="768" height="432">\n'
            '      <div class="blog-hero-shade" aria-hidden="true"></div>\n'
            '      <span class="blog-badge">Вибір редакції</span>\n'
            '      <div class="blog-hero-text">\n'
            '        <span class="blog-cat">%s</span>\n'
            '        <h2>%s</h2>\n        <p>%s</p>\n        %s\n      </div>\n    </article>\n'
            % (' is-soon' if feat['status'] == 'soon' else '', esc(feat['image']), esc(feat['alt']),
               esc(cats[feat['category']]), esc(feat['title']), esc(feat['excerpt']), meta(feat)))
    items = ''.join(
        '        <li class="blog-latest-item%s">\n          <span class="blog-num" aria-hidden="true">%02d</span>\n'
        '          <div>\n            <span class="blog-cat">%s</span>\n            <h3>%s</h3>\n            %s\n          </div>\n        </li>\n'
        % (' is-soon' if p['status'] == 'soon' else '', i + 1, esc(cats[p['category']]), esc(p['title']), meta(p))
        for i, p in enumerate(latest))
    latest_html = ('    <aside class="blog-latest glass-panel" aria-labelledby="blogLatestTitle">\n'
                   '      <h2 id="blogLatestTitle" class="blog-latest-title">Свіже</h2>\n      <ol class="blog-latest-list">\n%s      </ol>\n    </aside>\n' % items)
    chips = ('      <button type="button" class="blog-chip is-on" data-cat="all" aria-pressed="true">Усі <span>%d</span></button>\n' % len(posts)
             + ''.join('      <button type="button" class="blog-chip" data-cat="%s" aria-pressed="false">%s <span>%d</span></button>\n'
                       % (c['id'], esc(c['name']), counts.get(c['id'], 0)) for c in data['categories'] if counts.get(c['id'])))
    cards = ''.join(card(p, cats) for p in posts)

    main = ('<main id="main" tabindex="-1">\n\n<section class="blog-head">\n  <div class="wrap">\n'
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
    out = head + nav_block + main + tail
    os.makedirs(OUT_DIR, exist_ok=True)
    io.open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8').write(out)
    print('blog/index.html зібрано: %d матеріалів (%d опубліковано, решта заглушки)' % (len(posts), len(published)))


if __name__ == '__main__':
    build()
