"""Посилені версії десяти статей (16.11.2026) для сторінок форматів (діджей-сет, ярмарки, спорт, тренінги, забіги).
Кожну статтю прогнано через ту саму розмову власника в ChatGPT «Create. Бот для написания постов» (шаблон
inbox/blog/strengthen2/_header.txt: ціни без сум, факти SILENT, без тире), відповіді лежать у
inbox/blog/strengthen2/out/rw-<slug>.txt. Відповідь перевірено вручну: прибрано повтори з сусідніми статтями
(щоб не конкурували), неперевірені твердження й загальні підсумки. Скрипт перетворює markdown відповіді на блоки
статті: розділ з абзацами → текстовий блок у дві колонки, розділ зі списком → блок карток (вигляд чергується),
цитата → плашка поруч із фото, FAQ → питання. Фото й пара «фото + цитата» беруться з уже згенерованої статті
(tools/new_articles_2026_11b.py), щоб лишились лише кадри зі сторінок послуг.
Запуск: python3 tools/strengthen_articles_2026_11b.py [slug ...] && python3 tools/build_en.py
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import article_edits_2026_11b as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'blog_src')
OUT = os.path.join(ROOT, 'inbox', 'blog', 'strengthen2', 'out')

# Розділи, які прибираємо (повтор сусідньої статті чи загальні слова), і точкові заміни тексту.
DROP = {
    # Кілька діджеїв і батл розкриває окрема стаття: тут лишаємо одне речення з посиланням (див. EXTRA нижче).
    'dj-set-u-navushnykakh': ['Чому три канали змінюють атмосферу вечора'],
}
EXTRA = {
    'dj-set-u-navushnykakh': {'after': 'Як працює діджей-сет у навушниках', 'p': (
        'Якщо діджеїв кілька, кожен отримує свій канал, і на одному майданчику можуть грати до трьох сетів одночасно. '
        'Як перетворити це на змагання з раундами, ми розповіли окремо: [[/blog/dj-batl-try-didzhei/|діджей-батл у навушниках]].')},
    # У відповідях ChatGPT для цих двох статей зникло посилання на сторінку послуги: повертаємо.
    'hrupove-trenuvannia-prosto-neba': {'after': 'Як навушники допомагають тренеру працювати з групою', 'p': (
        'Детальніше про формат: [[/experiences/sport/|навушники SILENT для тренувань і спортивних подій]].')},
    'tantsiuvalna-prohulianka-mistom': {'after': 'Що таке танцювальна прогулянка і як вона працює', 'p': (
        'Детальніше про формат: [[/experiences/runs-walks/|навушники SILENT для забігів і прогулянок]]. '
        'А якщо група не танцює, а біжить, читайте, [[/blog/yak-orhanizuvaty-zabih/|як організувати забіг]].')},
}
# Кома, яку ChatGPT поставив на місці тире (тире заборонені): робимо двокрапку чи прибираємо.
REPL = {
    'dj-set-u-navushnykakh': [('уникнути плутанини в день вечірки, поговорити', 'уникнути плутанини в день вечірки: поговорити')],
    'rozvahy-na-yarmarku': [('Їхнє завдання, дати', 'Їхнє завдання: дати')],
    'tantsiuvalna-prohulianka-mistom': [('Його завдання, допомогти', 'Його завдання: допомогти'),
                                        ('Танцювальна прогулянка, це групова', 'Танцювальна прогулянка це групова')],
    'vyiznyi-treninh-yak-orhanizuvaty': [('рішення для навчання команди, змінити', 'рішення для навчання команди: змінити')],
    'dj-batl-try-didzhei': [('Інший варіант, зробити', 'Інший варіант: зробити'),
        # колонки розділу «Як визначити переможця» різнились на три рядки: прибираємо службову фразу
        ('{"p": "Є кілька способів визначити найкращого діджея."}, ', ''),
        ('[[/experiences/dj-set/|Детальніше про формат діджей-сету в навушниках]]', 'Детальніше про [[/experiences/dj-set/|формат діджей-сету в навушниках]]')],
    'yak-orhanizuvaty-sportyvne-sviato': [('Детальніше про [[/blog/hrupove-trenuvannia-prosto-neba/|нього можна прочитати тут]]',
        'Про нього ми розповіли окремо: [[/blog/hrupove-trenuvannia-prosto-neba/|групове тренування просто неба]]')],
    'yak-provesty-treninh-dlia-velykoi-hrupy': [('[[/blog/vyiznyi-treninh-yak-orhanizuvaty/|Про це читайте в статті]]',
        'Про це окрема стаття: [[/blog/vyiznyi-treninh-yak-orhanizuvaty/|виїзний тренінг]]')],
    'yak-orhanizuvaty-zabih': [('[[/blog/tantsiuvalna-prohulianka-mistom/|Про цей формат читайте тут]]',
        'Про цей формат окрема стаття: [[/blog/tantsiuvalna-prohulianka-mistom/|танцювальна прогулянка містом]]')],
    'hrupove-trenuvannia-prosto-neba': [('Один із варіантів для групових занять просто неба, бездротові', 'Один із варіантів для групових занять просто неба: бездротові')],
}

LINK = re.compile(r'([^.;!?(]*?)\s*\(посилання:\s*(/[^)\s]+)\)')

def links(t):
    """«текст (посилання: /шлях/)» → [[/шлях/|текст]]. Підпис: слова перед дужкою після останньої двокрапки чи коми;
    якщо перед дужкою двокрапка й підпису нема («зібрали в окремій статті: (посилання)»), посиланням стає фраза перед
    двокрапкою. Довгий підпис скорочуємо до частини після останнього прийменника «в/у/про»."""
    def short(lead, label):
        if len(label.split()) > 5:
            k = max(label.rfind(' в '), label.rfind(' у '), label.rfind(' про '))
            if k > 0:
                n = 5 if label[k:k + 5] == ' про ' else 3
                if len(label[k + n:].split()) >= 2:
                    return lead + label[:k + n], label[k + n:]
        return lead, label
    def rep(m):
        before, href = m.group(1), m.group(2)
        ws = before[:len(before) - len(before.lstrip())]
        core = before.strip()
        if core.endswith(':') or not core:
            core = core.rstrip(':').rstrip()
            cut = max(core.rfind(': '), core.rfind(', '))
            lead, label = (core[:cut + 2], core[cut + 2:]) if cut >= 0 else ('', core)
            lead, label = short(lead, label)
            return '%s%s[[%s|%s]]' % (ws, lead, href, label) if label else before
        cut = max(core.rfind(': '), core.rfind(', '))
        lead, label = (core[:cut + 2], core[cut + 2:]) if cut >= 0 else ('', core)
        lead, label = short(lead, label.strip())
        if not label:
            return before
        return '%s%s[[%s|%s]]' % (ws, lead, href, label)
    return LINK.sub(rep, t)

def clean(t):
    t = t.replace('*', '').replace('—', ',').replace('–', ',').strip()
    t = re.sub(r'\s+,', ',', t)
    return links(t)

def parse(md):
    lines = [l.rstrip() for l in md.split('\n')]
    meta = {}; sections = []; cur = None; lead = []; mode = None
    for l in lines:
        s = l.strip()
        if not s: continue
        low = s.replace('*', '').lower()
        if low.startswith('seo title:'): meta['seo'] = s.replace('*', '').split(':', 1)[1].strip(); continue
        if low.startswith('meta description:'): meta['meta'] = s.replace('*', '').split(':', 1)[1].strip(); continue
        if low.startswith('підзаголовок:'): meta['sub'] = s.replace('*', '').split(':', 1)[1].strip(); continue
        if s.startswith('# '): meta['h1'] = s[2:]; continue
        if low in ('вступ', 'вступ:'): mode = 'lead'; continue
        if low.startswith('вступ:'): lead.append(s.replace('*', '').split(':', 1)[1].strip()); continue
        if s.startswith('## '):
            cur = {'title': re.sub(r'^\d+\.\s*', '', s[3:].replace('*', '').strip()), 'items': []}; sections.append(cur); mode = 'sec'; continue
        if mode == 'lead' and cur is None:
            if s.startswith('*') and s.endswith('*') and len(s) < 200 and not lead: pass
            lead.append(s); continue
        if cur is None: continue
        if s.startswith('### '): cur['items'].append(('h3', re.sub(r'^\d+\.\s*', '', s[4:].replace('*', '').strip())))
        elif s.startswith('- '): cur['items'].append(('li', s[2:]))
        elif s.startswith('> '): cur['items'].append(('q', s[2:]))
        elif s.startswith('*') and s.endswith('*') and s.count('*') == 2 and len(s) < 220:
            # Курсивний рядок: цитата-кандидат, але підводка на двокрапку («Чекліст перед…:») лишається абзацом.
            cur['items'].append(('p', s) if s.strip('*').rstrip().endswith(':') else ('qi', s.strip('*')))
        else: cur['items'].append(('p', s))
    return meta, lead, sections

def card(li):
    m = re.match(r'\*([^*]+?)[.:]?\*[.:]?\s*(.*)$', li)
    if m: return {'t': clean(m.group(1)).rstrip('.:'), 'd': clean(m.group(2))}
    if ': ' in li and len(li.split(': ', 1)[0]) < 60:
        a, b = li.split(': ', 1); return {'t': clean(a), 'd': clean(b)}
    return {'t': clean(li), 'd': ''}

# Іконки для тематичних переліків (ключі ART_ICONS у build_blog.py). Ключ: початок слова в назві картки, перший збіг.
ICON_KEYS = [('дах', 'sun'), ('терас', 'sun'), ('ресторан', 'chat'), ('музе', 'calm'), ('галере', 'eye'), ('офіс', 'case'),
    ('пляж', 'sun'), ('басейн', 'drop'), ('двір', 'sofa'), ('сад', 'sofa'), ('жанр', 'versus'), ('десятиліт', 'clock'),
    ('резидент', 'star'), ('колег', 'person'), ('кількіст', 'mixed'), ('сум', 'clipboard'), ('гостей', 'heart'), ('журі', 'star'),
    ('торгов', 'gift'), ('фудкорт', 'drop'), ('майстеркл', 'bulb'), ('простір для майстер', 'bulb'), ('сцен', 'mic'), ('танцпол', 'party'),
    ('інформац', 'pin'), ('дегустац', 'drop'), ('виступ', 'mic'), ('фотозон', 'eye'), ('квест', 'route'), ('зимов', 'star'),
    ('вечірн', 'active'), ('сімейн', 'heart'), ('естафет', 'active'), ('командні спорт', 'active'), ('конкурси на коорд', 'eye'),
    ('ігри на команд', 'mixed'), ('веселі', 'party'), ('інтелект', 'bulb'), ('парні', 'person'), ('фінальна', 'star'),
    ('воду', 'drop'), ('покритт', 'route'), ('розмір', 'mixed'), ('тінь', 'sun'), ('навколишн', 'route'), ('побут', 'sofa'), ('погод', 'cloud'),
    ('простір для всієї', 'mixed'), ('зони для практ', 'bulb'), ('умови для облад', 'headphones'), ('план на випадок', 'cloud'),
    ('логіст', 'route'), ('переход', 'siren'), ('ширин', 'route'), ('місця для зуп', 'pin'), ('воду', 'drop'), ('старт', 'pin'),
    ('зручність для піш', 'person'), ('зрозуміла навіг', 'route'), ('мінімум склад', 'siren'), ('цікаві точки', 'eye'),
    ('зручний старт', 'pin'), ('простір для фіналу', 'party'), ('апаратур', 'speaker'), ('живлен', 'bulb'), ('час на налашт', 'clock'),
    ('що робити, якщо потрібен', 'mic'), ('голос', 'mic'), ('музика разом', 'wave'), ('індивідуальн', 'headphones'), ('три канали', 'wave'),
    ('розташування пульт', 'speaker'), ('маршрут гостей', 'route'), ('час завершен', 'clock'), ('місце повернен', 'pin'),
    ('кількість діджеїв', 'mixed'), ('формат батлу', 'versus'), ('особливості прог', 'clipboard'), ('плейлист', 'wave'),
    ('години доступ', 'clock'), ('місце розвантаж', 'pin'), ('проходи', 'route'), ('прибиран', 'clipboard'),
    ('спільне поясн', 'mic'), ('робота в підгруп', 'mixed'), ('представлен', 'star'), ('перерви', 'clock')]

def icon_for(t):
    low = t.lower()
    for k, ic in ICON_KEYS:
        if low.startswith(k) or (' ' + k) in ' ' + low[:40]:
            return ic
    return None

def visual_pass(blocks):
    """Impeccable polish у межах шаблону: (1) тематичні переліки з короткими назвами отримують іконки, якщо кожна назва
    має іконку; (2) переліки-запитання («Чи…», «Хто…») стають легким списком split замість важких карток;
    (3) два сусідні блоки карток не повторюють той самий вигляд."""
    prev = None
    for b in blocks:
        if b.get('keep') and b.get('cards'):
            prev = (b.get('layout'), b.get('marks')); continue
        if b.get('type') != 'text' or not b.get('cards'):
            prev = None if b.get('type') == 'text' else prev
            continue
        cards = b['cards']; tl = b['title'].lower()
        checklist = re.search(r'чекліст|перевір|узгод|підготу|що потрібно|вартість|скільки|врахувати', tl)
        questions = sum(c['t'].rstrip().endswith('?') or re.match(r'(Чи|Хто|Який|Яка|Які|Де|Що|Скільки|Коли)\b', c['t']) is not None for c in cards) >= len(cards) / 2
        ics = [icon_for(c['t']) for c in cards]
        if not checklist and not re.search(r'побуд|сценар|етап|ритм|увагу', tl) and all(ics) and len(set(ics)) > 1:
            for c, ic in zip(cards, ics): c['ic'] = ic
            b['marks'] = 'icons'
            if b.get('layout') in ('split', 'rows'): b['layout'] = 'three' if len(cards) == 6 else 'cols'
        elif questions and not any(c['d'] for c in cards):
            b['layout'] = 'split'; b['marks'] = 'none'
            if not b.get('lead'): b['lead'] = (b.get('foot') or [''])[:1]; b['foot'] = (b.get('foot') or [])[1:]
        if re.search(r'як (вона )?працює|реєстрац', tl) and len(cards) in (4, 6) and 'ic' not in cards[0]:
            b['layout'] = 'rows'; b.pop('marks', None)   # покрокові переліки: нумеровані рядки
        elif tl.startswith('чому') and b.get('marks') == 'check':
            b['marks'] = 'none'   # перелік проблем, а не дій: галочка тут бреше
        sig = (b.get('layout'), b.get('marks'))
        if prev == sig:
            # Сусідній блок такого самого вигляду: беремо перший допустимий інший варіант (cols лише 4/8, three лише 6).
            n = len(cards); has_d = any(c['d'] for c in cards)
            ok = lambda l: (l != 'cols' or n in (4, 8)) and (l != 'three' or n == 6) and (l != 'split' or not has_d)
            for l, m in [('cols', 'check'), ('split', 'check'), ('cols', 'none'), ('rows', None), ('three', 'check'), ('three', 'none'), ('split', 'none')]:
                if ok(l) and (l, m) != prev and not (m == 'check' and not checklist):
                    b['layout'] = l
                    if m: b['marks'] = m
                    else: b.pop('marks', None)
                    break
            sig = (b.get('layout'), b.get('marks'))
        # Довгі описи у вузьких колонках читаються погано: cols/three з середнім описом >160 символів стають рядками.
        avg = sum(len(c['d']) for c in cards) / len(cards)
        if b.get('layout') in ('cols', 'three') and avg > 160 and len(cards) != 3:
            b['layout'] = 'rows'
            if b.get('marks') is None and not re.search(r'побуд|сценар|етап|ритм|увагу|програм', tl): b['marks'] = 'none'
            sig = (b.get('layout'), b.get('marks'))
        prev = sig

def build(slug):
    md = open(os.path.join(OUT, 'rw-%s.txt' % slug), encoding='utf-8').read()
    meta, lead, sections = parse(md)
    art = json.load(open(os.path.join(SRC, slug + '.json'), encoding='utf-8'))
    old = art['blocks']
    pair = next((b for b in old if b['type'] == 'pair'), None)
    photos = next((b for b in old if b['type'] == 'photos'), None)
    faq, blocks, quote, quote_i = [], [], None, None
    variants = [('rows', None), ('three', 'check'), ('cols', 'none'), ('split', 'check')]
    vi = 0
    for sec in sections:
        title = sec['title']
        if title in DROP.get(slug, []): continue
        if title.lower().startswith('faq') or 'запитання' in title.lower() or title.lower().startswith('питання'):
            q = None
            for kind, t in sec['items']:
                if kind in ('q', 'qi') or (kind == 'p' and t.startswith('*') and t.endswith('*')): q = clean(t)
                elif kind == 'h3': q = clean(t)
                elif kind == 'p' and q: faq.append({'q': q, 'a': clean(t)}); q = None
            continue
        items = []
        for kind, t in sec['items']:
            if kind == 'q':
                quote = quote or clean(t)   # «> …»: справжня цитата від ChatGPT, має перевагу
            elif kind == 'qi':
                quote_i = quote_i or clean(t)
            else:
                items.append((kind, t))
        # Кілька списків у розділі. Групи з підписом на двокрапку («Локація та умови:») стають картками однієї сітки
        # (назва групи + пункти реченнями). Якщо підписи є не в усіх групах, перший список лишається основним блоком,
        # а кожен наступний список із підписом стає окремим блоком-чеклістом із заголовком із підпису.
        groups, cur_g, pending = [], None, None
        for k, t in items:
            if k == 'li':
                if cur_g is None: cur_g = {'intro': pending, 'items': []}; groups.append(cur_g); pending = None
                cur_g['items'].append(t)
            else:
                cur_g = None
                pending = t.strip('*').strip() if (k == 'p' and t.strip('*').rstrip().endswith(':') and len(t) < 90) else None
        if len(groups) >= 2 and all(g['intro'] for g in groups) and len(groups) in (2, 3):
            sent = lambda t: (lambda c: (c['t'] + ('. ' + c['d'] if c['d'] else '')).rstrip('.') + '.')(card(t))
            cards = [{'t': clean(g['intro']).rstrip(':'), 'd': ' '.join(sent(t) for t in g['items'])} for g in groups]
            intros = {g['intro'] for g in groups}
            pre = [clean(t) for k, t in items[:next(i for i, (k, _) in enumerate(items) if k == 'li')] if k == 'p' and t.strip('*').strip() not in intros]
            last_li = max(i for i, (k, _) in enumerate(items) if k == 'li')
            post = [clean(t) for k, t in items[last_li + 1:] if k == 'p']
            blk = {'type': 'text', 'title': title, 'cards': cards, 'layout': 'three' if len(groups) == 3 else 'rows', 'marks': 'none'}
            if pre: blk['lead'] = pre
            if post: blk['foot'] = post
            blocks.append(blk)
            continue
        if len(groups) >= 2 and groups[1]['intro']:
            # другий список із підписом → окремий блок після основного (обробляємо основний нижче, без нього)
            g2 = groups[1]
            cut = next(i for i, (k, t) in enumerate(items) if k == 'p' and t.strip('*').strip() == g2['intro'])
            tail = items[cut:]; items = items[:cut]
            extra_cards = [card(t) for t in g2['items']][:8]
            if len(extra_cards) % 2: extra_cards = extra_cards[:-1]
            extra = {'type': 'text', 'title': clean(g2['intro']).rstrip(':'), 'cards': extra_cards, 'layout': 'cols' if len(extra_cards) in (4, 8) else 'three', 'marks': 'check'}
            tail_p = [clean(t) for k, t in tail if k == 'p' and t.strip('*').strip() != g2['intro']]
            if tail_p: extra['foot'] = tail_p
        else:
            extra = None
        # Перший суцільний список розділу стає картками; усе, що після нього (абзаци й інші списки), іде у висновок
        # абзацами: другий список зливається з підводкою в одне речення-перелік. Так у блоці лишаються 4, 6 чи 8 карток.
        first = next((i for i, (k, _) in enumerate(items) if k == 'li'), None)
        lis, rest = [], []
        if first is not None:
            e = first
            while e < len(items) and items[e][0] == 'li': e += 1
            lis = [t for _, t in items[first:e]]
            rest = items[e:]
            if len(lis) % 2 or len(lis) > 8:
                keep = 8 if len(lis) > 8 else len(lis) - 1
                if keep < 4:   # короткий непарний список: пункти стають абзацами
                    items = [('p', (lambda c: c['t'] + (': ' + c['d'] if c['d'] else ''))(card(t))) if k == 'li' else (k, t) for k, t in items]
                    lis = []
                else:
                    rest = [('li', t) for t in lis[keep:]] + rest
                    lis = lis[:keep]
        h3s = [i for i, (k, _) in enumerate(items) if k == 'h3']
        if not lis and len(h3s) in (4, 6, 8) and h3s[0] <= 3 and all(items[i + 1][0] == 'p' for i in h3s if i + 1 < len(items)):
            # Візуальний прохід (Impeccable polish): розділ «підзаголовок + абзац» × 4/6/8 читається як стіна тексту.
            # Робимо картки: послідовність (сценарій, програма, етапи) нумерованими рядками, решту з іконками.
            groups = []
            for n_, i in enumerate(h3s):
                end = h3s[n_ + 1] if n_ + 1 < len(h3s) else len(items)
                groups.append({'t': clean(items[i][1]), 'd': ' '.join(clean(t) for k, t in items[i + 1:end] if k == 'p')})
            lead_p = [clean(t) for k, t in items[:h3s[0]] if k == 'p']
            seq = re.search(r'побуд|програм|сценар|етап|ритм|увагу', title.lower())
            blk = {'type': 'text', 'title': title, 'cards': groups, 'layout': 'rows' if seq else 'cols'}
            if not seq: blk['marks'] = 'none'
            if lead_p: blk['lead'] = lead_p
            blocks.append(blk)
            continue
        if not lis:
            col = [({'h3': clean(t)} if k == 'h3' else {'p': clean(t)}) for k, t in items]
            if not col: continue
            blk = {'type': 'text', 'title': title, 'cols': [col]}
            blocks.append(blk)
        else:
            before = [t for k, t in items[:first]]
            after = []
            for k, t in rest:
                if k == 'li':
                    c = card(t); item = (c['t'] + (' (' + c['d'].rstrip('.') + ')' if c['d'] else '')).rstrip('.')
                    if after and after[-1].endswith(':'): after[-1] += ' ' + item[0].lower() + item[1:]
                    elif after and after[-1].endswith(';'): after[-1] += ' ' + item[0].lower() + item[1:]
                    else: after.append(item)
                    after[-1] += ';'
                else:
                    if after and after[-1].endswith(';'): after[-1] = after[-1][:-1] + '.'
                    after.append(t)
            if after and after[-1].endswith(';'): after[-1] = after[-1][:-1] + '.'
            pre = [clean(t) for t in before]
            cards = [card(t) for t in lis]
            title_cards = title
            long_pre = len(' '.join(pre)) > 500
            n = len(cards); has_d = any(c['d'] for c in cards)
            layout, marks = variants[vi % len(variants)]; vi += 1
            if n == 8: layout, marks = 'cols', ('none' if has_d else 'check')
            if n == 6 and layout == 'rows': layout = 'three'
            if n == 4 and has_d: layout, marks = ('rows', None) if vi % 2 else ('cols', 'none')   # чергуємо рядки й колонки
            if not has_d: layout, marks = ('split', 'check') if n >= 6 else ('three' if n == 6 else 'cols', 'check')
            if long_pre and layout == 'split': layout = 'three' if n == 6 else 'cols'
            if n == 6 and layout == 'cols': layout = 'three'   # 6 карток у 4 колонки лишають порожні клітинки
            blk = {'type': 'text', 'title': title_cards or (title + ': коротко'), 'layout': layout, 'cards': cards}
            if marks: blk['marks'] = marks
            if layout == 'split':
                blk['lead'] = pre[:1] or [''] ; blk['foot'] = pre[1:] + [clean(t) for t in after]
            else:
                if pre: blk['lead'] = pre
                if after: blk['foot'] = [clean(t) for t in after]
                if len(pre) > 2: blk['lead_cols'] = True
                if len(after) > 2: blk['foot_cols'] = True
            if layout == 'split' and not blk['lead'][0]:
                blk['lead'] = blk['foot'][:1] or ['']; blk['foot'] = blk['foot'][1:]
            blocks.append(blk)
        if extra: blocks.append(extra)
        ex = EXTRA.get(slug)
        if ex and ex['after'] == title:
            last = blocks[-1]
            if 'cols' in last: last['cols'][0].append({'p': ex['p']})
            else: last.setdefault('foot', []).append(ex['p'])
    E.apply(slug, blocks)
    visual_pass(blocks)
    for b in blocks: b.pop('keep', None)
    # Блок про вартість завжди останній перед CTA (рішення власника 17.11.2026): чекліст іде перед ним.
    pi = [i for i, x in enumerate(blocks) if x.get('type') == 'text' and re.match(r'(Скільки коштує|Вартість|Що входить у роботу SILENT)', x['title'])]
    if pi and pi[-1] != len(blocks) - 1:
        blocks.append(blocks.pop(pi[-1]))
    # Фото: пара з цитатою після другого блоку, дві фотографії перед передостаннім.
    if pair:
        if quote or quote_i: pair['quote'] = quote or quote_i
        blocks.insert(min(2, len(blocks)), pair)
    if photos:
        # Фото ставимо всередину найдовшої ділянки з ≥3 текстових блоків поспіль (розбиває «стіну»), інакше ближче до кінця.
        runs, i = [], 0
        while i < len(blocks):
            j = i
            while j < len(blocks) and blocks[j].get('type') == 'text' and not blocks[j].get('cards'): j += 1
            if j - i >= 3: runs.append((j - i, i))
            i = j + 1 if j == i else j
        if runs:
            ln, st = max(runs); blocks.insert(st + ln // 2, photos)
        else:
            blocks.insert(max(len(blocks) - 2, 3), photos)
    words = len(re.findall(r'\w+', json.dumps(blocks, ensure_ascii=False) + ' '.join(lead)))
    art['blocks'] = blocks
    art['lead'] = E.LEADS.get(slug) or clean(' '.join(lead))
    if meta.get('sub'): art['subtitle'] = clean(meta['sub'])
    if meta.get('meta') and len(meta['meta']) <= 160: art['meta'] = clean(meta['meta'])
    if len(faq) >= 4: art['faq'] = faq[:6] if len(faq) % 2 == 0 else faq[:len(faq) - 1]
    art['read'] = '%d хв читання' % max(5, round(words * 0.62 / 180))
    for a, b in REPL.get(slug, []):
        s = json.dumps(art, ensure_ascii=False)
        if a not in s: print('  (заміни нема в статті:', a[:40], ')'); continue
        art = json.loads(s.replace(a, b))
    art['_note'] = art.get('_note', '') + ' Посилено 16.11.2026 через ChatGPT (tools/strengthen_articles_2026_11b.py).'
    json.dump(art, open(os.path.join(SRC, slug + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return len(blocks), len(faq), art['read']

if __name__ == '__main__':
    slugs = sys.argv[1:] or [f[3:-4] for f in sorted(os.listdir(OUT)) if f.startswith('rw-')]
    for s in slugs:
        print(s, build(s))
