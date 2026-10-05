#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Збирає en/index.html з index.html.

Українська сторінка — єдине джерело правди. Англійська не редагується руками:
вона щоразу генерується заново, тож структура, класи, порядок блоків і будь-яка
правка розмітки приходять в англійську версію самі. Тут лежить тільки те, чим
дві версії різняться, — словник рядків, шляхи до файлів і SEO-теги.

Запуск:  python3 tools/build_en.py
Після зміни тексту в index.html прогнати ще раз.
"""
import hashlib, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, 'index.html')
DST  = os.path.join(ROOT, 'en', 'index.html')
SRC404 = os.path.join(ROOT, '404.html')
DST404 = os.path.join(ROOT, 'en', '404.html')

NB = ' '   # нерозривний пробіл, яким в українському тексті склеєні прийменники

# ---------------------------------------------------------------- SEO / head
HEAD = [
 ('<html lang="uk">', '<html lang="en">'),
 ('<title>SILENT — Silent Disco під ключ у Києві та по Україні</title>',
  '<title>SILENT — Full-service silent disco in Kyiv and across Ukraine</title>'),
 ('<meta name="description" content="SILENT — Silent Disco під ключ у Києві та по Україні: бездротові LED-навушники, 3 канали музики, доставка, налаштування й супровід на вашій події.">',
  '<meta name="description" content="SILENT — full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, 3 music channels, delivery, setup and on-site support for your event.">'),
 ('<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="en_US">'),
 ('<meta property="og:title" content="SILENT — одна вечірка. Три музичні світи.">',
  '<meta property="og:title" content="SILENT — one party. Three worlds of music.">'),
 ('<meta property="og:description" content="SILENT — Silent Disco під ключ у Києві та по Україні: бездротові LED-навушники, 3 канали музики, доставка, налаштування й супровід на вашій події.">',
  '<meta property="og:description" content="SILENT — full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, 3 music channels, delivery, setup and on-site support for your event.">'),
 ('<meta property="og:url" content="https://silent.org.ua/">',
  '<meta property="og:url" content="https://silent.org.ua/en/">'),
 ('<meta name="twitter:title" content="SILENT — одна вечірка. Три музичні світи.">',
  '<meta name="twitter:title" content="SILENT — one party. Three worlds of music.">'),
 ('<meta name="twitter:description" content="SILENT — Silent Disco під ключ у Києві та по Україні: бездротові LED-навушники, 3 канали музики, доставка, налаштування й супровід на вашій події.">',
  '<meta name="twitter:description" content="SILENT — full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, 3 music channels, delivery, setup and on-site support for your event.">'),
 ('<link rel="canonical" href="https://silent.org.ua/">',
  '<link rel="canonical" href="https://silent.org.ua/en/">'),
 # Логотип у шапці: українська веде на /, англійська — на /en/ (JS на самій
 # головній гортає вгору без перезавантаження).
 ('<a href="/" class="logo"', '<a href="/en/" class="logo"'),
]

# ------------------------------------------------- JSON-LD головної (EN)
# Одна організація на бренд, а не по одній на мову. WebSite і Organization
# спільні й ідентичні в обох версіях (@id лишаються https://silent.org.ua/#…),
# у англійській немає лише description організації (воно українське). Те, що
# справді залежить від мови, — Service і WebPage — отримує власні адреси
# /en/#service і /en/#webpage, тож два тексти не суперечать один одному.
import json as _json
_SITE = 'https://silent.org.ua'
_LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
EN_SERVICE_NAME = 'Full-service silent disco'
EN_SERVICE_DESC = ('Wireless LED headphones with three music channels, delivery, on-site setup, '
                   'technical support through the evening, teardown and removal — as one service.')
EN_OFFER_DESC = ('From 12,000 UAH: 40 headphones for 4 hours. The final price depends on the date, '
                 'location, duration and format.')
EN_PAGE_NAME = 'SILENT — Full-service silent disco in Kyiv and across Ukraine'
EN_PAGE_DESC = ('SILENT — full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, '
                '3 music channels, delivery, setup and on-site support for your event.')


def en_home_jsonld(s):
    m = _LD.search(s)
    d = _json.loads(m.group(2))
    by = {n['@type']: n for n in d['@graph']}
    by['Organization'].pop('description', None)
    svc = by['Service']
    svc['@id'] = _SITE + '/en/#service'
    svc['name'] = EN_SERVICE_NAME
    svc['description'] = EN_SERVICE_DESC
    svc['offers']['description'] = EN_OFFER_DESC
    page = by['WebPage']
    page.update({'@id': _SITE + '/en/#webpage', 'url': _SITE + '/en/', 'name': EN_PAGE_NAME,
                 'description': EN_PAGE_DESC, 'inLanguage': 'en',
                 'mainEntity': {'@id': _SITE + '/en/#service'}})
    text = '\n' + _json.dumps(d, ensure_ascii=False, indent=2) + '\n'
    return s[:m.start(2)] + text + s[m.end(2):]


# ------------------------------------------------- JSON-LD сторінки FAQ
# Розмітка FAQPage збирається З ВИДИМОЇ сторінки при кожному запуску, а не
# пишеться руками: раніше в ній було 9 питань, коли на сторінці їх 48.
from html.parser import HTMLParser as _HP


class _FaqParser(_HP):
    """Збирає пари «питання → відповідь» з розмітки .faq-item. Кнопки-посилання
    всередині відповіді (.faq-cta) в текст не потрапляють."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []
        self.mode = None      # 'q' | 'a'
        self.depth = 0
        self.skip = 0
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '') or ''
        if tag == 'div' and 'faq-item' in cls.split():
            self.cur = {'q': [], 'a': []}
        elif self.cur is not None and tag == 'h3' and self.mode is None:
            self.mode = 'q'
        elif self.cur is not None and tag == 'div' and 'faq-a' in cls.split():
            self.mode, self.depth = 'a', 1
        elif self.mode == 'a':
            if tag == 'div':
                self.depth += 1
            if tag == 'a' and 'faq-cta' in cls.split():
                self.skip += 1
            elif self.skip and tag == 'a':
                self.skip += 1
            if tag == 'p' and self.cur['a']:
                self.cur['a'].append(' ')

    def handle_endtag(self, tag):
        if self.mode == 'q' and tag == 'h3':
            self.mode = None
        elif self.mode == 'a':
            if tag == 'a' and self.skip:
                self.skip -= 1
            elif tag == 'div':
                self.depth -= 1
                if self.depth == 0:
                    self.mode = None
                    q = re.sub(r'\s+', ' ', ''.join(self.cur['q']).replace('\xa0', ' ')).strip()
                    ans = re.sub(r'\s+', ' ', ''.join(self.cur['a']).replace('\xa0', ' ')).strip()
                    if q and ans:
                        self.items.append((q, ans))
                    self.cur = None

    def handle_data(self, data):
        if self.cur is None:
            return
        if self.mode == 'q':
            self.cur['q'].append(data)
        elif self.mode == 'a' and not self.skip:
            self.cur['a'].append(data)


def faq_pairs(html_text):
    p = _FaqParser()
    p.feed(html_text)
    return p.items


def set_faq_jsonld(s, lang):
    """Замінює всі ld+json-блоки сторінки FAQ одним: FAQPage + BreadcrumbList."""
    en = lang == 'en'
    base = _SITE + ('/en/faq/' if en else '/faq/')
    home = _SITE + ('/en/' if en else '/')
    title = re.search(r'<title>(.*?)</title>', s).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    pairs = faq_pairs(s)
    if len(pairs) < 10:
        sys.exit('FAQ: знайдено лише %d питань — розбір розмітки зламався' % len(pairs))
    crumb_home, crumb_faq = ('Home', 'Questions and answers') if en else ('Головна', 'Питання і відповіді')
    graph = [
        {'@type': 'FAQPage', '@id': base + '#webpage', 'url': base, 'name': title, 'description': desc,
         'inLanguage': 'en' if en else 'uk-UA',
         'isPartOf': {'@id': _SITE + '/#website'}, 'publisher': {'@id': _SITE + '/#organization'},
         'breadcrumb': {'@id': base + '#breadcrumb'},
         'mainEntity': [{'@type': 'Question', 'name': q,
                         'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]},
        {'@type': 'BreadcrumbList', '@id': base + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': crumb_home, 'item': home},
            {'@type': 'ListItem', 'position': 2, 'name': crumb_faq, 'item': base}]},
    ]
    block = ('<script type="application/ld+json">\n' +
             _json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2) +
             '\n</script>')
    ms = list(_LD.finditer(s))
    if not ms:
        sys.exit('FAQ: немає жодного ld+json-блоку, нікуди вставляти')
    # усі блоки, окрім першого, видаляємо; перший замінюємо
    for m in reversed(ms[1:]):
        s = s[:m.start()] + s[m.end():]
    m = ms[0]
    s = s[:m.start()] + block + s[m.end():]
    return s


def build_faq_ua_jsonld():
    s = io.open(SRC_FAQ, encoding='utf-8').read()
    s = set_faq_jsonld(s, 'uk')
    io.open(SRC_FAQ, 'w', encoding='utf-8').write(s)
    return len(faq_pairs(s))


# ------------------------------------------------------- SEO / head 404
# У 404.html усі адреси абсолютні (файл віддають замість будь-якої
# неіснуючої адреси, тож відносні не працюють). Посилання на головну та її
# розділи build_404() переводить на /en/ — див. там.
HEAD404 = [
 ('<html lang="uk">', '<html lang="en">'),
 ('<title>Сторінки немає — SILENT</title>', '<title>Page not found — SILENT</title>'),
 ('<meta name="description" content="Сторінки за цією адресою немає. Повертайтесь на головну SILENT — silent disco під ключ у Києві та по Україні.">',
  '<meta name="description" content="There is no page at this address. Head back to the SILENT homepage — full-service silent disco in Kyiv and across Ukraine.">'),
 ('<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="en_US">'),
 ('<meta property="og:title" content="Сторінки немає — SILENT">',
  '<meta property="og:title" content="Page not found — SILENT">'),
 ('<meta property="og:description" content="Сторінки за цією адресою немає. Повертайтесь на головну SILENT.">',
  '<meta property="og:description" content="There is no page at this address. Head back to the SILENT homepage.">'),
]

SWITCH_UA_404 = """    <span class="lang-switch" role="group" aria-label="Мова сайту">
      <span class="lang-cur" aria-current="true">UA</span>
      <a href="/en/" hreflang="en" lang="en">EN</a>
    </span>"""
SWITCH_EN_404 = """    <span class="lang-switch" role="group" aria-label="Site language">
      <a href="/" hreflang="uk" lang="uk">UA</a>
      <span class="lang-cur" aria-current="true">EN</span>
    </span>"""

# ------------------------------------------------------------------- шляхи
# Сторінка лежить на рівень глибше за корінь, тож усі відносні адреси
# піднімаються на крок вище. Абсолютні (http, #, mailto:) не чіпаємо.
PATHS = [
 # Заздалегідь написаний текст у посиланні Telegram: кирилиці в ньому немає
 # (відсоткове кодування), тож assert_translated його не спіймав би.
 ('?text=%D0%9F%D1%80%D0%B8%D0%B2%D1%96%D1%82%21%20%D0%A5%D0%BE%D1%87%D1%83%20%D0%B4%D1%96%D0%B7%D0%BD%D0%B0%D1%82%D0%B8%D1%81%D1%8F%20%D0%B1%D1%96%D0%BB%D1%8C%D1%88%D0%B5%20%D0%BF%D1%80%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%BD%D1%8F%20SILENT%20DISCO%20%D0%B4%D0%BB%D1%8F%20%D0%BC%D0%BE%D1%94%D1%97%20%D0%BF%D0%BE%D0%B4%D1%96%D1%97.', '?text=Hi%21%20I%20would%20like%20to%20know%20more%20about%20running%20a%20SILENT%20DISCO%20at%20my%20event.'),
 ('href="assets/site.css"', 'href="../assets/site.css"'),
 ('src="assets/site.js"',   'src="../assets/site.js"'),
 ('src="assets/vendor/',    'src="../assets/vendor/'),
 ('href="images/',  'href="../images/'),
 ('src="images/',   'src="../images/'),
 # data-poster ПЕРЕД звичайним poster=: рядок "poster=\"images/" — це
 # підрядок "data-poster=\"images/", тож у зворотному порядку перше правило
 # вже підмінило б усі data-poster, і друге не знайшло б свій текст.
 ('data-poster="images/', 'data-poster="../images/'),
 ('poster="images/', 'poster="../images/'),
 ('data-video="video/',   'data-video="../video/'),
 ('src="video/',    'src="../video/'),
 ("url('images/",  "url('../images/"),
]

# /experiences/ → /en/experiences/, але НЕ /experiences/corporate/: його англійської версії немає.
EXP_LINK = re.compile(r'href="/experiences/(?!corporate)')

# --------------------------------------------------------------- перемикач
SWITCH_UA = """    <span class="lang-switch" role="group" aria-label="Мова сайту">
      <span class="lang-cur" aria-current="true">UA</span>
      <a href="en/" hreflang="en" lang="en">EN</a>
    </span>"""
SWITCH_EN = """    <span class="lang-switch" role="group" aria-label="Site language">
      <a href="../" hreflang="uk" lang="uk">UA</a>
      <span class="lang-cur" aria-current="true">EN</span>
    </span>"""

# ------------------------------------------------------------------- рядки
# Ключ — точний рядок з index.html, значення — переклад. Порядок тут довільний:
# застосовуються від найдовших до найкоротших, щоб короткий рядок не з'їв
# частину довшого.
T = {
'Домашні вечірки': 'House parties',
'Квартира, будинок або дача: гості танцюють до ранку, а за стіною нічого не чути. Без розмов із сусідами наступного дня.': 'A flat, a house or a country place: guests dance until morning and nothing is heard through the wall. No conversations with the neighbours the next day.',
'Майстеркласи': 'Hands-on workshops',
'Руки зайняті роботою, а інструкції чути просто у вусі. Ведучий не перекрикує шум майстерні й не збирає всіх довкола себе.': 'Hands are busy with the work while the instructions come straight into the ear. The host does not shout over the workshop noise or gather everyone around.',
'Забіги та прогулянки': 'Runs and walks',
'Група рухається містом або парком, і голос гіда чи тренера доходить до кожного — навіть до тих, хто відстав на сотню метрів.': 'The group moves through the city or a park and the voice of the guide or coach reaches everyone, including those a hundred metres behind.',
'Табори та молодіжні збори': 'Camps and youth gatherings',
'Медитація': 'Meditation',
'Драйв-ін формат': 'Drive-in format',
'Від тихої вечері з друзями до вечірки на всю ніч: гучність і канал під настрій кожного гостя.': 'From a quiet dinner with friends to a party that runs all night: volume and channel to suit every guest.',
'Голос інструктора чи ведучого просто у вусі, музика — на власній гучності. Йога, медитація, ecstatic dance: ніщо не збиває з практики.': 'The instructor or guide speaks right into your ear, the music sits at your own volume. Yoga, meditation, ecstatic dance: nothing breaks the practice.',
'Двір, дах, парк чи майданчик для авто — звук у навушниках, тиша навколо. Фільм до ночі без питань від сусідів і без звукової інфраструктури.': 'A yard, a roof, a park or a car lot: the sound is in the headphones and everything around stays quiet. A film until late with no questions from the neighbours and no sound rig at all.',
'Забіги, фітнес, тренування, розминки: команда чує тренера, а не вітер і вуличний шум, навіть коли група велика.': 'Runs, fitness, training, warm-ups: the group hears the coach rather than the wind and the street, even when the class is large.',
'Ранкові розминки, тихі години роздумів, командні ігри й вечірня дискотека — один комплект на всі активності зміни.': 'Morning warm-ups, quiet hours of reflection, team games and an evening disco: one kit for every activity of the session.',
'Синхронний переклад': 'Simultaneous translation',
'Доповідач говорить однією мовою, гість чує свою: кожен канал — окремий переклад, без кабін і роздачі приймачів по залу.': 'The speaker talks in one language, the guest hears their own: each channel carries a separate interpretation, with no booths and no receivers handed around the hall.',
'Тренінги й навчання': 'Training sessions',
'Голос тренера однаково чути в кожній групі. Кілька вправ ідуть паралельно в одному залі й не заважають одна одній.': 'The trainer is heard equally in every group. Several exercises run in parallel in one room without getting in each other’s way.',
'Виставки та експо': 'Expos and trade shows',
'Кожен стенд отримує власний канал. Відвідувач обирає, кого слухати, і в павільйоні не стоїть суцільний гул.': 'Every stand gets its own channel. Visitors choose who to listen to, and the hall is free of the usual wall of noise.',
'Медитація': 'Meditation',
'Голос ведучого й музика йдуть просто у вуха. Зовнішні звуки не збивають, і кожен ставить свою гучність.': 'The guide’s voice and the music go straight into the ears. Outside sounds do not intrude, and everyone sets their own volume.',
'Бар-тури': 'Bar tours',
'Компанія рухається між локаціями зі своєю музикою. Вечірка не закінчується на порозі закладу.': 'The group moves between venues with its own music. The party does not stop at the door.',
'Готелі й ресорти': 'Hotels and resorts',
'Вечірка біля басейну чи на терасі, яка не будить гостей у номерах і не впирається в години тиші.': 'A party by the pool or on the terrace that does not wake guests in their rooms or run into quiet hours.',
'Дівич-вечір': 'Bachelorette party',
'Свій плейлист у навушниках і можливість говорити звичайним голосом, не перекрикуючи музику.': 'Your own playlist in the headphones, and the option to talk in a normal voice instead of shouting over the music.',
'Стендап і комедія': 'Stand-up and comedy',
'Кожне слово доходить до останнього ряду. Реакція залу не глушить наступну репліку.': 'Every word reaches the back row. The room’s laughter does not drown the next line.',
'Модні покази': 'Fashion shows',
'Саундтрек показу звучить у навушниках гостей, а коментар — окремим каналом для преси.': 'The show soundtrack plays in the guests’ headphones, with commentary on a separate channel for the press.',
'Танцювальні змагання': 'Dance competitions',
'Кожна команда репетирує під свою музику в одному залі. Треки не накладаються.': 'Each team rehearses to its own music in the same hall. The tracks do not collide.',
'Бренд-активації': 'Brand activations',
'Звукова зона на фестивалі, у ТРЦ чи на вулиці — без узгодження гучності з майданчиком.': 'A sound zone at a festival, in a mall or on the street, with no volume to negotiate with the venue.',
'Дитячі свята': 'Kids’ parties',
'Гучність під вік кожної дитини. Нікого не лякає надто голосна музика, а батьки поруч чують одне одного.': 'Volume set to each child’s age. No one is startled by music that is too loud, and parents nearby can still hear each other.',
'Події для літніх': 'Events for older guests',
'Голос ведучого просто у вусі й власна гучність. Чути добре навіть тим, кому заважає гул зали.': 'The host’s voice right in the ear and volume set by each guest. Those who struggle with room noise can still hear well.',
'Квести': 'Quests',
'Команди отримують підказки кожна у свій канал. Гра йде в одному просторі, але ніхто не чує чужих відповідей.': 'Each team gets its clues on its own channel. The game runs in one space, yet no one overhears another team’s answers.',
'Гра «Імпостер»': 'The Impostor game',
'Один канал звучить інакше за решту, і команді треба вирахувати, хто його слухає. Гра вбудована в саме обладнання.': 'One channel plays something different from the rest, and the team has to work out who is listening to it. The game is built into the equipment itself.',
'Натискаючи, ви погоджуєтесь, що ми зв’яжемося з вами щодо події. Якщо ви заповните контакт і не надішлете заявку, введене теж зберігається — ':
 'By sending this you agree that we may contact you about your event. If you fill in a contact and do not send the request, what you typed is still saved — ',
'як саме, написано в політиці': 'the privacy policy explains how',
'Політика конфіденційності': 'Privacy policy',
'Написати нам у Telegram': 'Message us on Telegram',
'Написати нам': 'Message us',
# --- меню й підвал -------------------------------------------------------
'Перейти до вмісту': 'Skip to content',

# --- вікно після надсилання заявки ----------------------------------------
'Заявку прийнято': 'Request received',
'Дякуємо. Напишемо вам, щойно перевіримо дату — відповідаємо протягом дня.':
  'Thank you. We will write as soon as we have checked the date, and we answer within the day.',


# --- сторінка 404 --------------------------------------------------------
'Помилка 404': 'Error 404',
'Тут тиша — і цього разу не тому, що ми так задумали.':
  "It's quiet here — and this time we didn't plan it that way.",
'Сторінки за цією адресою немає. Схоже, посилання застаріло або в адресі загубився символ. Решта сайту на місці.':
  'There is no page at this address. The link has probably gone stale, or a character got lost on the way. The rest of the site is where you left it.',
'На головну': 'Go to the homepage',
'Розділи сайту': 'Site sections',

'На початок сторінки': 'Back to top',
'Нагору сторінки': 'Back to top',
'Як це працює': 'How it works',
'Що входить': "What's included",
'Сценарії': 'Scenarios',
'Ціна': 'Pricing',
'Питання': 'FAQ',
'Тихі враження': 'Quiet Experiences',
'Усі формати': 'All formats',
'Бізнес': 'Business',
# Фільтр тем над «Silent-досвідами». «Усі» окремим словом небезпечно: ключ
# зачепив би «Усі формати» й будь-яке речення, тож беремо разом із розміткою.
'>Усі <span>': '>All <span>',
'Теми форматів': 'Format themes',
'Свята': 'Celebrations',
'Для дітей': 'For kids',
'Навчальні заклади': 'Schools',
'Церкви й табори': 'Churches & camps',
'Культура': 'Culture',
'Спорт': 'Sport',
'Міські події': 'City events',
'Церковні служби': 'Church services',
'Молодіжні табори': 'Youth camps',
'Про формат': 'About the format',
'Організація та логістика': 'Logistics & setup',
'Ціна та бронювання': 'Pricing & booking',
'Оплата й умови': 'Payment & terms',
'Дослідити всі питання': 'Explore all questions',
'Усе про SILENT — заздалегідь': 'Everything about SILENT — in advance',
'Одна технологія, десятки форматів.': 'One technology, dozens of formats.',
'Обирайте свій.': 'Pick yours.',
'Перш ніж бронювати.': 'Before you book.',
'Прочитайте це.': 'Read this.',
'Формат, організація, ціна, обладнання, умови — коротко й по суті.': 'Format, logistics, pricing, equipment, terms — short and to the point.',
'Формат, організація, ціна, обладнання, умови.': 'Format, logistics, pricing, equipment, terms.',
'Не знайшли своє питання серед прикладів?': "Don't see your question in the examples?",
'Що таке silent disco?': 'What is silent disco?',
'Чи потрібен діджей?': 'Do we need a DJ?',
'Скільки часу займає встановлення?': 'How long does setup take?',
'Виїжджаєте за межі Києва?': 'Do you travel outside Kyiv?',
'Скільки коштує silent disco?': 'How much does silent disco cost?',
'Як забронювати дату?': 'How do I book a date?',
'Скільки музичних каналів?': 'How many music channels?',
'Скільки тримає заряд навушників?': 'How long does the headphone battery last?',
'Яка схема оплати?': "What's the payment schedule?",
'Чи можна перенести дату?': 'Can I reschedule the date?',
'Кому підходить формат?': 'Who is this format for?',
'Що підготувати з нашого боку?': 'What do we need to prepare?',
'Що входить у вартість?': "What's included in the price?",
'Скільки навушників замовити?': 'How many headphones to order?',
'Хто відповідає за навушники?': 'Who is responsible for the headphones?',
'Чим це відрізняється від колонок?': 'How is this different from speakers?',
'Можна на вулиці чи в дощ?': 'Can it be outdoors or in the rain?',
'Це остаточна сума?': 'Is this the final amount?',
'Чи заважають спілкуватись?': 'Do they get in the way of talking?',
'Чи потрібен депозит?': 'Is a deposit required?',
'Всі гості чують одну музику?': 'Do all guests hear the same music?',
'За скільки бронювати дату?': 'How far ahead to book a date?',
'Що впливає на ціну?': 'What affects the price?',
'Чи потрібне живлення?': 'Does it need a power source?',
'Що при скасуванні?': 'What if I need to cancel?',
'Всі питання': 'All questions',
'Це справді весело?': 'Is it actually fun?',
'Скільки триває подія?': 'How long does the event last?',
'Скільки коштують опції?': 'How much do the extras cost?',
'Що як загублять навушники?': 'What if headphones get lost?',
'Хто платить за поломку?': 'Who pays if something breaks?',
'Форс-мажор і безпека': 'Force majeure & safety',
'Що робити, якщо обладнання дасть збій?': 'What if the equipment fails?',
'Хто відповідає за музику на події?': 'Who is responsible for the music?',
'Що буде через форс-мажор?': 'What happens in a force majeure event?',
'Чи можна перенести через погоду?': 'Can we reschedule due to weather?',
'Хто відповідає за безпеку на заході?': 'Who is responsible for event safety?',
'Чи потрібен паперовий підпис?': 'Do we need a paper signature?',
'Як можна оплатити?': 'How can I pay?',
'Перевірити дату': 'Check a date',
'Перевірити доступність дати': 'Check if your date is free',

# --- hero ----------------------------------------------------------------
'Silent Disco під ключ': 'Full-service silent disco',
'Сайлент Диско в навушниках': 'Silent disco in headphones',
'Сайлент Диско': 'Silent disco',
'Тиха вечірка під ключ': 'Full-service quiet party',
'12 000 грн': '12,000 UAH',
'40 гостей': '40 guests',
'Київ та Україна': 'Kyiv and across Ukraine',
'від <b>': 'from <b>',
'три хвилі музики —': 'three waves of music —',
'ви обираєте <span class="accent-lime">свою</span>': 'you pick <span class="accent-lime">yours</span>',
'Три канали звучать паралельно в'+NB+'навушниках кожного гостя. Хтось танцює під хаус, хтось під поп'+NB+'— і'+NB+'всі поруч, в'+NB+'одному залі.':
  "Three channels play at the same time in every guest's headphones. Some dance to house, some to pop — and all of them side by side, in the same room.",

'Оберіть канал': 'Pick a channel',
'Увімкнути звук': 'Turn sound on',
'Deep &amp; Dance — електроніка, хаус, ритм': 'Deep &amp; Dance — electronic, house, rhythm',
'Pop &amp; Throwback — хіти, під які всі знають слова': 'Pop &amp; Throwback — the hits everyone knows the words to',
'Chill &amp; Soul — повільне, тепле, близьке': 'Chill &amp; Soul — slow, warm, close',

# --- чому silent disco ---------------------------------------------------
'Чому silent disco': 'Why silent disco',
'Звичайна вечірка змушує обирати за всіх. Ця — дає обрати кожному.':
  'An ordinary party makes you choose for everyone. This one lets everyone choose.',
'Чорно-білий кадр: сцена з колонками і темна зала глядачів':
  'Black-and-white shot: a stage with speakers and a dark room of guests',
'Як зазвичай': 'The usual way',
'Ти підлаштовуєшся під вечір': 'You adjust to the night',
'Музику обирають за всіх. Якщо вона «не твоя» — залишається або терпіти, або йти. Комусь голосно, комусь нудно, комусь просто не хочеться танцювати.':
  "The music is picked for everyone. If it's not your thing, you either put up with it or leave. It's too loud for some, boring for others, and some just don't feel like dancing.",
'Компанія друзів сміється у світних зелених навушниках':
  'A group of friends laughing in glowing green headphones',
'Із silent disco': 'With silent disco',
'Вечір підлаштовується під тебе': 'The night adjusts to you',
'Ніхто не мусить підлаштовуватись. Три канали — і кожен обирає свій настрій. Танцюй, говори, відпочивай, перемикайся — і залишайся частиною спільної події. Разом, але по-своєму.':
  'Nobody has to adjust. Three channels, and everyone picks their own mood. Dance, talk, rest, switch — and still be part of the same night. Together, your own way.',

# --- як це працює --------------------------------------------------------
'Як насправді влаштована тиха вечірка?': 'How does a quiet party actually work?',
'Музика йде не з колонок, а одразу в навушники кожного гостя. Один передавач роздає три канали, і людина сама обирає, який слухати і на якій гучності. Колонок немає, тож ззовні залишається тиша. Ми привозимо навушники із запасними комплектами, збираємо систему на місці й лишаємось на вечір. Від вас потрібні тільки дата й приблизна кількість гостей. Працюємо в Києві й виїжджаємо по всій Україні.':
  "The music doesn't come from speakers — it goes straight into every guest's headphones. One transmitter carries three channels, and each person chooses which one to listen to and how loud. There are no speakers, so outside it stays quiet. We bring the headphones with spare sets, assemble the system on site and stay for the evening. All we need from you is a date and a rough number of guests. We work in Kyiv and travel anywhere in Ukraine.",
'Заявка': 'Request',
'Дата, місце, гості': 'Date, venue, guests',
'Форма займає хвилину': 'The form takes a minute',
'Дзвонити не обов’язково': 'No phone call needed',
'Розрахунок': 'Quote',
'Рахуємо вартість': 'We work out the cost',
'Відповідаємо протягом дня': 'We reply the same day',
'Ціна залежить від дати й тривалості': 'The price depends on the date and the hours',
'Монтаж': 'Setup',
'Ми приїжджаємо': 'We arrive',
'Близько 30 хвилин до старту': 'About 30 minutes before the start',
'Показуємо, як перемикати канали': 'We show you how to switch channels',
'Вечірка': 'The party',
'Ви танцюєте': 'You dance',
'Гості перемикають канали самі': 'Guests switch channels themselves',
'Демонтаж і вивіз на нас': 'Teardown and pickup are on us',

# --- досвід гостя --------------------------------------------------------
'Досвід гостя': 'The guest experience',
'Що відчують ваші гості на танцполі.': 'What your guests will feel on the dancefloor.',
'Три канали одночасно': 'Three channels at once',
'RED, GREEN, BLUE звучать паралельно. У кожного гостя — свій ефір, і всі танцюють в одному залі.':
  'RED, GREEN and BLUE play in parallel. Every guest gets their own broadcast, and everyone dances in the same room.',
'Кожен обирає свій настрій': 'Everyone picks their own mood',
'Драйв, хіти чи повільне — гість перемикає канал одним дотиком і залишається там, де йому добре.':
  'High energy, big hits or something slow — a guest switches channel with one tap and stays where it feels good.',
'Особиста гучність': 'Personal volume',
'Кожен виставляє звук під себе. Ніхто не виходить із дзвоном у вухах — комфортно й дітям, і старшим.':
  'Everyone sets the level for themselves. Nobody leaves with ringing ears — it suits children and older guests alike.',
'Можна нормально спілкуватися': 'You can actually talk',
'Навушники на шию — і розмова йде звичайним голосом. Без «що?» і «повтори!» крізь гуркіт колонок.':
  'Headphones down to the neck and the conversation runs at a normal voice. No “what?” or “say that again!” over booming speakers.',
'LED-візуал у кожному кадрі': 'LED visuals in every shot',
'Підсвітка на кожному гості перетворює зал на готову картинку. Фото й відео виходять яскравими без окремого світлового обладнання.':
  'The glow on every guest turns the room into a ready-made picture. Photos and video come out bright with no separate lighting rig.',
'Формат, якого ще не бачили': "A format they haven't seen before",
'Танці «в тиші» — незвичне відчуття вже з перших хвилин. Гості проводять час не так, як на звичайній вечірці.':
  "Dancing “in silence” feels unfamiliar from the first minutes. Guests spend the evening in a way they simply don't at an ordinary party.",

# --- що входить ----------------------------------------------------------
'Що саме ви отримуєте за свої гроші.': 'Exactly what you get for your money.',
'Silent disco під ключ — комплект обладнання, логістика й супровід у межах однієї послуги.':
  'Full-service silent disco — the equipment, the logistics and the on-site support all within one service.',
'Обладнання': 'Equipment',
'Від 40 бездротових навушників з\xa0LED-підсвіткою, три канали грають одночасно. Передавачі та\xa0запасні навушники в\xa0комплекті.':
  'From forty wireless headphones with LED backlighting, three channels playing at once. Transmitters and spare headphones included.',
'Доставка й монтаж': 'Delivery and setup',
'Приїжджаємо заздалегідь, збираємо систему й\xa0перевіряємо сигнал ще\xa0до\xa0першого гостя\xa0— вам не\xa0треба цим перейматися.':
  "We arrive early, assemble the system and check the signal before your first guest — you don't need to worry about it.",
'Підготовлені плейлисти': 'Playlists prepared in advance',
'Три готові плейлисти під настрій вечора. DJ можна не\xa0наймати\xa0— музика вже підібрана.':
  'Three playlists ready for the evening’s mood. Skip the DJ — the music is already sorted.',
'Супровід і демонтаж': 'On-site support and teardown',
'Весь вечір поруч\xa0— стежимо за\xa0технікою. Наприкінці забираємо все самі, вам нічого не\xa0лишається робити.':
  'We stay all evening, watching the equipment. At the end we pack everything up ourselves — nothing left for you to do.',
'Короткий reels': 'A short reel',
'Короткий ролик вечора\xa0— можна одразу викласти в\xa0сторіз.':
  'A short clip of the evening — ready to post straight to stories.',
'у базовій ціні': 'in the base price',
'за бажанням': 'optional',
'Окремо орендувати колонки чи\xa0підсилювачі не\xa0треба\xa0— цей комплект закриває весь звук вечора.':
  "No need to rent speakers or amps separately — this kit covers the whole evening's sound.",

# --- галерея -------------------------------------------------------------
'Атмосфера події, гортайте вбік': 'Event atmosphere, scroll sideways',
'Атмосфера': 'Atmosphere',
'SILENT звучить однаково в залі й на даху, в музеї й під небом.':
  'SILENT sounds the same in a hall or on a rooftop, in a museum or under open sky.',
'Гортайте вбік, щоб побачити більше кадрів': 'Scroll sideways for more shots',
'Попередні кадри': 'Previous shots',
'Наступні кадри': 'Next shots',
'Дивитися відео: ': 'Watch video: ',
'ДИВИТИСЯ · ДИВИТИСЯ · ДИВИТИСЯ · ': 'WATCH · WATCH · WATCH · WATCH · ',
'Навушники для гостей на вході': 'Headphones waiting for guests at the entrance',
'Гості танцюють у червоному світлі': 'Guests dancing in red light',
'Дискокуля над залою': 'A mirror ball above the room',
'Ряди навушників перед подією': 'Rows of headphones before the event',
'Танці серед колон': 'Dancing between the columns',
'Юрба перед сценою': 'A crowd in front of the stage',
'Вечірка за склом, тиша назовні': 'A party behind glass, silence outside',
'Пара в обіймах серед гостей': 'A couple holding each other among the guests',
'Біля бару, кожен у своїх навушниках': 'At the bar, everyone in their own headphones',
'Подруги перепочивають на дивані': 'Friends taking a break on the sofa',
'Танцпол просто неба': 'An open-air dancefloor',
'Щільний танцпол у фіолетовому світлі': 'A packed dancefloor in purple light',
'Розмова в синьому світлі': 'A conversation in blue light',
'Навушник на столі': 'A headset on the table',
'Ранкове тренування на вулиці': 'A morning workout outdoors',
'Святковий стіл у рожевому світлі': 'A celebration table in pink light',
'Кінопоказ просто неба': 'An open-air film screening',
'Повний двір у навушниках': 'A full courtyard in headphones',
'Дівчина танцює серед вогнів': 'A woman dancing among the lights',
'Вечірка на даху над містом': 'A rooftop party above the city',
'Сет на заході сонця': 'A set at sunset',
'Навушник зблизька': 'A headset up close',
'Танці у дворі надвечір': 'Dancing in the courtyard at dusk',
'Гостя озирається на танцполі': 'A guest glancing back on the dancefloor',
'Синє світло над танцполом': 'Blue light over the dancefloor',
'Гості співають разом у синьому світлі': 'Guests singing together in blue light',
'Гостя з коктейлем серед танцполу': 'A guest with a cocktail in the middle of the dancefloor',
'Перший танець молодят': "The newlyweds' first dance",
'Дах із панорамою нічного міста': 'A rooftop with the night city below',
'Захід сонця над пляжним танцполом': 'Sunset over a beach dancefloor',
'Йога-сет на світанку біля моря': 'A sunrise yoga set by the sea',
'Лазери й екран у залі': 'Lasers and a screen in the hall',
'Руки вгору на танцполі': 'Hands in the air on the dancefloor',
'Сервірований стіл із навушниками': 'A laid table with headphones',
'Дві подруги сміються': 'Two friends laughing',
'Лазери над залою в навушниках': 'Lasers over a room in headphones',
'Компанія танцює разом': 'A group dancing together',
'Гості в залі музею': 'Guests in a museum hall',
'Гості співають разом': 'Guests singing together',
'Гостя вибирає свій канал': 'A guest choosing her channel',
'Повний двір гостей': 'A courtyard full of guests',

# --- silent-досвіди ------------------------------------------------------
'Silent-досвіди': 'Silent experiences',
'Silent disco — це лише один зі сценаріїв. Тихий звук працює всюди, де важливо чути.':
  'Silent disco is only one of the scenarios. Quiet sound works anywhere it matters to hear.',
'Одна технологія — десятки форматів. Від приватних свят і весілля до екскурсії музеєм: гортайте нижче й дивіться, що вже можна зробити.':
  'One technology, dozens of formats. From private celebrations and weddings to a museum tour: scroll on and see what is already possible.',
'Сценарії подій, гортайте вбік': 'Event scenarios, scroll sideways',
'Замовити цей досвід': 'Book this experience',
'Гортайте вбік, щоб побачити всі формати': 'Scroll sideways to see every format',
'Попередні сценарії': 'Previous scenarios',
'Наступні сценарії': 'Next scenarios',
'<option>Весілля</option>': '<option>Wedding</option>',
'Весілля': 'Weddings',
'Гості самі обирають: танцювати чи говорити. Жодного гуркоту на всю залу — і жодних дзвінків від готелю о другій ночі.':
  'Guests choose for themselves: dance or talk. Nothing booming across the room, and no call from the hotel at two in the morning.',
'Кіно просто неба': 'Open-air cinema',
'Двір, дах, парк — звук у навушниках, тиша навколо. Фільм до ночі без питань від сусідів.':
  'A courtyard, a rooftop, a park — sound in the headphones, quiet all around. A film that runs late with no questions from the neighbours.',
'Студентські події': 'Student events',
'Посвята, випускний, вечірка гуртожитку — гучно для своїх і тихо для адміністрації.':
  'Initiations, graduations, a dorm party — loud for your own people and quiet for the administration.',
'Презентація релізу': 'Release listening party',
'Послухайте новий альбом у деталях — разом і водночас особисто. Камерний формат для перших слухачів.':
  'Hear a new album in detail — together and privately at the same time. An intimate format for its first listeners.',
'Драйв-ін формат': 'Drive-in format',
'Майданчик, екран і звук у навушниках — подія там, де немає жодної звукової інфраструктури.':
  'An empty lot, a screen and sound in the headphones — an event where there is no audio infrastructure at all.',
'Музичні коледжі': 'Music colleges',
'Камерне прослуховування студентських програм: чути кожну партію без гучних моніторів у залі.':
  'Intimate listening sessions for student programmes: every part audible without loud monitors in the hall.',
'Фестивалі': 'Festivals',
'Додаткова сцена, яка не конфліктує з головною і не впирається в комендантську годину.':
  "An extra stage that doesn't clash with the main one and doesn't run into curfew.",
'Музеї та галереї': 'Museums and galleries',
'Аудіосупровід, синхронізований із простором. Відвідувач занурюється, не порушуючи тиші зали.':
  'An audio track synced to the space. Visitors get drawn in without breaking the quiet of the room.',
'Благодійні гала': 'Charity galas',
'Аукціон і танці в одному залі. Гості чують ведучого, не борючись із фоновою музикою.':
  'An auction and dancing in the same room. Guests hear the host without fighting the background music.',
'Шкільні свята': 'School events',
'Події та збори коштів, які діти чекають. Без перевантаження звуком у спортзалі.':
  'Events and fundraisers children look forward to. Without overloading the gym with sound.',
'Церковні та молодіжні табори': 'Church and youth camps',
'Ранкові зібрання, тихі години роздумів і вечірні дискотеки — на одному комплекті обладнання.':
  'Morning gatherings, quiet hours for reflection and evening discos — on one set of equipment.',
'Той самий формат у чистому вигляді: три канали, навушники й танцпол, який не заважає нікому навколо.':
  'The format in its purest form: three channels, headphones and a dancefloor that bothers nobody around it.',
'Дні народження': 'Birthdays',
'Від дитячого свята до дорослої вечірки: гучність під вік і настрій кожної компанії.':
  "From a children's party to a grown-up one: volume to match the age and mood of each group.",
'Конференції': 'Conferences',
'Кілька сцен в одному залі й тихі обговорення в групах. Кожен чує свого спікера, не заважаючи сусідній секції.':
  'Several stages in one hall and quiet breakout discussions. Everyone hears their own speaker without disturbing the section next door.',
'Екскурсії': 'Guided tours',
'Гід говорить упівголоса, а чути однаково добре і в першому ряду, і в останньому. Без крику й мегафона.':
  'The guide speaks softly and is heard just as well at the front as at the back. No shouting, no megaphone.',
'Ранкові розминки, командні ігри, вечірня дискотека — один комплект на всі активності зміни.':
  'Morning warm-ups, team games, an evening disco — one kit for every activity of the session.',
'Діджей-сет наживо': 'Live DJ set',
'Резидент або запрошений діджей мікшує просто у ваші навушники — з реакцією на зал.':
  'A resident or guest DJ mixes straight into your headphones, reading the room as they go.',
'Церковні служби та зібрання': 'Church services and gatherings',
'Проповідь і музика звучать чітко для кожного — у залі, у дворі чи на виїзному служінні.':
  'The sermon and the music come through clearly for everyone — in the hall, in the yard or at an outdoor service.',
'Корпоративи': 'Corporate events',
'Формат для тімбілдингу чи корпоративу, у якому команда нарешті розкривається. Працює і в офісі, і в лофті — без узгодження гучності з орендодавцем.':
  'A format for team building or a company party where the team finally opens up. Works in an office or a loft, with no volume to negotiate with the landlord.',
'Йога та ecstatic dance': 'Yoga and ecstatic dance',
'Голос інструктора просто у вусі, музика — на власній гучності. Ніщо не збиває з практики.':
  "The instructor's voice right in your ear, the music at your own volume. Nothing pulls you out of the practice.",
'Камерні концерти': 'Intimate concerts',
'Прослуховування, де чути кожен нюанс виконання. Публіка максимально близько до звуку.':
  'Sessions where every nuance of the performance comes through. The audience as close to the sound as it gets.',
'Інклюзивні події': 'Inclusive events',
'Кожен регулює гучність під себе — подія стає доступною для гостей із сенсорною чутливістю.':
  'Everyone sets their own volume, which makes the event accessible to guests with sensory sensitivities.',
'Громадські зібрання': 'Community gatherings',
'Лекції, покази, зустрічі спільноти — чути кожне слово навіть на відкритому майданчику.':
  'Talks, screenings, community meetings — every word audible even in an open space.',
'Ярмарки та маркети': 'Fairs and markets',
'Музична зона просто серед рядів — гості танцюють, а торгівля поруч іде своїм ходом.':
  'A music zone right among the stalls — guests dance while trading carries on beside them.',
'Іммерсивні театри': 'Immersive theatre',
'Голос акторів і саундтрек звучать просто у вусі глядача. Сцену можна розгорнути навіть просто неба.':
  "The actors' voices and the soundtrack play right in the audience's ear. The stage can be set up even in the open air.",
'Спортивні події': 'Sports events',
'Забіги, тренування, розминки: команда чує тренера, а не вітер і вуличний шум.':
  'Runs, training, warm-ups: the team hears the coach, not the wind and the street noise.',

# --- калькулятор ---------------------------------------------------------
'Калькулятор': 'Calculator',
# Підвал: посилання на сторінки замість дублів якорів головної.
'Для корпоративів': 'Corporate events',
'Питання і відповіді': 'Questions and answers',
'Порахувати вартість': 'Work out the cost',
'Порахуйте бюджет вечора до заявки.': 'Work out the budget for the evening before you enquire.',
'Мінімальне замовлення — 40 навушників на 4 години. Посуньте повзунок і додайте опції, щоб побачити орієнтовний бюджет для вашої події.':
  'The minimum order is 40 headphones for 4 hours. Move the slider and add options to see a rough budget for your event.',
'Навушники SILENT із логотипом і підсвіткою трьох каналів — зеленого, синього та червоного':
  'SILENT headphones with the logo and the three channel colours lit — green, blue and red',
'мінімум навушників': 'headphones minimum',
'базова тривалість': 'base duration',
'музичні канали': 'music channels',
'налаштування на місці': 'setup on site',
'Навушники': 'Headphones',
'Орієнтир': 'Estimate',
'Кількість навушників': 'Number of headphones',
'Тривалість': 'Duration',
'Менше годин': 'Fewer hours',
'Більше годин': 'More hours',
'виїзд по'+NB+'Україні': 'travel across Ukraine',
'короткий reels': 'a short reel',
'дим і'+NB+'світло': 'smoke and lights',
'База 40 навушників / 4 години': 'Base: 40 headphones / 4 hours',
'Додаткові навушники': 'Extra headphones',
'Додаткові години': 'Extra hours',
'Опції': 'Options',
'Ціна за гостя': 'Price per guest',
'Це орієнтир. Фінальна ціна залежить від дати, локації, тривалості та формату — і не є публічною офертою.':
  "This is an estimate. The final price depends on the date, the venue, the hours and the format, and it isn't a public offer.",

# --- гарантія ------------------------------------------------------------
'Наша гарантія': 'Our guarantee',
'Якщо в перші пів години гості не танцюють — знімаємо частину суми.':
  'If nobody is dancing in the first half hour, we take part of the fee off the bill.',
'Ми відповідаємо за результат вечора, тож фінансовий ризик беремо на себе.':
  "We're accountable for how the evening turns out, so we carry the financial risk.",
'Обрати дату': 'Pick your date',

# --- відгуки -------------------------------------------------------------
'Відгуки': 'Reviews',
'Що кажуть ті, хто це відчув.': "What people who've felt it say.",
'Короткі враження людей, які вже мали цей досвід.':
  "Short impressions from people who've already had this experience.",
# Цитати надав власник (29.09.2026); імена, ролі й зірки при них — тимчасові
# заглушки (див. коментар над .tst-wrap в index.html). Ключ цитати — рядок так,
# як він у розмітці (пробіли в ключі зіставляються і зі звичайним, і з
# нерозривним).
'«Ми навіть не уявляли, наскільки це змінить атмосферу. Спочатку всі просто придивлялися, а за кілька хвилин танцювали вже майже всі. Було відчуття, ніби звичайний простір раптом перетворився на зовсім іншу реальність».':
  "“We had no idea how much this would change the atmosphere. At first everyone was just looking around, and a few minutes later almost everyone was dancing. It felt as if an ordinary space had suddenly turned into a completely different reality.”",
'«Я дуже переживав, що гості не зрозуміють формат. Але щойно почалася музика, люди дуже швидко включилися. Навіть ті, хто спочатку просто спостерігав, зрештою одягнули навушники й танцювали разом з усіма».':
  "“I was really worried the guests wouldn't understand the format. But as soon as the music started, people got into it very quickly. Even those who were just watching at first ended up putting on headphones and dancing with everyone else.”",
'«Найбільше сподобалося відчуття свободи. Хтось танцював, хтось спілкувався, хтось перемикав музику — і при цьому всі залишалися частиною однієї вечірки. Кожен проживав цей досвід по-своєму».':
  "“What I liked most was the feeling of freedom. Someone was dancing, someone was chatting, someone was switching the music — and still everyone stayed part of one party. Everyone experienced it in their own way.”",
'«Звичайна гучна вечірка в нашому просторі була неможлива. А тут ми отримали справжню танцювальну атмосферу без шуму навколо. Це було дивне й дуже круте відчуття — бачити людей, які танцюють у майже повній тиші».':
  "“An ordinary loud party was impossible in our space. Here we got a real dance atmosphere without the noise around us. It was a strange and really cool feeling — watching people dance in almost complete silence.”",
'«Я не очікував, що це настільки затягне. Спочатку здається, що ти просто слухаєш музику в навушниках. Але потім помічаєш, як усі навколо танцюють, перемикають канали, сміються — і сам уже повністю всередині цього».':
  "“I didn't expect it to pull me in this much. At first it seems like you're just listening to music in headphones. But then you notice everyone around you dancing, switching channels, laughing — and you're already completely inside it yourself.”",
'«Найцікавіше — кожен чув свою музику, але всі були в одному просторі. Хтось обрав хіти, хтось ретро, хтось зовсім інший настрій. Різні музичні смаки раптом перестали бути проблемою».':
  "“The most interesting part — everyone heard their own music, yet everyone was in the same space. Some picked hits, some retro, some a completely different mood. Different musical tastes suddenly stopped being a problem.”",
'«Спочатку ми думали, що silent disco — це просто навушники замість колонок. Але це виявилося зовсім іншим досвідом. Люди більше взаємодіяли між собою, сміялися, показували одне одному свої канали й постійно були залучені в те, що відбувається».':
  "“At first we thought silent disco was just headphones instead of speakers. But it turned out to be a completely different experience. People interacted with each other more, laughed, showed each other their channels and were constantly engaged in what was going on.”",
'«Це був той формат, після якого гості ще довго обговорювали вечір. Було багато моментів, які неможливо пояснити словами — їх просто потрібно побачити й пережити самому».':
  "“This was the kind of format after which the guests kept talking about the evening for a long time. There were many moments that are impossible to explain in words — you simply have to see and experience them yourself.”",
'«Це була наша перша silent disco, і ми взагалі не знали, чого очікувати. У результаті отримали вечірку, яка відчувалася зовсім не так, як звичайна. Наче всі на якийсь час опинилися в одному спільному досвіді, але кожен проживав його по-своєму».':
  "“This was our first silent disco and we had no idea what to expect. We ended up with a party that felt nothing like an ordinary one. As if everyone had, for a while, ended up in one shared experience, yet each lived it in their own way.”",
'Олена К.': 'Olena K.',
'Дмитро П.': 'Dmytro P.',
'Марина Ц.': 'Maryna Ts.',
'Артем В.': 'Artem V.',
'Ігор М.': 'Ihor M.',
'Софія Р.': 'Sofiia R.',
'Катерина Л.': 'Kateryna L.',
'Богдан Ш.': 'Bohdan Sh.',
'Анна Т.': 'Anna T.',
'організаторка події': 'event organiser',
'організатор події': 'event organiser',
'гостя вечірки': 'party guest',
'гість вечірки': 'party guest',
'Попередні відгуки': 'Previous reviews',
'Наступні відгуки': 'Next reviews',
'Гортайте вбік, щоб побачити більше відгуків': 'Scroll sideways for more reviews',

# --- FAQ -----------------------------------------------------------------
'Питання наперед': 'Questions up front',
'Те, що зазвичай питають перед замовленням.': 'What people usually ask before booking.',
'Скільки місця потрібно на танцполі?': 'How much dancefloor space do we need?',
'Орієнтовно <strong>1 м² на людину</strong> для активних танців, менше — якщо частина гостей сидітиме. Скажіть нам розмір залу й кількість гостей — порахуємо, чи вистачить простору, і порадимо оптимальну кількість навушників.':
  "Roughly <strong>1 m² per person</strong> for active dancing, less if some of the guests will be seated. Tell us the size of the room and the number of guests and we'll work out whether there's enough space, then suggest how many headsets to take.",
'Чи можна на вулиці?': 'Can it be outdoors?',
'Так, але обладнання залежить від живлення і не любить вологу. У дощ або без розетки поруч потрібен запасний план — намет, навіс або перенесення в приміщення. Обговорюємо це заздалегідь, коли дізнаємось локацію.':
  "Yes, but the equipment needs power and doesn't like damp. In rain, or with no socket nearby, you need a backup plan — a tent, a canopy or moving indoors. We work that out in advance, once we know the venue.",
'Це справді тихо ззовні?': 'Is it really quiet from the outside?',
'Гості танцюють, співають і сміються — це не безшумно. Але сумарний шум навіть від сотні людей у навушниках — мала частка того, що дають звичайні колонки. І коли хтось хоче поговорити, він просто знімає навушники на шию і спілкується звичайним голосом.':
  "Guests dance, sing and laugh, so it isn't soundless. But the total noise from even a hundred people in headphones is a small fraction of what ordinary speakers make. And when someone wants to talk, they simply slide the headphones down to their neck and speak at a normal voice.",
'Наскільки довго тримає заряд?': 'How long does the battery last?',
'Навушники працюють <strong>10+ годин</strong> без підзарядки — вистачає на будь-який вечір з запасом. Приїжджаємо із зарядженим комплектом, тож про це можна не думати.':
  "The headphones run <strong>10+ hours</strong> on one charge — enough for any evening with room to spare. We arrive with the kit fully charged, so it isn't something you need to think about.",
'Чи потрібен окремо DJ?': 'Do we need a DJ as well?',
"Не обов'язково. Наймати живого DJ — це окрема стаття витрат, зазвичай суттєва сума за вечір. Ми наперед готуємо три плейлисти під ваш настрій, тож DJ потрібен, лише якщо хочете живий мікс саме на місці.":
  'Not necessarily. Hiring a live DJ is a separate line in the budget, usually a sizeable one for the evening. We prepare three playlists in advance to match your mood, so a DJ is only needed if you want a live mix on the night.',
'Чи підходить для дітей?': 'Is it suitable for children?',
'Так. У кожного гостя — особиста гучність, тож дитячий слух легко вберегти від зайвого звуку. Для подій із малими дітьми радимо одразу обмежити гучність на нижчому рівні — про це подбаємо ще до початку.':
  "Yes. Every guest has their own volume, so it's easy to keep children's hearing away from too much sound. For events with small children we suggest capping the volume lower from the outset — we take care of that before it starts.",
'Як повертаються навушники наприкінці?': 'How do the headphones come back at the end?',
'Ставимо один пункт видачі й повернення на вході, щоб нічого не губилося. При потребі використовуємо просту систему обліку, щоб наприкінці вечора точно знати, що все зібрано — без незручних питань до гостей.':
  'We set up a single hand-out and return point at the entrance so nothing goes astray. If needed we use a simple tracking system, so by the end of the evening we know for certain everything is back — without awkward questions to guests.',
'Що якщо навушники загубляться або пошкодяться?': 'What if headphones get lost or damaged?',
# Відповідь дослівно та сама, що на /faq/ (узгоджена з договором v2.0): стара
# обіцяла заставу щоразу й «покриваємо із застави, без розбирань» — договір
# каже інакше (депозит не обов'язковий, компенсує замовник).
'Таке трапляється на живих вечірках. У комплекті є запасні навушники на заміну, а якщо обладнання не повернули, загубили чи пошкодили — замовник компенсує погоджену вартість одиниці обладнання. Умови такого випадку прописані в договорі до конкретного замовлення.':
  "It happens at real parties. The set includes spare headphones as replacements, and if equipment isn't returned, gets lost or is damaged, the client pays the agreed value of that item. The terms for this are set out in the contract for the specific booking.",

# --- форма ---------------------------------------------------------------
'Перевірте дату <span class="em">своєї</span> події': 'Check the date of <span class="em">your</span> event',
"Залиште заявку — ми зв'яжемося, перевіримо, чи вільна дата, підберемо формат і підтвердимо бронь після узгодження.":
  "Send a request and we'll get in touch, check whether the date is free, work out the format and confirm the booking once it's agreed.",
'Кількість обладнання обмежена, тож дати розбирають наперед':
  'Equipment is limited, so dates get taken well in advance',
"Заявка ні до чого не зобов'язує — це перевірка доступності":
  "A request commits you to nothing — it's an availability check",
'Попередній місяць': 'Previous month',
'Наступний місяць': 'Next month',
'<span>Пн</span><span>Вт</span><span>Ср</span><span>Чт</span><span>Пт</span><span>Сб</span><span>Нд</span>':
  '<span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>',
'Оберіть дату — вона підставиться у форму': 'Pick a date and it will fill the form',
'Як вас звати': 'Your name',
"Ім'я": 'Name',
'Телефон або Telegram': 'Phone or Telegram',
'+380… або @нік': '+380… or @handle',
'Що ви плануєте?': 'What are you planning?',
'Хочу дізнатися ціну': 'I want to know the price',
# Групи в полі «Що ви плануєте?»: наміри й типи подій раніше стояли одним
# списком упереміш.
'Що вас цікавить': 'What you need',
'Тип події': 'Event type',
# Назви перемикачів каналів для читалки екрана (aria-label): без них кнопка
# оголошувалась як «перемикач, натиснуто» без жодного слова, який саме.
'Канал RED': 'Channel RED',
'Канал GREEN': 'Channel GREEN',
'Канал BLUE': 'Channel BLUE',
'Планую подію': "I'm planning an event",
'Шукаю формат для клієнта': 'Looking for a format for a client',
'Хочу обговорити нестандартний сценарій': "I'd like to discuss something out of the ordinary",
'День народження': 'Birthday',
'Корпоратив': 'Company party',
'Випускний': 'Graduation',
'Тімбілдинг': 'Team building',
'Дитяче свято': 'Kids\' party',
'Фестиваль': 'Festival',
'Скільки гостей орієнтовно': 'Roughly how many guests',
'Бажана дата': 'Preferred date',
'Оберіть дату, напр. 15 червня': 'Pick a date, e.g. June 15',
"Як ви про нас дізналися? (необов'язково)": 'How did you hear about us? (optional)',
'Оберіть варіант': 'Choose one',
'Рекомендація': 'Recommendation',
'На події від SILENT': 'At a SILENT event',
'Інше': 'Other',
"Коментар (необов'язково)": 'Comment (optional)',
'Розкажіть більше про подію, побажання щодо локації, часу тощо':
  'Tell us more about the event, the venue you have in mind, the timing and anything else',
'Надіслати заявку': 'Send the request',
"Натискаючи, ви погоджуєтесь, що ми зв'яжемося з вами щодо події.":
  'By sending this you agree that we may contact you about the event.',
'Заявку прийнято ✦': 'Request received ✦',
"Дякуємо! Ми зв'яжемося найближчим часом, щоб узгодити деталі й підтвердити дату вашого вечора.":
  "Thank you. We'll be in touch shortly to agree the details and confirm the date of your evening.",

# --- числа, одиниці, ініціали --------------------------------------------
# Формат числа міняється разом із локаллю: uk-UA ставить нерозривний пробіл
# (12 000), en-US — кому (12,000). Скрипт друкує суми через Intl і зробить це
# сам; тут ті самі числа, але вписані в розмітку руками.
'12 000': '12,000',
'грн': 'UAH',
'<small>шт.</small>': '<small>units</small>',
'<small>год</small>': '<small>hrs</small>',
'<b>4 год</b>': '<b>4 hrs</b>',
'<b>~30 хв</b>': '<b>~30 min</b>',
'<div class="tst-avatar">ОК</div>': '<div class="tst-avatar">OK</div>',
'<div class="tst-avatar">ДП</div>': '<div class="tst-avatar">DP</div>',
'<div class="tst-avatar">МЦ</div>': '<div class="tst-avatar">MT</div>',
'<div class="tst-avatar">АВ</div>': '<div class="tst-avatar">AV</div>',
'<div class="tst-avatar">СР</div>': '<div class="tst-avatar">SR</div>',
'<div class="tst-avatar">ІМ</div>': '<div class="tst-avatar">IM</div>',
'<div class="tst-avatar">КЛ</div>': '<div class="tst-avatar">KL</div>',
'<div class="tst-avatar">БШ</div>': '<div class="tst-avatar">BS</div>',
'<div class="tst-avatar">АТ</div>': '<div class="tst-avatar">AT</div>',

# --- підвал --------------------------------------------------------------
'Ви кажете дату, ми привозимо вечірку. Так просто. Silent disco у Києві та по всій Україні.':
  'You name the date, we bring the party. It\'s that simple. Silent disco in Kyiv and across Ukraine.',
'Залишити заявку': 'Send a request',
'Усі формати': 'All formats',
'Формати для дітей': 'Formats for kids',
'Формати для свят': 'Formats for celebrations',
'Бізнес-формати': 'Business formats',
'Почути канали': 'Hear the channels',
'Про формат': 'About the format',
'Перед замовленням': 'Before you book',
'Про Silent disco': 'About silent disco',
'Київ · виїзд по Україні': 'Kyiv · we travel across Ukraine',
'Написати в Telegram': 'Message on Telegram',
'Для яких подій': 'For any occasion',
'Усі 44 формати': 'All 44 formats',
'Чого очікувати': 'What to expect',
'Пошта': 'Email',
'Пишіть у будь-який месенджер — відповідаємо швидко.':
  'Message us on any of these — we reply quickly.',
'Silent disco під ключ · Київ · 2026': 'Full-service silent disco · Kyiv · 2026',
'Ціни орієнтовні й не є публічною офертою': 'Prices are indicative and not a public offer',

# --- лайтбокс і вікно подяки ---------------------------------------------
'Відео з події': 'Video from the event',
'Пауза або відтворення': 'Pause or play',
'Закрити': 'Close',
'Попереднє відео': 'Previous video',
'Наступне відео': 'Next video',
"Залишайтесь на зв'язку — стежте за майбутніми подіями та кулісами SILENT:":
  'Stay in touch — follow upcoming events and what happens behind the scenes at SILENT:',
}

# ------------------------------------------------- англійський блок рядків
I18N_EN = """<!-- Рядки, які скрипт виводить сам. Усе інше — статичний текст у розмітці
     нижче. Оголошується ДО site.js: той читає window.SILENT_I18N при старті. -->
<script>
window.SILENT_I18N = {
  base: '../',
  locale: 'en-US',
  currency: 'UAH',
  hero: [
    {
      lines: ['Silent Disco:', 'three waves of music —', 'you pick {yours}'],
      mLines: [
        ['Silent Disco:', ''],
        ['three waves', ''],
        ['of music —', ''],
        ['you pick', 'sr'],
        ['{yours}', '']
      ],
      mSub: 'One night, three different dancefloors.',
      sub: "Three channels play at the same time in every guest's headphones. Some dance to house, some to pop — and all of them side by side, in the same room."
    },
    {
      lines: ['Rooftop, flat, {office} —', 'the venue is no', 'longer a limit.'],
      mLines: [
        ['Rooftop, flat,', ''],
        ['{office} — the venue', ''],
        ['is no longer', 'sr'],
        ['a limit.', '']
      ],
      mSub: 'The party goes wherever you say.',
      sub: 'The whole sound system fits into the headphones: no speakers, no acoustic requirements, no negotiating the volume. You choose where the party happens.'
    },
    {
      lines: ['Dance like', '{nobody}', 'can hear you.'],
      mLines: [
        ['Dance like', ''],
        ['{nobody}', 'sr'],
        ['can hear you.', '']
      ],
      mSub: 'Because nobody can — and the night runs as long as you want.',
      sub: 'Because nobody can. Outside it stays quiet, so the evening lasts exactly as long as you want it to, not as long as the clock allows.'
    }
  ],
  sound: { on: 'Sound on', off: 'Turn sound on', mute: 'Turn sound off' },
  calc: {
    outside: 'travel across Ukraine',
    reel: 'a short reel',
    smoke: 'smoke and lights',
    opts: (list) => `, options: ${list.join(', ')}`,
    summary: (qty, hours, opts, total) =>
      `From the calculator: ${qty} headphones, ${hours} hrs${opts}. Estimated budget: ${total} UAH.`,
    note: (qty, hours, total) =>
      `✓ Pulled in from the calculator: <b>${qty} headphones, ${hours} hrs, ~${total} UAH</b>. Check the comment below — you can add to it.`
  },
  uc: {
    order: 'Book this experience',
    count: (n) => `${n} ${n === 1 ? 'format' : 'formats'} in this theme`,
    line: (name) => `Interested in: ${name}.`,
    note: (name) => `✓ Chosen experience: <b>${name}</b>. It is already in the comment below — add any details you like.`
  },
  cal: { foot: 'Date in the form: ' },
  video: { clip: (n) => 'Clip ' + n, prev: 'Previous video', next: 'Next video' },
  form: {
    required: 'Please leave a name and a contact so we can get back to you.',
    contactBad: 'That contact does not look right. Leave a phone number, an @handle or an email so we can reach you.',
    datePast: 'That date has already passed. Pick the nearest one that works, or leave the field empty.',
    sending: 'Sending…',
    netFail: 'Could not send — the connection seems to be gone. Try again or message us on Telegram.',
    checking: (d) => `Checking <b>${d}</b>`
  }
};
</script>
<script src="../assets/vendor/gsap.min.js"></script>
<script src="../assets/vendor/ScrollTrigger.min.js"></script>
<script src="../assets/site.js"></script>"""


# Зіставляємо не буквально: в українському тексті пробіли між прийменником і
# словом нерозривні, а апостроф трапляється і прямий, і типографський. Шукати
# кожен варіант окремо означало б тримати словник у двох-трьох копіях.
def flexible(key):
    out = []
    for ch in key:
        if ch == ' ':
            out.append('[ \u00a0]')
        elif ch in "'\u2019\u02bc":
            out.append("['\u2019\u02bc]")
        else:
            out.append(re.escape(ch))
    return re.compile(''.join(out))


def translate(s):
    # Від найдовших рядків до найкоротших, щоб короткий не з'їв частину довшого.
    # Словник об'єднаний із T_FAQ: питання на головній беруть ДОСЛІВНО ті самі
    # відповіді, що й /faq/ (вартість, що входить, бронювання, перенесення), і
    # тримати їхній переклад у двох місцях означало б, що вони розійдуться.
    merged = dict(T)
    merged.update(T_FAQ)
    for k in sorted(merged, key=len, reverse=True):
        s = flexible(k).sub(lambda m, v=merged[k]: v, s)
    return s


def assert_translated(s, name):
    # Жодної кирилиці поза HTML-коментарями. Коментарі — нотатки для
    # розробника, вони однакові в обох файлах і читачеві не видні.
    check = re.sub(r'<!--[\s\S]*?-->', '', s)
    left = sorted({l.strip() for l in check.split('\n') if re.search(r'[А-Яа-яІіЇїЄєҐґ]', l)})
    if left:
        print('НЕПЕРЕКЛАДЕНЕ у %s (%d рядків):' % (name, len(left)))
        for l in left:
            print('   ', l[:160])
        sys.exit(1)


# ------------------------------------------------------- позначка версії
# Браузер кешує site.css і site.js на 10 хвилин за заголовком GitHub Pages, а
# далі тримає їх за власними міркуваннями. Через це після кожного деплою
# лишалося питання «це вже нова версія чи ще стара?», і відповісти на нього
# можна було тільки жорстким перезавантаженням. Тепер в адресі стоїть перші
# вісім символів хешу самого файла: зміст не змінився — адреса та сама й кеш
# працює як слід; зміст змінився — адреса інша, і браузерові нема що
# підставляти зі старого.
# Версіоновані активи. Іконки тут нарівні зі скриптом і стилями, і потребують
# цього навіть більше: файли замінюють, лишаючи те саме ім'я, а favicon браузери
# тримають у кеші впертіше за будь-що інше — без позначки версії постійний
# відвідувач місяцями бачив би стару.
#
# Шлях шукаємо без початку, тож під правило підпадають усі написання відразу:
# images/…, ../images/… і /images/…
STAMPED = re.compile(
    r'((?:assets/site\.(?:css|js))|(?:assets/vendor/(?:gsap|ScrollTrigger|Flip)\.min\.js))'
    r'(\?v=[0-9a-f]+)?')

# Ключем служить сам шлях, а не розширення. Це не дрібниця: іконок дві, обидві
# .png, і на ключі-розширенні вони мовчки ділили б один хеш — тобто зміна однієї
# збивала б адресу іншої.
STAMPED_FILES = (
    'assets/site.css',
    'assets/site.js',
    'assets/vendor/gsap.min.js',
    'assets/vendor/ScrollTrigger.min.js',
    'assets/vendor/Flip.min.js',
)


def unstamp(text):
    """Прибирає позначку. Потрібно до збірки: PATHS шукає точні рядки
    href="assets/site.css", і з хвостом ?v= вони б не збіглися."""
    return STAMPED.sub(lambda m: m.group(1), text)


def stamp(text, hashes):
    return STAMPED.sub(lambda m: m.group(1) + '?v=' + hashes[m.group(1)], text)


# ------------------------------------------------- стрічка сценаріїв
# Сторінки досвідів показують ті самі картки, що й головна, за винятком власної.
# Тримати їхню копію в кожному файлі означало б, що перша ж правка тексту на
# головній розійдеться з п'ятьма копіями. Тому джерело одне — index.html, а
# сторінка досвіду містить лише маркер із назвою картки, яку треба прибрати.
#
# Коли з'явиться англійська версія цих сторінок, переклад карток заходить саме
# сюди: рядки беруться з того самого T, що й решта сайту.
UC_START = '<!-- UC-STRIP:START'
UC_END = '<!-- UC-STRIP:END -->'
# Сторінка-список використовує ті самі картки, але сіткою, а не стрічкою:
# обгортка .uc-row там зайва, бо нічого не прокручується вбік.
UC_FILTER_START = '<!-- UC-FILTER:START -->'
UC_FILTER_END = '<!-- UC-FILTER:END -->'
UC_GRID_START = '<!-- UC-GRID:START'
UC_GRID_END = '<!-- UC-GRID:END -->'

# Досвіди, у яких уже є власна сторінка. Їхня картка в сітці веде на неї, решта
# лишаються кнопкою, що підставляє формат у заявку. Список росте разом зі
# сторінками — і це єдине місце, де його треба поповнити.
EXPERIENCE_URLS = {
    'Корпоративи': '/experiences/corporate/',
}

# Порядок карток на сторінці-списку. Це НЕ дані про продажі: статистики звернень
# за форматами в нас немає, і вигадувати її не можна. Порядок складено з того,
# що на сайті вже є: типи подій у формі заявки (весілля, день народження,
# корпоратив, випускний, тімбілдинг, фестиваль) і три аудиторії з PRODUCT.md —
# приватна особа, агенція, корпоративний замовник. Спершу ті формати, заради
# яких сюди приходять найчастіше, далі — нішеві.
#
# Це єдине місце, де порядок задається: щоб переставити, досить посунути рядок.
# Формати, яких тут немає, стають у кінець у порядку з index.html.
# Теми фільтра на сторінці-списку. Формат може належати кільком темам одразу:
# табір — це і церква, і діти; екскурсія — і культура, і навчальний заклад.
# Тому лічильник біля назви — це обсяг теми, а не частка від двадцяти шести, і
# сума кнопок навмисно більша за кількість карток.
# Вимога одна: кожен формат має потрапити щонайменше в одну тему, інакше він
# зникне з фільтра. Збірка це перевіряє.
EXPERIENCE_CATEGORIES = [
    ('business',  'Бізнес',            ['Корпоративи', 'Конференції', 'Презентація релізу',
                                        'Благодійні гала',
                                        'Синхронний переклад',
                                        'Тренінги й навчання',
                                        'Виставки та експо',
                                        'Модні покази',
                                        'Бренд-активації',
                                        'Квести',
                                        'Гра «Імпостер»']),
    ('party',     'Свята',             ['Весілля', 'Дні народження', 'Silent disco',
                                        'Діджей-сет наживо', 'Студентські події',
                                        'Бар-тури',
                                        'Готелі й ресорти',
                                        'Дівич-вечір',
                                        'Дитячі свята',
                                        'Гра «Імпостер»',
                                        'Домашні вечірки']),
    ('kids',      'Для дітей',         ['Шкільні свята', 'Дні народження',
                                        'Церковні та молодіжні табори',
                                        'Кіно просто неба',
                                        'Дитячі свята',
                                        'Квести',
                                        'Гра «Імпостер»',
                                        'Табори та молодіжні збори']),
    ('education', 'Навчальні заклади', ['Шкільні свята', 'Студентські події',
                                        'Музичні коледжі', 'Екскурсії',
                                        'Музеї та галереї',
                                        'Синхронний переклад',
                                        'Тренінги й навчання',
                                        'Майстеркласи']),
    ('faith',     'Церкви й табори',   ['Церковні служби та зібрання',
                                        'Церковні та молодіжні табори',
                                        'Табори та молодіжні збори']),
    ('culture',   'Культура',          ['Музеї та галереї', 'Екскурсії', 'Іммерсивні театри',
                                        'Камерні концерти', 'Кіно просто неба', 'Презентація релізу',
                                        'Музичні коледжі',
                                        'Виставки та експо',
                                        'Стендап і комедія',
                                        'Модні покази',
                                        'Танцювальні змагання',
                                        'Драйв-ін формат',
                                        'Майстеркласи']),
    ('sport',     'Спорт',             ['Спортивні події', 'Йога та ecstatic dance',
                                        'Танцювальні змагання',
                                        'Медитація',
                                        'Забіги та прогулянки']),
    ('community', 'Міські події',      ['Фестивалі', 'Громадські зібрання',
                                        'Ярмарки та маркети', 'Інклюзивні події',
                                        'Благодійні гала',
                                        'Бар-тури',
                                        'Готелі й ресорти',
                                        'Бренд-активації',
                                        'Події для літніх',
                                        'Квести',
                                        'Забіги та прогулянки']),
]

# Порядок за популярністю формату, а не за тим, коли картку додали.
# Спирається на три джерела, бо одного вистачило б лише на здогадку:
#   • частки замовлень у Silent Disco Party Rentals (вибірка 3000 бронювань,
#     Північна Америка): дні народження 23%, звичайні вечірки 22%, шкільні
#     події 22%, корпоративи 11%, церковні 4%, весілля 4%, громадські 3%,
#     йога 3%, благодійні 2%, конференції 2%, бар-міцва 2%;
#   • перелік британських прокатів «основне, що замовляють»: весілля, дні
#     народження, корпоративи, школи, будинки для літніх, дівич-вечори, далі
#     фестивалі, церкви, студентські бали, громадські збори коштів;
#   • те, під що тут уже збудована сторінка й тексти.
# Дві свідомі поправки до цифр. Весілля в американській вибірці — 4%, але це
# самовивіз навушників без команди; усі прокати з виїздом називають весілля
# серед головного, тож картка стоїть у першій пʼятірці. Бар-міцва (2%) не має
# українського відповідника — її місце забирають дитячі свята й випускні.
EXPERIENCE_ORDER = [
    'Дні народження',
    'Silent disco',
    'Шкільні свята',
    'Весілля',
    'Корпоративи',
    'Студентські події',
    'Дитячі свята',
    'Фестивалі',
    'Церковні служби та зібрання',
    'Церковні та молодіжні табори',
    'Табори та молодіжні збори',
    'Конференції',
    'Йога та ecstatic dance',
    'Громадські зібрання',
    'Домашні вечірки',
    'Дівич-вечір',
    'Кіно просто неба',
    'Благодійні гала',
    'Екскурсії',
    'Діджей-сет наживо',
    'Ярмарки та маркети',
    'Спортивні події',
    'Тренінги й навчання',
    'Забіги та прогулянки',
    'Музеї та галереї',
    'Камерні концерти',
    'Медитація',
    'Бренд-активації',
    'Майстеркласи',
    'Синхронний переклад',
    'Інклюзивні події',
    'Стендап і комедія',
    'Події для літніх',
    'Бар-тури',
    'Квести',
    'Гра «Імпостер»',
    'Танцювальні змагання',
    'Готелі й ресорти',
    'Виставки та експо',
    'Презентація релізу',
    'Модні покази',
    'Іммерсивні театри',
    'Музичні коледжі',
    'Драйв-ін формат',
]
UC_CARD = re.compile(r'      <article class="uc-card"[\s\S]*?\n      </article>\n')

EXPERIENCE_PAGES = [
    os.path.join('experiences', 'index.html'),
    os.path.join('experiences', 'corporate', 'index.html'),
]


def _link_card(card, name, depth):
    """Картка досвіду, що має власну сторінку, веде на неї замість кнопки."""
    url = EXPERIENCE_URLS.get(name)
    if not url:
        return card
    return card.replace(
        '<button type="button" class="uc-order">Замовити цей досвід</button>',
        '<a class="uc-order" href="%s">Дивитися досвід</a>' % url)


def _categories_of(name):
    """Усі теми формату. Перетини дозволені: табір — і церква, і діти."""
    return [key for key, _title, items in EXPERIENCE_CATEGORIES if name in items]


def _check_categories(cards):
    """Формат без теми зник би з фільтра — це єдине, чого не можна допустити."""
    names = [re.search(r'data-uc="([^"]*)"', c).group(1) for c in cards]
    listed = {n for _k, _t, items in EXPERIENCE_CATEGORIES for n in items}
    orphan = [n for n in names if n not in listed]
    ghost = sorted(n for n in listed if n not in names)
    if orphan:
        sys.exit('формати без теми, вони зникли б із фільтра: ' + ', '.join(orphan))
    if ghost:
        sys.exit('теми називають формати, яких немає в index.html: ' + ', '.join(ghost))


def _filter_markup(cards):
    names = [re.search(r'data-uc="([^"]*)"', c).group(1) for c in cards]
    out = ['        <button type="button" class="exp-chip is-on" data-cat="all" '
           'aria-pressed="true">Усі <span>%d</span></button>' % len(names)]
    for key, title, items in EXPERIENCE_CATEGORIES:
        n = sum(1 for nm in names if nm in items)
        out.append('        <button type="button" class="exp-chip" data-cat="%s" '
                   'aria-pressed="false">%s <span>%d</span></button>' % (key, title, n))
    return '\n'.join(out)


def _check_home_order(home):
    """Два ряди стрічки на головній мусять читатися як один список за рангом.

    Ряди гортаються паралельно, нижній зсунутий на пів картки, тож у кожній
    колонці опиняються сусідні номери: зверху непарні, знизу парні. Якщо
    розкласти 1-22 у верхній ряд, а 23-44 у нижній, відвідувач побачить поруч
    найпопулярніший формат і двадцять третій — порядок буде в коді, але не
    на екрані.
    """
    rank = {n: i for i, n in enumerate(EXPERIENCE_ORDER)}
    body = home[home.index('id="ucGrid"'):home.index('class="uc-nav uc-prev"')]
    rows = body.split('data-row="b"')
    if len(rows) != 2:
        sys.exit('на головній не два ряди карток')
    got = [re.findall(r'data-uc="([^"]+)"', part) for part in rows]
    missing = [n for n in rank if n not in got[0] + got[1]]
    if missing:
        sys.exit('у EXPERIENCE_ORDER є назви, яких немає в index.html: '
                 + ', '.join(missing))
    want = [EXPERIENCE_ORDER[0::2], EXPERIENCE_ORDER[1::2]]
    for i, (g, w) in enumerate(zip(got, want)):
        if g != w:
            bad = next((a for a, b in zip(g + [None], w + [None]) if a != b), None)
            sys.exit('ряд «%s» на головній не за популярністю — збився на «%s»'
                     % ('ab'[i], bad))


def build_home_filter():
    """Фільтр тем над двома рядами «Silent-досвідів» на головній.

    Головна — джерело карток, тож теми (data-cats) проставляються прямо в
    index.html, і вже звідти їх бачить і site.js, і англійська збірка, і
    стрічки сторінок досвідів. Кнопки фільтра — з того самого
    EXPERIENCE_CATEGORIES, що й на інших сторінках: лічильник біля назви не
    може розійтися з картками. Крок ідемпотентний: повторний запуск дає той
    самий файл. Мусить іти ДО build(), бо build() читає index.html.
    """
    path = SRC
    text = io.open(path, encoding='utf-8').read()
    cards = UC_CARD.findall(text)
    if not cards:
        sys.exit('картки сценаріїв не знайдені в index.html')
    _check_categories(cards)

    def stamp_cats(m):
        return '<article class="uc-card" data-cats="%s" data-uc="%s"' % (
            ' '.join(_categories_of(m.group(1))), m.group(1))
    text = re.sub(r'<article class="uc-card"(?: data-cats="[^"]*")? data-uc="([^"]*)"',
                  stamp_cats, text)

    if UC_FILTER_START not in text:
        sys.exit('немає маркера фільтра тем у index.html')
    fh = text.index(UC_FILTER_START) + len(UC_FILTER_START)
    ft = text.index(UC_FILTER_END)
    text = text[:fh] + '\n' + _filter_markup(UC_CARD.findall(text)) + '\n      ' + text[ft:]

    io.open(path, 'w', encoding='utf-8').write(text)
    print('фільтр тем на головній: карток — %d' % len(cards))


def build_experience_strips():
    home = io.open(SRC, encoding='utf-8').read()
    cards = UC_CARD.findall(home)
    if not cards:
        sys.exit('картки сценаріїв не знайдені в index.html')
    _check_categories(cards)
    _check_home_order(home)

    for rel in EXPERIENCE_PAGES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding='utf-8').read()

        grid = UC_GRID_START in text
        start_tag = UC_GRID_START if grid else UC_START
        end_tag = UC_GRID_END if grid else UC_END
        if start_tag not in text:
            sys.exit('немає маркера карток: ' + rel)

        head = text.index(start_tag)
        tail = text.index(end_tag) + len(end_tag)
        marker = text[head:text.index('-->', head) + 3]
        m = re.search(r'exclude="([^"]*)"', marker)
        skip = m.group(1) if m else ''

        depth = '../' * (rel.count(os.sep))
        kept = []
        for c in cards:
            nm = re.search(r'data-uc="([^"]*)"', c)
            nm = nm.group(1) if nm else ''
            if nm == skip:
                continue
            card = _link_card(c.replace('src="images/', 'src="%simages/' % depth),
                              nm, depth)
            # Теми проставляємо завжди, не лише в сітці: сторінка досвіду теж
            # може захотіти фільтр над стрічкою — і тоді дані вже готові, без
            # окремого проходу.
            # У index.html теми вже стоять (build_home_filter), тож спершу
            # знімаємо їх — інакше атрибут задвоївся б.
            card = re.sub(r' data-cats="[^"]*"', '', card, count=1)
            card = card.replace(
                '<article class="uc-card"',
                '<article class="uc-card" data-cats="%s"' % ' '.join(_categories_of(nm)), 1)
            kept.append(card)

        # Порядок скрізь один — за популярністю формату. У сітці це видно
        # відразу: зверху те, заради чого сюди приходять найчастіше. У стрічці
        # менш очевидно, але теж важить: гортати починають зліва, тож перші
        # картки мусять бути найходовіші. Раніше стрічка брала порядок із
        # index.html як є, а там картки лежать через одну по двох рядках —
        # у один ряд це давало 1, 3, 5, … і лише потім 2, 4, 6.
        rank = {n: i for i, n in enumerate(EXPERIENCE_ORDER)}
        kept.sort(key=lambda c: rank.get(
            (re.search(r'data-uc="([^"]*)"', c) or [None, ''])[1], len(rank)))

        inner = ''.join('  ' + ln + '\n' if ln else '\n'
                        for ln in ''.join(kept).split('\n')[:-1])
        if grid:
            body = marker + '\n' + inner + '      ' + end_tag
        else:
            # Обгортка .uc-row обов'язкова: скрипт стрічки шукає саме її, а без
            # неї .uc-grid (flex-column) кладе картки стовпчиком — горизонтальної
            # прокрутки не існує, і сторінка виростає вдвічі.
            body = (marker + '\n'
                    + '        <div class="uc-row" data-row="a">\n'
                    + inner
                    + '        </div>\n'
                    + '        ' + end_tag)
        text = text[:head] + body + text[tail:]

        if UC_FILTER_START in text:
            fh = text.index(UC_FILTER_START) + len(UC_FILTER_START)
            ft = text.index(UC_FILTER_END)
            text = text[:fh] + '\n' + _filter_markup(kept) + '\n      ' + text[ft:]

        io.open(path, 'w', encoding='utf-8').write(text)
        print('картки зібрані: %s — %d, %s%s'
              % (rel, len(kept), 'сітка' if grid else 'стрічка',
                 (', без «%s»' % skip) if skip else ''))


def stamp_files():
    hashes = {}
    for rel in STAMPED_FILES:
        path = os.path.join(ROOT, *rel.split('/'))
        hashes[rel] = hashlib.sha1(io.open(path, 'rb').read()).hexdigest()[:8]
    # Сторінки досвідів теж проходять через версіонування: вони тягнуть той
    # самий site.css і site.js, і без позначки лишалися б зі старими копіями.
    extra = [os.path.join(ROOT, rel) for rel in EXPERIENCE_PAGES]
    extra.append(os.path.join(ROOT, 'privacy', 'index.html'))
    extra.append(os.path.join(ROOT, 'faq', 'index.html'))
    extra.append(DST_FAQ)
    extra.append(DST_EXP)
    for path in [SRC, DST, SRC404, DST404] + extra:
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding='utf-8').read()
        # Спершу рахуємо, потім відкриваємо на запис. Навпаки не можна: open у
        # режимі 'w' обнуляє файл одразу, і будь-яка помилка нижче лишила б на
        # диску порожнечу замість сторінки.
        out = stamp(unstamp(text), hashes)
        io.open(path, 'w', encoding='utf-8').write(out)
    print('версію активів проставлено: ' +
          ', '.join(rel.rsplit('/', 1)[1] + '=' + hashes[rel] for rel in STAMPED_FILES))


def build():
    s = unstamp(io.open(SRC, encoding='utf-8').read())

    for old, new in HEAD + PATHS:
        if s.count(old) < 1:
            sys.exit('немає в index.html: ' + old[:80])
        s = s.replace(old, new)

    s = en_home_jsonld(s)

    if s.count(SWITCH_UA) != 1:
        sys.exit('перемикач мови в меню не знайдено')
    s = s.replace(SWITCH_UA, SWITCH_EN)

    # Меню й футер у index.html спільні з іншими сторінками сайту, тож
    # якорі там абсолютні — /#book, /#price… На англійській головній такий
    # якір вів на УКРАЇНСЬКУ головну: «Check a date» відкривав форму, але
    # вже українською. Тут це розділи тієї самої сторінки. Посилання на
    # /faq/, /experiences/, /privacy/ лишаються як є — англійських версій
    # цих сторінок поки немає.
    s = s.replace('href="/#', 'href="#')
    # Англійська FAQ існує — посилання на неї з англійської головної.
    s = s.replace('href="/faq/', 'href="/en/faq/')
    # Каталог «Тихі враження» теж має англійську версію; сторінка корпоративів —
    # ще ні, її посилання лишаються українськими.
    s = EXP_LINK.sub('href="/en/experiences/', s)

    # блок рядків цілком
    m = re.search(r'<!-- Рядки, які скрипт виводить сам\.[\s\S]*?<script src="\.\./assets/site\.js"></script>', s)
    if not m:
        sys.exit('блок SILENT_I18N не знайдено')
    s = s[:m.start()] + I18N_EN + s[m.end():]

    s = translate(s)

    # hreflang не чіпаємо: обидві сторінки мусять називати ту саму пару, тож
    # трійка посилань з index.html переїжджає сюди дослівно. Змінюється лише
    # canonical — він у кожної сторінки свій.

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    io.open(DST, 'w', encoding='utf-8').write(s)
    assert_translated(s, 'en/index.html')
    print('en/index.html зібрано:', len(s.split('\n')), 'рядків, неперекладеного немає')


def build_404():
    """en/404.html з 404.html — тим самим способом і тим самим словником.

    Окрема функція, а не ще один прохід у build(): у сторінки помилки своя
    голова (noindex, свій title) і свій перемикач мови — з неіснуючої адреси
    він веде на головну іншої мови, а не на її таку саму помилку.
    """
    s = unstamp(io.open(SRC404, encoding='utf-8').read())

    for old, new in HEAD404:
        if s.count(old) < 1:
            sys.exit('немає в 404.html: ' + old[:80])
        s = s.replace(old, new)

    # Головна й її розділи — на англійську головну, а не українську. До
    # заміни перемикача мови: в українському перемикачі 404 посилання на
    # /en/, його регулярка не зачепить, а після заміни там з'явиться
    # href="/" на українську, який саме й мусить лишитись як є.
    s = re.sub(r'href="/(#[^"]*)?"', lambda m: 'href="/en/' + (m.group(1) or '') + '"', s)
    s = s.replace('href="/faq/', 'href="/en/faq/')

    if s.count(SWITCH_UA_404) != 1:
        sys.exit('перемикач мови в 404.html не знайдено')
    s = s.replace(SWITCH_UA_404, SWITCH_EN_404)

    s = translate(s)

    os.makedirs(os.path.dirname(DST404), exist_ok=True)
    io.open(DST404, 'w', encoding='utf-8').write(s)
    assert_translated(s, 'en/404.html')
    print('en/404.html зібрано:', len(s.split('\n')), 'рядків, неперекладеного немає')



# ================================================================ FAQ (en/faq/)
# Та сама схема, що й для головної: en/faq/index.html НЕ редагується руками,
# а збирається з faq/index.html. Правка в українській FAQ → перезапуск цього
# скрипта, інакше дві версії розійдуться.
#
# Власний словник, а не лише спільний T: у T є короткі ключі з головної
# («Ціна», «Обладнання», «Питання»…), і без повних речень FAQ вони
# вихоплювали б шматки з середини відповідей («Equipment одне», «Weddingsм»).
# Тут кожне питання й відповідь — один цілий ключ. Об'єднаний словник
# сортується від найдовших ключів, тож ці повні речення завжди спрацьовують
# раніше за будь-який короткий ключ із T.
#
# Юридичні формулювання (оплата, скасування, перенесення, відповідальність,
# форс-мажор) перекладені дослівно за змістом українських — без нових
# обіцянок. Джерело правди для них — PRODUCT.md, не цей переклад.
SRC_FAQ = os.path.join(ROOT, 'faq', 'index.html')
DST_FAQ = os.path.join(ROOT, 'en', 'faq', 'index.html')

HEAD_FAQ = [
 ('<html lang="uk">', '<html lang="en">'),
 ('<title>Питання і відповіді про SILENT — усе про Silent Disco</title>',
  '<title>Questions and answers about SILENT — everything about silent disco</title>'),
 ('<meta name="description" content="Усе, що зазвичай питають перед замовленням SILENT: формат, організація, ціна, обладнання. Коротко й по суті, без брошурного тону.">',
  '<meta name="description" content="Everything people usually ask before booking SILENT: the format, organising, price, equipment. Short and to the point, no brochure talk.">'),
 ('<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="en_US">'),
 ('<meta property="og:title" content="Питання і відповіді про SILENT">',
  '<meta property="og:title" content="Questions and answers about SILENT">'),
 ('<meta property="og:description" content="Три канали музики в навушниках кожного гостя, гучність у кожного своя, ззовні тиша. Що варто знати перед замовленням.">',
  '<meta property="og:description" content="Three channels of music in every guest\'s headphones, everyone sets their own volume, and it stays quiet outside. What to know before you book.">'),
 ('<meta property="og:url" content="https://silent.org.ua/faq/">',
  '<meta property="og:url" content="https://silent.org.ua/en/faq/">'),
 ('<meta name="twitter:title" content="Питання і відповіді про SILENT">',
  '<meta name="twitter:title" content="Questions and answers about SILENT">'),
 ('<meta name="twitter:description" content="Усе, що зазвичай питають перед замовленням SILENT: формат, ціна, обладнання, умови.">',
  '<meta name="twitter:description" content="Everything people usually ask before booking SILENT: format, price, equipment, terms.">'),
 ('<link rel="canonical" href="https://silent.org.ua/faq/">',
  '<link rel="canonical" href="https://silent.org.ua/en/faq/">'),
]

SWITCH_UA_FAQ = """    <span class="lang-switch" role="group" aria-label="Мова сайту">
      <span class="lang-cur" aria-current="true">UA</span>
      <a href="/en/faq/" hreflang="en" lang="en">EN</a>
    </span>"""
SWITCH_EN_FAQ = """    <span class="lang-switch" role="group" aria-label="Site language">
      <a href="/faq/" hreflang="uk" lang="uk">UA</a>
      <span class="lang-cur" aria-current="true">EN</span>
    </span>"""

# --- Описи карток форматів (оновлено 05.10.2026). Ключ — український текст картки.
T_CARDS = {
'Різні смаки — один танцпол. Кожен обирає свою музику, а всі залишаються частиною однієї вечірки.':
  'Different tastes, one dance floor. Everyone picks their own music, and everyone stays part of the same party.',
'Три канали грають одночасно — три музичні світи в одному просторі. Перемикайся між ними одним рухом.':
  'Three channels play at once — three musical worlds in one space. Switch between them with a single move.',
'Шкільна дискотека чи тематичне свято, яке діти пам’ятатимуть. Танцюють на повну, а в залі тихо.':
  'A school disco or themed party the kids will remember. They dance their hearts out, and the hall stays quiet.',
'Різна музика для різних поколінь — і всі танцюють разом. Свято триває й там, де гучно не можна.':
  "Different music for different generations — and everyone dances together. The party goes on where loud isn't allowed.",
'Три музичні канали — три настрої. Кожен знаходить своє, а команда залишається разом на одному танцполі.':
  'Three music channels, three moods. Everyone finds their own, and the team stays together on one dance floor.',
'Студентські вечірки, випускні та інші події стають яскравішими, коли кожен може обрати свою музику.':
  'Student parties, graduations and other events get brighter when everyone can choose their own music.',
'Плейлисти, підібрані для дітей, і контроль гучності для кожного. Весело, безпечно й комфортно.':
  'Playlists chosen for children and volume control for each of them. Fun, safe and comfortable.',
'Кілька сцен в одному просторі. Перемикайся між музичними світами, не залишаючи танцпол.':
  'Several stages in one space. Switch between musical worlds without leaving the dance floor.',
'Проводьте служіння будь-де — у залі чи просто неба. Проповідь, музика й переклад звучать у навушниках.':
  'Hold your service anywhere — in a hall or outdoors. Sermon, music and interpretation play in the headphones.',
'Ранкова молитва, навчання, спільні активності й вечірня дискотека — один комплект для різних моментів дня.':
  'Morning prayer, teaching, shared activities and an evening disco — one set for different moments of the day.',
'Зарядка, ігри, навчання, дискотека — один комплект навушників для всього дня та різних форматів.':
  'Morning exercise, games, teaching, a disco — one set of headphones for the whole day and different formats.',
'Кілька спікерів чи воркшопів працюють одночасно. Обирай, що слухати, — сесії не заважають одна одній.':
  "Several speakers or workshops run at once. Choose what to listen to — sessions don't get in each other's way.",
'Голос інструктора поруч, музика занурює у власний ритм. Повна концентрація без шуму.':
  "The instructor's voice is close, the music draws you into your own rhythm. Full focus, no noise.",
'Від форумів до публічних дискусій — кожен чує спікера чітко, навіть просто неба й серед міського шуму.':
  'From forums to public debates — everyone hears the speaker clearly, even outdoors and amid city noise.',
'Танцюй до ранку, не турбуючи весь будинок. Музика залишається тільки там, де відбувається ваша вечірка.':
  'Dance till morning without disturbing the whole building. The music stays only where your party is.',
'Один вечір — три настрої. Танцюйте під свій канал і створіть момент лише для вашої компанії.':
  'One evening, three moods. Dance to your own channel and create a moment just for your group.',
'Кіно під зорями без обмежень за гучністю. Екран, нічне небо — і звук фільму прямо у навушниках.':
  "Cinema under the stars with no volume limits. A screen, the night sky — and the film's sound right in the headphones.",
'Від промови та аукціону до музики й танців — один простір легко змінює свій настрій протягом вечора.':
  'From the speech and the auction to music and dancing — one space easily changes its mood through the evening.',
'Голос гіда залишається поруч незалежно від того, де ти в групі. Слухай, дивись і не пропускай жодної історії.':
  "The guide's voice stays close wherever you are in the group. Listen, look and don't miss a single story.",
'Справжній DJ-досвід без обмежень локації. Музика, світло навушників і натовп — атмосфера будь-де.':
  'A real DJ experience with no location limits. Music, glowing headphones and the crowd — atmosphere anywhere.',
'Танцпол між прилавками. Музика для гостей, розмови для продавців — один простір для всіх.':
  'A dance floor between the stalls. Music for guests, conversation for sellers — one space for everyone.',
'Тренер говорить — команда чує. Чіткий звук залишається з кожним учасником, навіть посеред шуму та руху.':
  'The coach speaks — the team hears. Clear sound stays with every participant, even amid noise and movement.',
'Кілька груп в одному просторі. Кожна слухає своє завдання чи лекцію — без звукового хаосу.':
  'Several groups in one space. Each listens to its own task or lecture — without sound chaos.',
'Голос гіда супроводжує всю групу. Неважливо, хто попереду, а хто відстав — ніхто не губить маршрут.':
  "The guide's voice goes with the whole group. It doesn't matter who is in front and who lags behind — no one loses the route.",
'Кожен експонат отримує власну історію. Слухай її у навушниках, зберігаючи тишу навколо.':
  'Every exhibit gets its own story. Listen to it in the headphones while keeping the silence around you.',
'Музика звучить максимально близько. Кожна нота, подих і деталь інструмента залишаються чутними.':
  'The music sounds as close as it gets. Every note, breath and detail of the instrument stays audible.',
'Голос веде тебе всередину, а зовнішній світ відходить на другий план. Твій простір спокою — будь-де.':
  'A voice leads you inward while the outside world fades into the background. Your space of calm — anywhere.',
'Брендові welcome-треки й аудіовставки звучать прямо у вухах аудиторії — чітко й без втрат.':
  "Branded welcome tracks and audio inserts play right in your audience's ears — clearly and without loss.",
'Наступний крок звучить прямо у вухах. Слухай майстра, не відриваючи рук від роботи.':
  'The next step sounds right in your ears. Listen to the master without taking your hands off the work.',
'Одна подія — кілька мов. Кожен обирає свій канал і слухає доповідь зрозумілою мовою.':
  'One event — several languages. Everyone chooses their own channel and listens to the talk in a language they understand.',
'Власна гучність для людей із сенсорною чутливістю, зокрема аутичних. Менше перевантаження.':
  'Individual volume for people with sensory sensitivity, including autistic guests. Less overload.',
'Кожен жарт доходить чисто, навіть коли зал вибухає сміхом. Ніяких пропущених панчлайнів.':
  'Every joke lands cleanly, even when the room erupts in laughter. No missed punchlines.',
'Плейлисти молодості, власна гучність і чіткий звук — щоб кожен міг бути частиною події.':
  'Playlists of youth, individual volume and clear sound — so everyone can be part of the event.',
'Музика переходить разом із вами від бару до бару. Вечірка не закінчується разом із дверима одного закладу.':
  "The music moves with you from bar to bar. The party doesn't end when the door of one venue closes.",
'Підказки й секретні завдання приходять прямо у ваш канал — суперники нічого не почують.':
  'Clues and secret tasks arrive right in your channel — rivals hear nothing.',
'Усі чують одну музику. Один — іншу. Спостерігай, хто реагує не так, і вирахуй зрадника, поки він не видав себе.':
  'Everyone hears the same music. One hears another. Watch who reacts oddly and find the traitor.',
'Три команди. Три треки. Один танцпол. Кожна команда чує свою музику й не збивається з ритму інших.':
  "Three teams. Three tracks. One dance floor. Each team hears its own music and doesn't lose the rhythm because of the others.",
'Від басейну до пляжу й вечірки — Silent працює там, де хочеться, і в будь-який час.':
  'From the pool to the beach and the party — Silent works where you want it, at any time.',
'Кожен стенд може мати власний звуковий канал. Відвідувач слухає саме ту історію, яку обирає.':
  'Every stand can have its own sound channel. The visitor listens to exactly the story they choose.',
'Новий альбом звучить так близько, ніби ти сидиш у студії з артистом. Жодна деталь не губиться.':
  "The new album sounds so close it's as if you were sitting in the studio with the artist. Not a single detail is lost.",
'Музика, кроки й світло зливаються в один ритм. Преса й команда можуть отримувати окремі аудіоканали.':
  'Music, footsteps and light merge into one rhythm. The press and the team can get separate audio channels.',
'Сцена посеред міста, а аудіодоріжка вистави звучить прямо у вухах глядача. Локація не має меж.':
  "The stage is in the middle of the city, while the show's audio track plays in the viewer's ears. No limits on location.",
'Кожна партія звучить окремо. Слухай глибше й розбирай деталі, що губляться в загальному звучанні.':
  'Each part sounds on its own. Listen deeper and pick out details lost in the overall sound.',
'Кіно просто неба без величезних колонок. Машини, екран, нічне небо — і звук прямо у твоїх навушниках.':
  'Open-air cinema without huge speakers. Cars, a screen, the night sky — and the sound right in your headphones.',
}
T.update(T_CARDS)

T_FAQ = {
# --- «Ціна й бронювання»: що буде після заявки
"Що відбувається після того, як я залишу заявку?": "What happens after I submit a request?",
"Заявка на сайті — це запит на перевірку дати: форма займає хвилину, дзвонити не обов'язково. Відповідаємо протягом дня й називаємо суму під вашу дату, тривалість і кількість гостей. Коли деталі узгоджені, дата бронюється, щойно надходить 50% передоплати, а решту 50% сплачуєте до заходу. У день події приїжджаємо заздалегідь, самі збираємо й налаштовуємо все, показуємо, як перемикати канали, а після вечора самі забираємо обладнання.":
  "A request on the site is a request to check the date: the form takes a minute, and you don't have to call. We reply the same day and give you a price for your date, length and guest count. Once the details are agreed, the date is booked as soon as the 50% prepayment arrives, and you pay the other 50% before the event. On the day we arrive ahead of time, set up and configure everything ourselves, show how to switch channels, and collect the equipment ourselves after the evening.",
# --- шапка сторінки
"Головна": "Home",
"Питання і відповіді": "Questions and answers",
"Усе, що ви хотіли спитати": "Everything you wanted to ask",
"Дощ і вулиця, кількість гостей, оплата, перенесення дати — тут усе, про що питають ще до першого дзвінка. Не знайшли свого — напишіть нам, розберемося разом.":
  "Rain and outdoor venues, guest numbers, payment, moving the date — everything people ask before the first call. Can't find yours? Message us and we'll figure it out together.",
"Категорії питань": "Question categories",
# Короткі версії питань для барабана в геро (рядки ведуть на повні питання
# нижче через data-q; повні формулювання перекладені окремо).
"Скільки це коштує?": "How much is it?",
"А якщо дощ?": "What if it rains?",
"Їдете за межі Києва?": "Travel outside Kyiv?",
"Що входить у ціну?": "What's in the price?",
"Кому це підходить?": "Who is it for?",
"Скільки тримає заряд?": "Battery life?",
"Від чого залежить ціна?": "What affects the price?",
"Коли бронювати дату?": "When should we book?",
"Скільки каналів музики?": "How many music channels?",
"Як оплатити?": "How do I pay?",
"</span> Організація</a>": "</span> Logistics</a>",
"</span> Ціна й бронювання</a>": "</span> Pricing & booking</a>",
"Оплата, скасування та відповідальність": "Payment, cancellation & liability",
"Усі питання": "All questions",

# --- 01 формат
"Що таке silent disco?": "What is silent disco?",
"Вечірка, де музика йде не з колонок, а прямо в бездротові навушники кожного гостя. У навушниках одночасно грають три незалежні канали, тож кожен обирає свій — а ззовні лишається тиша.":
  "A party where the music doesn't come from speakers but goes straight into each guest's wireless headphones. Three independent channels play in the headphones at once, so everyone picks their own — and outside it stays quiet.",
"Вечірка, де музика йде не з колонок, а прямо в бездротові навушники кожного гостя. У навушниках три незалежні канали одночасно, тож кожен обирає свій — а ззовні тихо.":
  "A party where the music doesn't come from speakers but goes straight into each guest's wireless headphones. Three independent channels play in the headphones at once, so everyone picks their own — and outside it's quiet.",
"Всі гості чують одну й ту саму музику?": "Do all guests hear the same music?",
"Ні. Три канали грають одночасно, і кожен перемикається сам просто на навушниках, коли захоче — без спільного компромісного плейлиста на весь зал.":
  "No. Three channels play at once, and everyone switches right on their headphones whenever they like — no single compromise playlist for the whole room.",
"Ні. Три канали грають одночасно, і кожен гість перемикається сам просто на навушниках коли захоче — без спільного компромісного плейлиста.":
  "No. Three channels play at once, and each guest switches right on their headphones whenever they like — no shared compromise playlist.",
"Це справді весело, чи це просто незвичний гаджет?": "Is it actually fun, or just an unusual gadget?",
"Перші хвилини гості придивляються — людей у навушниках бачити незвично, доки не вдягнеш їх сам. Але щойно перемикаєш канал на свій смак і бачиш поруч когось у тому самому кольорі підсвітки — це й затягує. Ми настільки в цьому впевнені, що якщо за перші пів години гості не танцюють — знімаємо частину суми. Це наша гарантія, а не порожні слова.":
  "For the first few minutes guests look around — people in headphones look unusual until you put a pair on yourself. But the moment you switch to a channel you like and spot someone nearby glowing the same colour, it pulls you in. We're so sure of it that if nobody is dancing in the first half hour, we take part of the fee off the bill. That's our guarantee, not just words.",
"Не обов'язково. Ми наперед готуємо три плейлисти під формат і настрій вечора, тож живий діджей потрібен лише якщо хочете саме його мікс на місці.":
  "Not necessarily. We prepare three playlists in advance for the format and mood of the night, so a live DJ is only needed if you specifically want their mix on the spot.",
"Кому підходить такий формат?": "Who is this format for?",
"Весіллям, днями народження й випускним так само, як корпоративам і тімбілдингам. Агенції та організатори теж замовляють SILENT під клієнтські події — формат однаково працює і для приватного свята, і для бізнесу.":
  "Weddings, birthdays and graduations just as much as company parties and team-building events. Agencies and organisers also book SILENT for client events — the format works equally well for a private celebration and for business.",
"Чим це відрізняється від вечірки зі звичайними колонками?": "How is it different from a party with regular speakers?",
"Головна відмінність — звук іде не з колонок у залі, а прямо в навушники кожного гостя. Це дає тишу зовні, три незалежні канали одночасно замість одного спільного плейлиста й особисту гучність у кожного гостя.":
  "The main difference is that the sound doesn't come from speakers in the room but goes straight into each guest's headphones. That means quiet outside, three independent channels at once instead of one shared playlist, and personal volume for every guest.",

# --- 02 організація
"За скільки часу бронювати дату?": "How far in advance should we book?",
"Кількість обладнання обмежена, тож популярні дати розбирають наперед. Що раніше залишите заявку, то більше шансів, що бажана дата ще вільна — особливо у високий сезон.":
  "Our equipment is limited, so popular dates get taken well in advance. The earlier you send a request, the better the chance your date is still free — especially in high season.",
"Близько 30 хвилин на збірку й перевірку сигналу до старту. Приїжджаємо заздалегідь, щоб усе було готове до першого гостя.":
  "About 30 minutes to set up and test the signal before the start. We arrive early so everything is ready for the first guest.",
"Що потрібно підготувати з нашого боку?": "What do we need to prepare on our side?",
"Місце для танців і розетку поруч, якщо це приміщення. Решту — навушники, передавачі, налаштування, супровід і вивіз — привозимо й забираємо самі.":
  "Space to dance and a power socket nearby if it's indoors. Everything else — headphones, transmitters, setup, on-site support and removal — we bring and take away ourselves.",
"Хто встановлює обладнання і чи лишається хтось на заході?": "Who sets up the equipment, and does anyone stay during the event?",
"Усе встановлює й налаштовує команда SILENT — підключаємо аудіосистему, перевіряємо сигнал, видаємо навушники. Представник лишається на весь захід для технічного супроводу, а наприкінці сам збирає й перевіряє обладнання.":
  "The SILENT team sets up and configures everything — we connect the audio system, check the signal and hand out the headphones. A representative stays for the whole event for technical support, and at the end packs up and checks the equipment.",
"Можна провести на вулиці чи в дощ?": "Can we do it outdoors or in the rain?",
"Так, але обладнання залежить від живлення і не любить вологу. Без розетки поруч або в дощ потрібен запасний план — намет, навіс або приміщення поруч. Обговорюємо це заздалегідь, щойно дізнаємось локацію.":
  "Yes, but the equipment depends on power and doesn't like moisture. Without a socket nearby, or in the rain, you need a backup plan — a tent, a canopy or an indoor space nearby. We discuss this in advance as soon as we know the location.",
"Так, база в Києві, але виїжджаємо по всій Україні. Напишіть локацію разом із заявкою — порахуємо формат і логістику під неї.":
  "Yes. We're based in Kyiv but travel across Ukraine. Add the location to your request and we'll work out the format and logistics for it.",
"Скільки триває подія і чи можна продовжити?": "How long does the event last, and can it be extended?",
"Базово — 4 години, мінімум на 40 навушників. Додаткові години можна взяти вже при бронюванні — порахуйте орієнтир у калькуляторі на головній сторінці.":
  "The base is 4 hours, with a minimum of 40 headphones. You can add extra hours when booking — get an estimate in the calculator on the home page.",
"Чи потрібно мені самостійно роздавати й збирати навушники?": "Do I have to hand out and collect the headphones myself?",
"Ні, це робить команда SILENT. Один пункт видачі й повернення на вході тримає процес простим, а наприкінці ми самі перевіряємо, що все зібрано.":
  "No, the SILENT team does that. A single pick-up and return point at the entrance keeps it simple, and at the end we check ourselves that everything is back.",

# --- 03 ціна
"Від <strong>12 000 грн</strong> за мінімальний комплект — 40 навушників на 4 години. Далі ціна залежить від кількості навушників, тривалості й опцій — порахуйте свій варіант у калькуляторі на головній сторінці.":
  "From <strong>12,000 UAH</strong> for the minimum set — 40 headphones for 4 hours. Beyond that, the price depends on the number of headphones, the duration and the options — work out your own version in the calculator on the home page.",
"Від 12 000 грн за мінімальний комплект — 40 навушників на 4 години. Далі ціна залежить від кількості навушників, тривалості й опцій.":
  "From 12,000 UAH for the minimum set — 40 headphones for 4 hours. Beyond that, the price depends on the number of headphones, the duration and the options.",
"Що входить у цю вартість?": "What does this price include?",
"У вартість входять: доставка обладнання на локацію, встановлення й налаштування, підключення аудіосистеми, видача навушників гостям, технічний супровід представника SILENT протягом усього заходу, а також збір і вивіз обладнання наприкінці. Це одна послуга під ключ — обладнання лишається власністю SILENT, а не передається вам в оренду.":
  "The price includes delivery of the equipment to the venue, setup and configuration, connecting the audio system, handing out headphones to guests, technical support from a SILENT representative throughout the event, and packing up and removing the equipment at the end. It's a single full-service package — the equipment remains SILENT's property and is not rented out to you.",
"Ціна на сайті — це остаточна сума?": "Is the price on the website final?",
"Ні, це орієнтир. Фінальна ціна залежить від дати, локації, тривалості й формату — і не є публічною офертою. Точну суму назвемо, щойно дізнаємось деталі вашої події.":
  "No, it's a guide. The final price depends on the date, location, duration and format — and is not a public offer. We'll give you the exact amount as soon as we know the details of your event.",
"Як можна оплатити?": "How can I pay?",
"Основний спосіб — безготівковий переказ на рахунок SILENT за реквізитами IBAN. Якщо для вашого замовлення можливі інші варіанти, скажемо про це одразу.":
  "The main way is a bank transfer to SILENT's account using the IBAN details. If other options are possible for your booking, we'll tell you straight away.",
"Залиште заявку на сайті — вкажіть дату, кількість гостей і формат. Після узгодження деталей дата бронюється, щойно надходить 50% передоплати; решта 50% сплачується до самого заходу.":
  "Send a request on the website with the date, the number of guests and the format. Once the details are agreed, the date is booked as soon as the 50% prepayment arrives; the remaining 50% is paid before the event.",
"Що впливає на фінальну ціну?": "What affects the final price?",
"Кількість навушників, тривалість події, дата й локація, а також опції — виїзд по Україні, короткий reels-ролик, дим і світло. 12 000 грн — стартова точка для мінімального комплекту, а не фіксована сума для будь-якого формату.":
  "The number of headphones, the length of the event, the date and location, plus options — travel across Ukraine, a short reel, smoke and lights. 12,000 UAH is the starting point for the minimum set, not a fixed price for every format.",
"Скільки коштують додаткові навушники, години чи опції?": "How much do extra headphones, hours or options cost?",
"Кожен пункт понад мінімум — додаткові навушники, зайві години, виїзд по Україні, reels-ролик, дим і світло — додається до базової ціни. Калькулятор на головній сторінці одразу перераховує суму під ваші параметри, тож точний орієнтир бачите ще до заявки.":
  "Everything beyond the minimum — extra headphones, extra hours, travel across Ukraine, a reel, smoke and lights — is added to the base price. The calculator on the home page recalculates the total for your parameters instantly, so you see an accurate estimate before you even send a request.",

# --- 04 обладнання
"Три — RED, GREEN, BLUE. Кожен канал грає свою музику одночасно з іншими, а навушники світяться кольором обраного каналу, тож з боку видно, хто що слухає.":
  "Three — RED, GREEN, BLUE. Each channel plays its own music at the same time as the others, and the headphones glow in the colour of the chosen channel, so you can see from the side who is listening to what.",
"Три — RED, GREEN, BLUE. Кожен канал грає свою музику одночасно з іншими, а навушники світяться кольором обраного каналу.":
  "Three — RED, GREEN, BLUE. Each channel plays its own music at the same time as the others, and the headphones glow in the colour of the chosen channel.",
"<strong>10+ годин</strong> без підзарядки — вистачає на будь-який вечір із запасом. Комплект приїжджає вже зарядженим, разом із запасними навушниками про всяк випадок.":
  "<strong>10+ hours</strong> without recharging — enough for any night with room to spare. The set arrives fully charged, along with spare headphones just in case.",
"10+ годин без підзарядки — вистачає на будь-який вечір із запасом. Комплект приїжджає вже зарядженим, разом із запасними навушниками про всяк випадок.":
  "10+ hours without recharging — enough for any night with room to spare. The set arrives fully charged, along with spare headphones just in case.",
"Чи потрібне окреме джерело живлення для обладнання?": "Does the equipment need its own power supply?",
"Так, передавачам і техніці потрібна розетка поруч. Якщо подія на вулиці або в місці без електрики — обговорюємо запасний варіант заздалегідь, щойно дізнаємось локацію.":
  "Yes, the transmitters and equipment need a socket nearby. If the event is outdoors or somewhere without electricity, we discuss a backup option in advance as soon as we know the location.",
"Що якщо навушники зламаються чи загубляться під час вечірки?": "What if headphones break or get lost during the party?",
"Таке трапляється на живих вечірках. У комплекті є запасні навушники на заміну, а якщо обладнання не повернули, загубили чи пошкодили — замовник компенсує погоджену вартість одиниці обладнання. Умови такого випадку прописані в договорі до конкретного замовлення.":
  "It happens at real parties. The set includes spare headphones as replacements, and if equipment isn't returned, gets lost or is damaged, the client pays the agreed value of that item. The terms for this are set out in the contract for the specific booking.",
"Скільки навушників можна замовити?": "How many headphones can we order?",
"Мінімум 40, на першому етапі — до 100 навушників і, відповідно, до 100 учасників одночасно. Якщо гостей більше, напишіть кількість у заявці — порадимо, як краще бути.":
  "At least 40, and for now up to 100 headphones — so up to 100 participants at once. If you have more guests, put the number in your request and we'll advise on the best way to handle it.",
"Чи заважають навушники спілкуватися?": "Do the headphones get in the way of talking?",
"Ні. Гучність у кожного своя, тож коли хочеться поговорити — досить зняти навушники на шию й говорити звичайним голосом, поки музика в них тихо грає поряд.":
  "No. Everyone sets their own volume, so when you want to talk, just slip the headphones down around your neck and talk normally while the music keeps playing quietly in them.",

# --- 05 оплата й умови
"50% вартості — передоплата, яка бронює дату; решта 50% — до проведення заходу. Дата вважається підтвердженою одразу після першої частини оплати.":
  "50% of the cost is a prepayment that secures the date; the remaining 50% is paid before the event. The date counts as confirmed as soon as the first part of the payment arrives.",
"Що буде, якщо я захочу скасувати захід?": "What happens if I want to cancel the event?",
"Залежить від того, за скільки днів до події: за 14+ днів повертаємо всю передоплату, за 7–13 днів — половину, менш ніж за 7 днів передоплата не повертається. Напишіть нам, що змінилося, — по можливості шукаємо рішення разом.":
  "It depends on how many days before the event you cancel: 14+ days out, we refund the full prepayment; 7–13 days out, half of it; less than 7 days out, the prepayment is not refunded. Write to us about what has changed — where possible, we look for a solution together.",
"Залежить від того, за скільки днів до події: за 14+ днів повертаємо всю передоплату, за 7-13 днів — половину, менш ніж за 7 днів передоплата не повертається.":
  "It depends on how many days before the event you cancel: 14+ days out, we refund the full prepayment; 7–13 days out, half of it; less than 7 days out, the prepayment is not refunded.",
"Так, безкоштовно — якщо попередити щонайменше за 21 день до заходу і нова дата вільна в календарі. Одне перенесення входить у бронювання, наступні узгоджуємо окремо.":
  "Yes, free of charge — if you let us know at least 21 days before the event and the new date is free in the calendar. One reschedule is included in the booking; any further ones are agreed separately.",
"Не завжди. SILENT може попросити забезпечувальний депозит для конкретного замовлення — потреба і сума узгоджуються заздалегідь і фіксуються в підтвердженні бронювання.":
  "Not always. SILENT may ask for a security deposit for a specific booking — whether it's needed and how much is agreed in advance and set out in the booking confirmation.",
"Хто відповідає за навушники під час заходу?": "Who is responsible for the headphones during the event?",
"Наш представник видає й забирає навушники особисто, тож контроль на місці — наш. Але за втрату чи пошкодження обладнання гостем відповідає замовник — незалежно від того, хто саме з гостей це спричинив.":
  "Our representative hands out and collects the headphones personally, so on-site control is ours. But the client is responsible for any loss of or damage to the equipment caused by a guest — regardless of which guest caused it.",
"Що буде, якщо навушник загублять або пошкодять?": "What happens if a headset is lost or damaged?",
"Замовник компенсує повну погоджену вартість одиниці обладнання — не лише ремонт. Таке обладнання складно оперативно замінити в Україні, тож і для пошкодженого, і для втраченого діє однакова компенсація, узгоджена в договорі.":
  "The client pays the full agreed value of the item — not just the repair. This kind of equipment is hard to replace quickly in Ukraine, so the same compensation, agreed in the contract, applies to both damaged and lost items.",

# --- 06 форс-мажор і безпека
"Що робити, якщо обладнання дасть збій під час вечірки?": "What if the equipment fails during the party?",
"Одразу скажіть нашому представнику — він на місці протягом усього заходу саме для цього. Ми вживаємо всіх розумних заходів, щоб усунути несправність або на ходу замінити обладнання.":
  "Tell our representative right away — they're on site for the whole event for exactly this reason. We take all reasonable steps to fix the fault or swap the equipment on the spot.",
"Хто відповідає за музику, яку вмикають на події?": "Who is responsible for the music played at the event?",
"За правомірність аудіо- чи відеоконтенту, який звучить на події, відповідає замовник. Ми відповідаємо за технічне відтворення звуку, а не за права на самі матеріали.":
  "The client is responsible for the lawful use of any audio or video content played at the event. We are responsible for the technical playback of the sound, not for the rights to the material itself.",
"Що буде, якщо подію неможливо провести через форс-мажор?": "What happens if the event can't go ahead because of force majeure?",
"Ідеться про повітряну тривогу, відключення світла та інші обставини, які ми, на жаль, добре знаємо. Наш формат тут — велика перевага: він дуже мобільний. Навушники й передавач легко перенести, тож якщо поруч є укриття — бомбосховище чи паркінг, — вечір можна продовжити там: переїзд займає буквально кілька хвилин, і гості й далі танцюють у безпеці. Якщо продовжити не вдається, спершу шукаємо нову дату; якщо перенесення неможливе, домовляємось із урахуванням того, що вже фактично зроблено.":
  "This covers air raid alerts, power cuts and other circumstances we unfortunately know all too well. Our format is a real advantage here: it is very mobile. The headphones and the transmitter are easy to move, so if there is a shelter nearby — a bomb shelter or an underground car park — the evening can carry on there: the move takes just a few minutes, and guests keep dancing in safety. If it can't carry on, we first look for a new date; if rescheduling isn't possible, we agree on terms that take into account what has already been done.",
"Ідеться про повітряну тривогу, відключення світла та інші обставини. Наш формат дуже мобільний: якщо поруч є укриття — бомбосховище чи паркінг, — вечір можна продовжити там, переїзд займає кілька хвилин. Якщо продовжити не вдається, спершу шукаємо нову дату; якщо перенесення неможливе, домовляємось із урахуванням того, що вже фактично зроблено.":
  "This covers air raid alerts, power cuts and other such circumstances. Our format is very mobile: if there is a shelter nearby — a bomb shelter or an underground car park — the evening can carry on there, and the move takes just a few minutes. If it can't carry on, we first look for a new date; if rescheduling isn't possible, we agree on terms that take into account what has already been done.",
"Чи можна перенести подію через погану погоду?": "Can the event be moved because of bad weather?",
"Так, якщо дощ, сніг чи інші умови роблять захід небезпечним для обладнання або людей — погоджуємо нову дату за тим самим принципом, що й будь-яке інше перенесення.":
  "Yes. If rain, snow or other conditions make the event unsafe for the equipment or for people, we agree a new date on the same basis as any other reschedule.",
"Хто відповідає за безпеку на самому заході?": "Who is responsible for safety at the event itself?",
"Замовник відповідає за загальну організацію та безпеку події й майданчика. Ми відповідаємо за справну й безпечну роботу свого обладнання і маємо право зупинити його використання, якщо виникає реальна загроза людям чи техніці.":
  "The client is responsible for the overall organisation and safety of the event and the venue. We are responsible for our equipment working properly and safely, and we have the right to stop using it if there is a real threat to people or equipment.",
"Чи потрібно підписувати договір особисто, на папері?": "Do we have to sign the contract in person, on paper?",
"Ні. Договір і підтвердження замовлення можна погодити електронно — листуванням, месенджером або іншим зручним способом, без особистої зустрічі.":
  "No. The contract and the booking confirmation can be agreed electronically — by email, messenger or any other convenient way, with no need to meet in person.",

# --- розділ «Музика та авторські права»
"Музика та авторські права": "Music and copyright",
"Музика й права": "Music & rights",
"Чи потрібно мені самостійно готувати музику для SILENT?": "Do I need to prepare the music for SILENT myself?",
"Ні. Ми можемо повністю підготувати музичний супровід для вашої події: підібрати треки, сформувати тематичні плейлисти та розподілити музику між каналами SILENT відповідно до формату й атмосфери вечірки.":
  "No. We can prepare the music for your event in full: choose the tracks, build themed playlists and distribute the music across the SILENT channels to match the format and atmosphere of the party.",
"Якщо у вас є власні музичні побажання або готовий плейлист — ми також можемо працювати з ним.":
  "If you have your own music preferences or a ready playlist, we can work with that too.",
"Чи можна використовувати популярну музику та відомі треки?": "Can we use popular music and well-known tracks?",
"Так. SILENT технічно підтримує відтворення звичайного музичного контенту — від популярних хітів до тематичних добірок.":
  "Yes. SILENT technically supports playing ordinary music content, from popular hits to themed selections.",
"Музична програма може бути сформована під формат вашої події, її аудиторію та ваші побажання.":
  "The music programme can be built around the format of your event, its audience and your wishes.",
"Хто відповідає за авторські права на музику?": "Who is responsible for copyright on the music?",
"Це залежить від формату заходу.":
  "It depends on the format of the event.",
"SILENT відповідає за технічну частину: обладнання, передачу та відтворення аудіо через систему навушників.":
  "SILENT is responsible for the technical side: the equipment, the transmission and the playback of audio through the headphone system.",
"Питання прав на публічне використання музичного контенту, якщо такі права необхідні для конкретного заходу, врегульовуються організатором, замовником або майданчиком відповідно до формату події.":
  "Rights for the public use of music content, where such rights are required for a specific event, are handled by the organiser, the client or the venue, depending on the format of the event.",
"А якщо це просто приватна вечірка, день народження чи весілля?": "What if it's just a private party, a birthday or a wedding?",
"Для приватних подій ми можемо повністю підготувати музичну програму та плейлисти під вашу вечірку — вам не потрібно самостійно підбирати кожен трек.":
  "For private events we can fully prepare the music programme and playlists for your party, so you don't have to choose every track yourself.",
"Питання авторських і суміжних прав залежить від конкретного формату заходу, тому статус «приватної вечірки» не означає автоматичного звільнення від усіх вимог щодо використання музики.":
  "Copyright and related rights depend on the specific format of the event, so the status of a “private party” does not automatically exempt it from every requirement on the use of music.",
"Якщо для вашого заходу такі вимоги застосовуються, їх забезпечує організатор, замовник або майданчик.":
  "If such requirements apply to your event, they are handled by the organiser, the client or the venue.",
"А якщо це публічний або комерційний захід?": "What if it's a public or commercial event?",
"Для публічних та комерційних заходів питання музичних прав має бути врегульоване відповідно до законодавства та формату заходу.":
  "For public and commercial events, music rights must be settled in line with the law and the format of the event.",
"SILENT може підготувати музичну концепцію, плейлисти та забезпечити їх технічне відтворення, але не передає і не гарантує наявність авторських чи суміжних прав на окремі музичні твори або фонограми, якщо це окремо не погоджено в договорі.":
  "SILENT can prepare the music concept and playlists and provide their technical playback, but does not transfer or guarantee copyright or related rights in individual musical works or recordings unless this is separately agreed in the contract.",
"За необхідності відповідні права та дозволи забезпечує організатор, замовник або майданчик.":
  "Where needed, the relevant rights and permissions are provided by the organiser, the client or the venue.",
"Чи можете ви підготувати музику повністю під нашу подію?": "Can you prepare the music entirely for our event?",
"Так. Ми можемо створити музичну концепцію саме під ваш захід: від welcome music і фонового звучання до танцювальної частини та afterparty.":
  "Yes. We can create a music concept for your event specifically: from welcome music and background sound to the dance part and the afterparty.",
"Можемо підготувати окремі плейлисти для різних каналів SILENT, враховуючи формат події, аудиторію, атмосферу та ваші музичні побажання.":
  "We can prepare separate playlists for the different SILENT channels, taking into account the event format, the audience, the atmosphere and your musical wishes.",
"<strong>Важливо:</strong> підготовка та технічне відтворення музичної добірки SILENT не означає автоматичного надання прав на публічне використання кожного музичного твору. Якщо для конкретного заходу такі права необхідні, їх забезпечує відповідальна сторона відповідно до умов заходу.":
  "<strong>Important:</strong> preparing and technically playing a SILENT music selection does not automatically grant the right to publicly use every musical work. If such rights are required for a specific event, they are provided by the responsible party under the terms of the event.",

# --- блок над формою
'Не знайшли <span class="em">відповідь</span>?': "Didn't find <span class=\"em\">your answer</span>?",
'Питайте напряму — <a class="ask-link" href="mailto:hello.silent.ua@gmail.com">hello.silent.ua@gmail.com</a> або <a class="ask-link" href="https://t.me/silent_ukraine" target="_blank" rel="noopener noreferrer">напишіть нам у Telegram</a>. А якщо вже готові, просто перевірте дату своєї події й залиште заявку.':
  'Ask us directly — <a class="ask-link" href="mailto:hello.silent.ua@gmail.com">hello.silent.ua@gmail.com</a> or <a class="ask-link" href="https://t.me/silent_ukraine" target="_blank" rel="noopener noreferrer">message us on Telegram</a>. And if you\'re ready, just check the date of your event and send a request.',
}

# Рядки, які виводить site.js. На FAQ немає hero, тож hero порожній (як і в
# українській версії цієї сторінки); решта — ті самі переклади, що й у
# I18N_EN головної.
I18N_FAQ_EN = """<script>
window.SILENT_I18N = {
  base: '',
  locale: 'en-US',
  currency: 'UAH',
  hero: [],
  sound: { on: 'Sound on', off: 'Turn sound on', mute: 'Turn sound off' },
  calc: {
    outside: 'travel across Ukraine',
    reel: 'a short reel',
    smoke: 'smoke and lights',
    opts: (list) => `, options: ${list.join(', ')}`,
    summary: (qty, hours, opts, total) =>
      `From the calculator: ${qty} headphones, ${hours} hrs${opts}. Estimated budget: ${total} UAH.`,
    note: (qty, hours, total) =>
      `✓ Pulled in from the calculator: <b>${qty} headphones, ${hours} hrs, ~${total} UAH</b>. Check the comment below — you can add to it.`
  },
  uc: {
    order: 'Book this experience',
    count: (n) => `${n} ${n === 1 ? 'format' : 'formats'} in this theme`,
    line: (name) => `Interested in: ${name}.`,
    note: (name) => `✓ Chosen experience: <b>${name}</b>. It is already in the comment below — add any details you like.`
  },
  cal: { foot: 'Date in the form: ' },
  video: { clip: (n) => 'Clip ' + n, prev: 'Previous video', next: 'Next video' },
  form: {
    required: 'Please leave a name and a contact so we can get back to you.',
    contactBad: 'That contact does not look right. Leave a phone number, an @handle or an email so we can reach you.',
    datePast: 'That date has already passed. Pick the nearest one that works, or leave the field empty.',
    sending: 'Sending…',
    netFail: 'Could not send — the connection seems to be gone. Try again or message us on Telegram.',
    checking: (d) => `Checking <b>${d}</b>`
  }
};
</script>"""


def build_faq():
    s = unstamp(io.open(SRC_FAQ, encoding='utf-8').read())

    for old, new in HEAD_FAQ:
        if s.count(old) < 1:
            sys.exit('немає в faq/index.html: ' + old[:80])
        s = s.replace(old, new)

    # Сторінка на рівень глибше за faq/: відносні шляхи до активів — на
    # крок вище. Абсолютні (/images/…) і так працюють.
    s = s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
    # Заготовлений текст у посиланні Telegram — англійською, як і на головній.
    s = s.replace(PATHS[0][0], PATHS[0][1])

    # Посилання: головна та її розділи — на англійську головну, сама FAQ —
    # на англійську FAQ. /experiences/ і /privacy/ лишаються українськими:
    # англійських версій цих сторінок поки немає. ДО заміни перемикача мови:
    # в українському перемикачі вже стоїть /en/faq/, регулярки його не
    # зачеплять, а в англійському з'явиться /faq/ на українську — його
    # чіпати не можна.
    s = re.sub(r'href="/(#[^"]*)?"', lambda m: 'href="/en/' + (m.group(1) or '') + '"', s)
    s = s.replace('href="/faq/', 'href="/en/faq/')
    s = EXP_LINK.sub('href="/en/experiences/', s)
    # Хлібні крихти в JSON-LD — на англійські адреси, як і видимі посилання.
    s = s.replace('"item": "https://silent.org.ua/"', '"item": "https://silent.org.ua/en/"')
    s = s.replace('"item": "https://silent.org.ua/faq/"', '"item": "https://silent.org.ua/en/faq/"')

    if s.count(SWITCH_UA_FAQ) != 1:
        sys.exit('перемикач мови в faq/index.html не знайдено')
    s = s.replace(SWITCH_UA_FAQ, SWITCH_EN_FAQ)

    m = re.search(r'<script>\nwindow\.SILENT_I18N = \{[\s\S]*?\n\};\n</script>', s)
    if not m:
        sys.exit('блок SILENT_I18N у faq/index.html не знайдено')
    s = s[:m.start()] + I18N_FAQ_EN + s[m.end():]

    # Об'єднаний словник: повні речення FAQ + спільні рядки меню/футера/форми.
    merged = dict(T)
    merged.update(T_FAQ)
    for k in sorted(merged, key=len, reverse=True):
        s = flexible(k).sub(lambda mm, v=merged[k]: v, s)

    # FAQPage і хлібні крихти — заново з англійського тексту сторінки.
    s = set_faq_jsonld(s, 'en')

    os.makedirs(os.path.dirname(DST_FAQ), exist_ok=True)
    io.open(DST_FAQ, 'w', encoding='utf-8').write(s)
    assert_translated(s, 'en/faq/index.html')
    print('en/faq/index.html зібрано:', len(s.split('\n')), 'рядків, неперекладеного немає')


# ====================================================== Тихі враження (en/experiences/)
# Та сама схема, що для FAQ: en/experiences/index.html збирається з
# experiences/index.html, руками не редагується. Картки форматів (44 шт.)
# беруть переклад зі спільного словника T — той самий, що й на англійській
# головній.
SRC_EXP = os.path.join(ROOT, 'experiences', 'index.html')
DST_EXP = os.path.join(ROOT, 'en', 'experiences', 'index.html')

HEAD_EXP = [
 ('<html lang="uk">', '<html lang="en">'),
 ('<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="en_US">'),
 ('<meta property="og:url" content="https://silent.org.ua/experiences/">',
  '<meta property="og:url" content="https://silent.org.ua/en/experiences/">'),
 ('<link rel="canonical" href="https://silent.org.ua/experiences/">',
  '<link rel="canonical" href="https://silent.org.ua/en/experiences/">'),
]

SWITCH_UA_EXP = """    <span class="lang-switch" role="group" aria-label="Мова сайту">
      <span class="lang-cur" aria-current="true">UA</span>
      <a href="/en/experiences/" hreflang="en" lang="en">EN</a>
    </span>"""
SWITCH_EN_EXP = """    <span class="lang-switch" role="group" aria-label="Site language">
      <a href="/experiences/" hreflang="uk" lang="uk">UA</a>
      <span class="lang-cur" aria-current="true">EN</span>
    </span>"""

T_EXP = {
"Тихі враження — формати silent disco від SILENT": "Quiet Experiences — silent disco formats from SILENT",
"Усі формати, де працює тихий звук: від корпоративу й весілля до екскурсії музеєм та йоги. Три канали в навушниках кожного гостя, ззовні тиша.":
  "Every format where quiet sound works: from a corporate party and a wedding to a museum tour and yoga. Three channels in every guest's headphones, and quiet outside.",
"Усі формати, де працює тихий звук: корпоративи, весілля, конференції, екскурсії, йога, кіно просто неба.":
  "Every format where quiet sound works: corporate parties, weddings, conferences, tours, yoga, open-air cinema.",
"Три канали музики в навушниках кожного гостя, гучність у кожного своя, ззовні тиша. Комплект, доставка, збірка й супровід.":
  "Three channels of music in every guest's headphones, everyone sets their own volume, and it stays quiet outside. Equipment, delivery, setup and support.",
"Формати: диско, фітнес, кіно, весілля, корпоративи, фестивалі, стендап, дитячі свята, виставки, духовні й культурні події, бізнес-заходи, концерти, освітні події, табори, медитації та інші — 44 сценарії нижче.":
  "Formats: disco, fitness, cinema, weddings, corporate parties, festivals, stand-up, kids' parties, exhibitions, spiritual and cultural events, business events, concerts, educational events, camps, meditations and more — 44 scenarios below.",
"Silent disco — лише один зі сценаріїв. Той самий комплект працює всюди, де звук має дійти до кожного, але не мусить лунати на всю залу: від корпоративу й весілля до екскурсії музеєм, конференції та йоги.":
  "Silent disco is only one of the scenarios. The same set works wherever sound has to reach everyone but shouldn't fill the whole room: from a corporate party and a wedding to a museum tour, a conference and yoga.",
"Оберіть формат, близький до вашого — або лишіть заявку, і ми підберемо його разом.":
  "Pick the format closest to yours — or send a request and we'll choose one together.",
"Що таке Silent disco?": "What is silent disco?",
"Не знайшли свій формат? Зробимо його сорок п’ятим.": "Can't find your format? We'll make it the forty-fifth.",
"Напишіть, що плануєте — скажемо, чи підходить тихий звук і скільки це коштуватиме.":
  "Tell us what you're planning — we'll say whether quiet sound fits and how much it will cost.",
"Дивитися досвід": "View the experience",
}


def build_experiences():
    if not os.path.exists(SRC_EXP):
        return
    s = unstamp(io.open(SRC_EXP, encoding='utf-8').read())

    for old, new in HEAD_EXP:
        if s.count(old) < 1:
            sys.exit('немає в experiences/index.html: ' + old[:80])
        s = s.replace(old, new)

    # Сторінка на рівень глибше, ніж experiences/: відносні шляхи до активів.
    s = s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
    s = s.replace(PATHS[0][0], PATHS[0][1])   # заготовлений текст Telegram — англійською

    # hreflang: сторінка називає пару (uk, en, x-default) — вона вже в
    # українській і однакова в обох. Лишається поміняти адреси переходів.
    s = re.sub(r'href="/(#[^"]*)?"', lambda m: 'href="/en/' + (m.group(1) or '') + '"', s)
    s = s.replace('href="/faq/', 'href="/en/faq/')
    s = EXP_LINK.sub('href="/en/experiences/', s)
    # JSON-LD: адреси, мова, хлібні крихти.
    s = s.replace('"@id": "https://silent.org.ua/experiences/#', '"@id": "https://silent.org.ua/en/experiences/#')
    s = s.replace('"url": "https://silent.org.ua/experiences/"', '"url": "https://silent.org.ua/en/experiences/"')
    s = s.replace('"item": "https://silent.org.ua/experiences/"', '"item": "https://silent.org.ua/en/experiences/"')
    s = s.replace('"item": "https://silent.org.ua/"', '"item": "https://silent.org.ua/en/"')
    s = s.replace('"inLanguage": "uk-UA"', '"inLanguage": "en-US"')

    if s.count(SWITCH_UA_EXP) != 1:
        sys.exit('перемикач мови в experiences/index.html не знайдено')
    s = s.replace(SWITCH_UA_EXP, SWITCH_EN_EXP)

    m = re.search(r'<script>\nwindow\.SILENT_I18N = \{[\s\S]*?\n\};\n</script>', s)
    if not m:
        sys.exit('блок SILENT_I18N у experiences/index.html не знайдено')
    s = s[:m.start()] + I18N_FAQ_EN + s[m.end():]

    merged = dict(T)
    merged.update(T_FAQ)
    merged.update(T_EXP)
    for k in sorted(merged, key=len, reverse=True):
        s = flexible(k).sub(lambda mm, v=merged[k]: v, s)

    os.makedirs(os.path.dirname(DST_EXP), exist_ok=True)
    io.open(DST_EXP, 'w', encoding='utf-8').write(s)
    assert_translated(s, 'en/experiences/index.html')
    print('en/experiences/index.html зібрано:', len(s.split('\n')), 'рядків, неперекладеного немає')


if __name__ == '__main__':
    # Першим: дописує теми й кнопки фільтра в сам index.html, з якого далі
    # збирається все інше.
    build_home_filter()
    build()
    build_404()
    # Стрічку сценаріїв збираємо до позначки версій: вона переписує сторінки
    # досвідів, і хеш активів має лягти вже на готовий вміст.
    build_experience_strips()
    print('FAQ JSON-LD (uk):', build_faq_ua_jsonld(), 'питань')
    build_faq()
    build_experiences()
    # Останнім кроком, коли обидві англійські сторінки вже на диску: позначка
    # лягає на всі чотири файли одразу.
    stamp_files()
