"""Одноразовий генератор сторінки /experiences/dance-competitions/ (танцювальні змагання, 25.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: данс-батл трьох команд, танцювальна школа або
студія, бальні танці (додано 25.11); на сторінці шість карток (ще підліткові команди, вечірка після змагань).
Факти з картки каталогу: до трьох команд, кожна слухає свій канал на одному танцполі. Журі, ведучого й правила
приносить клієнт; SILENT дає навушники, канали, за потреби передавач із мікрофоном. НЕ обіцяємо: дальності
сигналу, безпеки слуху. Тексти писано за скілом humanizer (без тире). Фото: 19 кадрів із ChatGPT
(inbox/dance-competitions/gen → convert.py → images/dance-competitions/); на кожному кадрі команда = колір.
Запуск: python3 tools/gen_dance_competitions_page.py (далі build_en.py). УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'dance-competitions', 'index.html')
IMG = '../../images/dance-competitions/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'dance-competitions', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

FLOOR = 'try-komandy-tantsiuiut-na-odnomu-tantspoli.webp'       # 01b картка 3:2
FOCUS = 'tantsivnytsia-v-zelenykh-navushnykakh-u-rusi.webp'       # 02 «Чому» 2:3
SCHOOL = 'vidkryta-podiia-tantsiuvalnoi-shkoly.webp'              # 03 картка 3:2
SHOWCASE = 'pokaz-studii-dvi-hrupy-v-riznykh-stiliakh.webp'       # 04 картка 3:2
TEENS = 'pidlitkova-komanda-tantsiuie-v-zali.webp'                # 05 картка 3:2
BALL = 'balni-tantsi-try-pary-hala-bal.webp'                        # 20 картка 3:2 (бальні танці, замість кола)
AFTER = 'vechirka-pislia-batlu-vsi-razom.webp'                    # 07 картка 3:2
PORTRAIT = 'portret-tantsivnytsi-iz-zaplyshchenymy-ochyma.webp'      # 25 квадрат («Чому» s-a, бальні)
FACEOFF = 'suparnyky-z-riznykh-komand-posmikhaiutsia.webp'        # 09 квадрат («Чому» s-b)
G1 = 'tantsivnytsia-v-zelenii-sukni-v-kruzhlinni.webp'              # 22 колаж 4:5 (бальні)
G2 = 'tantsivnyk-u-pozi-hip-hop.webp'                             # 11
G3 = 'tantsivnyk-u-fraku-v-elehantnii-pozi.webp'                  # 23 (бальні)
G4 = 'pidlitok-tantsiuie-z-radistiu.webp'                         # 13
G5 = 'valsuiucha-para-v-hala-bali.webp'                             # 21 (бальні)
G6 = 'litnia-para-tantsiuie-bal.webp'                               # 24 (бальні)
G7 = 'tantsivnytsia-v-stribku.webp'                               # 10 стрибок (повний зріст, світла зала)
G8 = 'dvi-tantsivnytsi-v-unison.webp'                             # 12 пара в унісон
G9 = 'komanda-sviatkuie-v-obiimakh.webp'                          # 15 група в обіймах
G10 = 'try-balni-pary-u-vals-zeleni-navushnyky.webp'              # 26 три бальні пари на повний зріст
HANDOUT = 'vydacha-navushnykiv-bilia-zalu-zmahan.webp'            # 16 2:3
LEADER = 'vedouchyi-hovoryt-do-trokh-komand.webp'                 # 17 квадрат
TECH = 'tekhnik-nalashtovuie-harnituru-vedouchomu.webp'           # 18 4:5
FINAL = 'try-komandy-tantsiuiut-u-velykomu-zali.webp'             # 19 16:9

TITLE = 'Танцювальні змагання: кожна команда під свій трек | SILENT'
DESC = 'Бездротові навушники для танцювальних змагань і данс-батлів: до трьох команд танцюють на одному майданчику, кожна під свою музику. Київ і по Україні.'
OG_T = TITLE
OG_D = 'До трьох команд танцюють на одному танцполі, і кожна слухає свій канал. Танцювальні змагання в навушниках. Київ і по Україні.'
OG_ALT = 'Три команди танцюють у світлому залі: червоні, зелені й сині навушники SILENT, кожна команда під свій трек'

s = open(SRC, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('Очікував %d збіг(и), знайшов %d: %r' % (count, n, old[:90]))
    s = s.replace(old, new)

def rep_re(pat, new, count=1):
    global s
    s, n = re.subn(pat, new, s, flags=re.S)
    if n != count:
        sys.exit('Регулярка: очікував %d, знайшов %d: %r' % (count, n, pat[:90]))

# ---------- <head> ----------
old_title = 'Конференції в навушниках — Silent Disco під ключ | SILENT'
rep('<title>%s</title>' % old_title, '<title>%s</title>' % TITLE)
rep('"name": "%s"' % old_title, '"name": "%s"' % TITLE)
old_desc = 'Аудіосупровід конференцій, воркшопів і бізнес-заходів у бездротових навушниках. 3 аудіоканали, технічний супровід, Київ та виїзд по Україні.'
rep(old_desc, DESC, count=3)
rep('Конференції в навушниках — Silent Disco | SILENT', OG_T, count=2)
rep('Аудіосупровід доповідей, воркшопів і бізнес-заходів у бездротових навушниках SILENT. Київ і виїзд по Україні.', OG_D, count=2)
rep('images/conferences/og-conferences.jpg', 'images/dance-competitions/og-dance-competitions.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Танцювальні змагання",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для танцювальних змагань"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для танцювальних змагань"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Танцювальні школи й студії, організатори данс-батлів і танцювальних змагань"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-25"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/dance-competitions/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/dance-competitions/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/dance-competitions/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Танцювальні змагання</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Танцювальні<br>змагання<br>в навушниках</span> <span class="t-sub">кожна команда танцює під свій трек</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Данс-батл чи бальні танці: до трьох команд або груп пар виходять на один танцпол одночасно, і кожна слухає свою музику в навушниках. Журі й ведучого запрошуєте ви, а SILENT видає навушники, налаштовує канали й супроводжує змагання.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="dance_hero_order">Обговорити змагання</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Свій канал</b> <span>для кожної команди.</span></span>')

# 10 різних кадрів (по 5 в колонці), щоб повтор безкінечного скролу був далеко; сусідні різні за характером:
# бальні (22, 24, 21, 26, 23) чергуються з хіп-хопом, стрибком, групою, підлітком, парою в унісон
gal1 = [(G1, '50% 40%'), (G7, '50% 40%'), (G6, '50% 40%'), (G4, '50% 40%'), (G10, '50% 40%')]
gal2 = [(G2, '50% 40%'), (G5, '50% 40%'), (G9, '50% 40%'), (G3, '50% 40%'), (G8, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# Колонки колажу втричі довші за типові (по 10 плиток замість 6): щоб швидкість стрічки лишилась тією самою,
# подовжуємо тривалість циклу пропорційно (46с * 10/6 ≈ 77с), інакше стрічка летіла б майже вдвічі швидше.
for _n in ('1', '2'):
    _old = '<div class="gallery-col gallery-col-%s">' % _n
    assert s.count(_old) == 1, _old
    s = s.replace(_old, '<div class="gallery-col gallery-col-%s" style="animation-duration:77s">' % _n)

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА ТАНЦЮВАЛЬНИХ ЗМАГАННЯХ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="dance-competitions">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Танцівниця в зелених навушниках SILENT посеред руху з зосередженим поглядом, позаду танцюють інші"' % (IMG, FOCUS))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Танцівниця в синіх навушниках SILENT із закритими очима, захоплена музикою, на тлі прожекторів бальної зали"' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Двоє танцюристів із різних команд грайливо суперничають: один у синіх навушниках SILENT, другий у червоних"' % (IMG, FACEOFF))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Кожна команда танцює під свій трек</h2>\n'
    '      <p>На звичайних змаганнях з колонок грає одна музика для всіх, і команди виходять на майданчик по черзі. Інші чекають.</p>\n'
    '      <p>У навушниках SILENT до трьох команд виходять на один танцпол одночасно, і кожна слухає свій канал. Те саме працює для бальних танців: пари танцюють свій вальс чи танго, а чужа музика їм не заважає. Гучність танцюрист налаштовує сам.</p>\n'
    '      <p>Журі та ведучого запрошуєте ви, а правила складаєте самі. Якщо потрібен голос ведучого, він говорить у мікрофон портативного передавача, який налаштовує SILENT. Попередьте команду, і ми підготуємо.</p>\n'
    '      <p class="story-sub story-close">Свій трек. Свій канал. Один танцпол.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де танцювальні змагання в навушниках працюють особливо добре</h2>')
cards = [
    (FLOOR, '50% 45%', 'Три команди танцюють одночасно в світлому залі: червоні, зелені й сині навушники SILENT, кожна команда під свій трек', 'Данс-батл трьох команд',
     'Усі три команди танцюють одночасно, кожна під свій трек у своїх навушниках. Один танцпол і три різні музики.'),
    (SCHOOL, '50% 45%', 'Відкрите заняття танцювальної школи: учні різного віку вивчають комбінацію в студії з дзеркалами, усі в синіх навушниках SILENT', 'Відкрита подія танцювальної школи',
     'Учні й гості вчать комбінацію під музику в навушниках. У залі тихо, а рухи йдуть у такт.'),
    (SHOWCASE, '50% 45%', 'Показ студії: ліворуч шестеро хіп-хоп танцюристів у червоних навушниках SILENT, праворуч шестеро сучасних танцюристів у синіх', 'Показ студії',
     'Дві групи виступають одночасно в різних стилях, і кожна слухає свій трек. Студія показує кілька напрямів на одному майданчику.'),
    (TEENS, '50% 45%', 'Команда з шести підлітків у однакових футболках танцює вуличний стиль у шкільному спортзалі в зелених навушниках SILENT', 'Підліткові команди',
     'Підлітки готують виступ або змагаються в залі школи чи клубу. Гучність у кожного своя.'),
    (BALL, '50% 45%', 'Шість пар вальсують у бальній залі з високими вікнами: жінки в довгих сукнях, чоловіки в темних костюмах, усі в синіх навушниках SILENT', 'Бальні танці',
     'Пари танцюють вальс чи інший бальний танець, і кожна група слухає свій трек. У залі тихо, а музика звучить лише у вухах танцюристів.'),
    (AFTER, '50% 45%', 'Вечірка після данс-батлу: вісімнадцять танцюристів із різних команд танцюють разом із піднятими руками в синіх навушниках SILENT', 'Вечірка після змагань',
     'Після оголошення результатів усі команди переходять на один канал і танцюють разом, як на тихій дискотеці.'),
]
arts = []
for img, pos, alt, h3, p in cards:
    arts.append('      <article class="uc-card scen-card reveal">\n        <div class="uc-media">\n'
                '          <img src="%s%s" style="--lqip:url(%s);object-position:%s" width="640" height="640" alt="%s" loading="lazy" decoding="async">\n'
                '        </div>\n        <div class="uc-body">\n          <h3>%s</h3>\n          <p>%s</p>\n        </div>\n      </article>'
                % (IMG, img, lqip(img), pos, alt, h3, p))
rep_re(r'(<div class="scen-cards scen-cards--six">\n).*?(\n    </div>\n  </div>\n</section>\n\n<!-- ЯК ЦЕ ПРАЦЮЄ)',
       r'\g<1>' + '\n'.join(arts).replace('\\', '\\\\') + r'\g<2>')

# ---------- Як це працює ----------
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на танцювальних змаганнях</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на танцювальних змаганнях</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Свій канал для команди</b> <span>До трьох команд танцюють одночасно, кожна на своєму каналі. Танцюрист перемикає канал одним дотиком, а SILENT налаштовує їх перед початком.</span></li>\n'
    '        <li><b>Свій трек</b> <span>Музику для кожної команди можна підготувати заздалегідь: плейлисти SILENT або ваші треки. Розкажіть про змагання, і ми підкажемо, як усе налаштувати.</span></li>\n'
    '        <li><b>Голос ведучого</b> <span>Якщо потрібен ведучий, його запрошуєте ви. Він бере портативний передавач із мікрофоном і говорить на потрібному каналі.</span></li>\n'
    '        <li><b>Усе налаштовує SILENT</b> <span>Ми привозимо навушники, налаштовуємо канали, видаємо навушники танцюристам і збираємо після змагань. Гучність у кожного своя: є регулятор.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук змагань беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте програму, журі й правила, а <a href="/">SILENT</a> дає навушники й налаштовує канали, щоб кожна команда чула свій трек.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для танцюристів із регулятором гучності;</span></li>\n'
    '        <li><span>канали для команд, до трьох одночасно;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого, якщо він потрібен;</span></li>\n'
    '        <li><span>видача навушників на вході й збір після змагань;</span></li>\n'
    '        <li><span>технічний супровід протягом заходу.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT біля входу в залу віддає танцівниці навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Ведучий змагань говорить до трьох команд у залі, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає ведучому закріпити гарнітуру, у руці в ведучого портативний передавач"' % (IMG, TECH))
rep_re(r'<img style="object-position:50% 50%"( width="1254" height="1254" class="s-b" src="[^"]*tekhnik-nalashtovuie-harnituru-vedouchomu\.webp")',
       r'<img style="object-position:50% 8%"\g<1>')

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від дати до першого виходу на танцпол</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату змагань, місця й кількості команд. На цій основі підбираємо комплект і канали.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Три команди танцюють у великому залі з високими вікнами: червоні, зелені й сині навушники SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат змагань, кількість танцюристів і команд.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, канали для команд, музику й мікрофон для ведучого, якщо він потрібен.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників танцюристам.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо змагання</h3>\n        <p>Налаштовуємо канали, перевіряємо звук, видаємо навушники й збираємо комплект після змагань відповідно до погодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="dance_process_order">Обговорити змагання</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="sport"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Танцювальні змагання" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Танцювальні змагання лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/sport/">спортивні події</a>, <a href="/experiences/yoga/">йога й ecstatic dance</a>, <a href="/experiences/dj-set/">діджей-сет наживо</a> й <a href="/experiences/silent-disco/">Silent Disco</a>. Поради шукайте в <a href="/blog/">блозі</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на танцювальних змаганнях')
Q = [
 ('Скільки команд може танцювати одночасно?', 'До трьох команд. Кожна слухає свій канал, а танцюрист перемикає канал одним дотиком.', ''),
 ('Чи може кожна команда мати свою музику?', 'Так. Музику для кожної команди можна підготувати заздалегідь: плейлисти SILENT або ваші треки. Розкажіть про змагання, і ми налаштуємо.', ''),
 ('Чи надаєте ви журі та ведучого?', 'Ні, журі й ведучого запрошуєте ви. SILENT дає навушники, канали, портативний передавач із мікрофоном і супроводжує змагання.', ''),
 ('Чи підходить формат для бальних танців?', 'Так. Пари танцюють бальні танці під свій трек у навушниках, а групи пар можна розвести по каналах. Після виступів усі можуть перейти на один канал і потанцювати разом.', ''),
 ('Чи можна кожному налаштувати гучність?', 'Так. У кожних навушниках є регулятор гучності, тож танцюрист сам обирає, наскільки гучно слухати.', ''),
 ('Скільки коштують навушники для змагань?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники танцюристам на вході й збираємо після змагань. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="dance_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="dance_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для танцювальних змагань</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові канали чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте танцювальні змагання? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про змагання, команди й місце. Ми підкажемо, як налаштувати канали й музику для кожної команди, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості танцюристів.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для змагань</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Танцювальні змагання</option>')
rep('Залиште заявку — перевіримо доступність обладнання та зв’яжемося з вами, щоб узгодити формат і технічні деталі.', 'Залиште заявку, ми перевіримо доступність обладнання та зв’яжемося з вами, щоб узгодити формат і технічні деталі.')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x and 'conferences/' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
