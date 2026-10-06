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
    return ('        <article class="uc-card blog-card%s" data-cat="%s">\n          %s\n'
            '          <div class="uc-body">\n            <span class="blog-cat">%s</span>\n'
            '            <h3>%s</h3>\n            <p>%s</p>\n            %s\n          </div>\n        </article>\n'
            % (' is-soon' if p['status'] != 'published' else '', p['category'], media, esc(cat),
               esc(p['title']), esc(p['excerpt']), foot))


def build(preview=False):
    data = json.load(io.open(POSTS, encoding='utf-8'))
    cats = {c['id']: c['name'] for c in data['categories']}
    posts = data['posts']
    for p in posts:
        if p['category'] not in cats:
            sys.exit('blog: невідома тема %r у %s' % (p['category'], p['slug']))
        if p['status'] not in ('soon', 'draft', 'published'):
            sys.exit('blog: невідомий статус %r у %s' % (p['status'], p['slug']))
        if p['status'] in ('draft', 'published') and not os.path.exists(os.path.join(ROOT, 'blog_src', p['slug'] + '.json')):
            sys.exit('blog: немає blog_src/%s.json для статті зі статусом %s' % (p['slug'], p['status']))
    published = [p for p in posts if p['status'] == 'published']

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
        if p['status'] != 'published':
            return '<span class="blog-soon">Скоро</span>'
        return '<a class="blog-read" href="/blog/%s/">Читати</a>' % p['slug']

    hero = ('    <article class="blog-hero-card%s">\n'
            '      <img src="%s" alt="%s" width="768" height="432">\n'
            '      <div class="blog-hero-shade" aria-hidden="true"></div>\n'
            '      <span class="blog-badge">Вибір редакції</span>\n'
            '      <div class="blog-hero-text">\n'
            '        <span class="blog-cat">%s</span>\n'
            '        <h2>%s</h2>\n        <p>%s</p>\n        %s\n      </div>\n    </article>\n'
            % (' is-soon' if feat['status'] != 'published' else '', esc(feat['image']), esc(feat['alt']),
               esc(cats[feat['category']]), esc(feat['title']), esc(feat['excerpt']), meta(feat)))
    items = ''.join(
        '        <li class="blog-latest-item%s">\n          <span class="blog-num" aria-hidden="true">%02d</span>\n'
        '          <div>\n            <span class="blog-cat">%s</span>\n            <h3>%s</h3>\n            %s\n          </div>\n        </li>\n'
        % (' is-soon' if p['status'] != 'published' else '', i + 1, esc(cats[p['category']]), esc(p['title']), meta(p))
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
    out = head + nav_block + main + tail
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


def article_blocks(blocks):
    """Тіло статті з блоків article.json (схема власника від 06.10.2026):
    text  заголовок + текст у дві рівні колонки (cols: [ліва, права], елементи {p} або {steps, start}; або cards: [{t,d}] для карток із нумерацією);
    pair  фото ліворуч і яскрава лаймова плашка з головною думкою праворуч, однакової висоти."""
    out = []
    for b in blocks:
        t = b['type']
        if t == 'text':
            # Заголовок розділу окремим рядком зверху (не ширший за одну колонку), під ним дві явні рівні колонки,
            # які починаються на одній лінії; текст розкладено вручну так, щоб вони були рівні за висотою.
            def col(items):
                html = ''
                for it in items:
                    if 'p' in it:
                        html += '<p>%s</p>' % inline(it['p'])
                    elif 'steps' in it:
                        html += '<ol class="art-steps" style="counter-reset: st %d">%s</ol>' % (it.get('start', 1) - 1, ''.join(
                            '<li><b>%s</b><span>%s</span></li>' % (esc(x['t']), inline(x['d'])) for x in it['steps']))
                    else:
                        sys.exit('blog: невідомий елемент колонки %r' % it)
                return '<div class="art-col">%s</div>' % html
            if b.get('cards'):
                # Кроки як стопка плашок з головної («Що входить»): ті самі .slabs/.slab, їх веде «Стопка плашок» у site.js.
                items = ''.join(
                    '<article class="slab reveal" style="--i:%d"><span class="slab-num" aria-hidden="true">%02d</span>'
                    '<div class="slab-body"><h3>%s</h3><p>%s</p></div></article>' % (i, i + 1, esc(x['t']), inline(x['d']))
                    for i, x in enumerate(b['cards']))
                out.append('<section class="art-blk"><div class="art-cols"><h2>%s</h2><div class="slabs art-slabs">%s</div></div></section>'
                           % (esc(b['title']), items))
                continue
            left, right = b['cols']
            out.append('<section class="art-blk"><div class="art-cols"><h2>%s</h2>%s%s</div></section>'
                       % (esc(b['title']), col(left), col(right)))
        elif t == 'pair':
            im = b['image']
            out.append('<div class="art-pair"><figure class="art-pair-img"><img src="%s" alt="%s" loading="lazy" decoding="async" width="1200" height="900"></figure>'
                       '<blockquote class="art-key"><div class="band-aurora" aria-hidden="true"><div class="aurora-liquid"></div></div><p>%s</p></blockquote></div>' % (esc(im['src']), esc(im['alt']), esc(b['quote'])))
        else:
            sys.exit('blog: невідомий тип блоку %r' % t)
    return '\n'.join(out)


def build_article(p, data, cats, posts, shared, card_fn):
    """Сторінка однієї статті /blog/<slug>/index.html із blog_src/<slug>.json."""
    a = json.load(io.open(os.path.join(ROOT, 'blog_src', p['slug'] + '.json'), encoding='utf-8'))
    slug = p['slug']
    url = '%s/blog/%s/' % (SITE, slug)
    published = p['status'] == 'published'
    plain_title = re.sub(r'<[^>]+>', '', a['headline'])
    meta_desc = a.get('meta', a['subtitle'])
    page_title = plain_title + ' | Блог SILENT'
    robots = '' if published else '<meta name="robots" content="noindex, follow">\n'
    img = SITE + a['cover']['src']
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
            '<meta property="og:image" content="%s">\n<link rel="canonical" href="%s">\n'
            % (esc(page_title), esc(meta_desc), robots, esc(page_title), esc(meta_desc), url, esc(img), url)
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
             '    <p class="art-meta"><span class="art-by"><img class="art-ava" src="/images/favicon.png" alt="" width="44" height="44"><b>%s</b></span>'
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
    rel = ''.join(card_fn(by_slug[r], cats) for r in a['related'] if r in by_slug)
    body = ('<main id="main" tabindex="-1">\n' + cover +
            '<div class="wrap art-body">\n'
            '  <p class="art-lead">%s</p>\n%s\n'
            '  <aside class="art-cta"><div><h2>Плануєте захід? Порахуйте бюджет до заявки.</h2>'
            '<p>Калькулятор покаже орієнтир, а форма перевірить, чи вільна дата.</p></div>'
            '<a class="art-cta-btn" href="/#price" data-cta="blog-article-price">Порахувати вартість</a></aside>\n'
            '  <section class="art-faq faq" aria-labelledby="artFaq"><h2 id="artFaq">Питання, які ставлять найчастіше</h2>'
            '%s</section>\n'
            '  <section class="art-related" aria-labelledby="artRel"><h2 id="artRel">Читайте також</h2>'
            '<div class="blog-grid">\n%s</div></section>\n'
            '  <p class="art-ask">Лишилися питання? Напишіть нам у <a href="https://t.me/silent_ukraine" target="_blank" rel="noopener noreferrer">Telegram</a> '
            'або на <a href="mailto:hello.silent.ua@gmail.com">пошту</a>: відповімо протягом дня.</p>\n</div>\n\n%s'
            % (esc(a['lead']), article_blocks(a['blocks']), faq, rel, shared['form_block']))
    out = head + nav_block + body + tail
    d = os.path.join(OUT_DIR, slug)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
    print('blog/%s/index.html зібрано (%s)' % (slug, p['status']))


if __name__ == '__main__':
    build()
