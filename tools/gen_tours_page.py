"""Одноразовий генератор сторінки /experiences/tours/ (радіогід для екскурсій, 14.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої. Кожна заміна має
збігтися рівно один раз (інакше скрипт падає), а наприкінці перевіряється, що в основному вмісті
сторінки не лишилось слова «конференц»/«conferen» (меню й підвал мають їх законно).
Факти погоджено з власником: гід ходить із групою (портативний передавач із мікрофоном), умови
як для всіх форматів (від 40 навушників / 4 год / від 12 000 грн), команда SILENT присутня.
Дальності сигналу, кількості мов і кількох гідів одночасно НЕ обіцяємо.
Запуск: python3 tools/gen_tours_page.py  (далі python3 tools/build_en.py)
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'tours', 'index.html')
IMG = '../../images/tours/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'tours', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

# Фото (14.11.2026): 4 від власника (сині навушники) + 15 згенерованих у ChatGPT за референсом навушників власника
# (усі навушники сині, логотип вертикально посередині чаші). Кожен кадр на сторінці один раз, без повторів.
EXPO = 'ekskursiya-hid-na-vystavtsi-stend.webp'
EXPO2 = 'ekskursiya-hid-poyasnyuye-hrupi-na-expo.webp'
GUIDE = 'ekskursiya-halereya-hid-z-hrupoyu.webp'
MUSEUM = 'ekskursiya-muzey-balkon-hrupa.webp'
STREET = 'ekskursiya-hid-vede-hrupu-starym-mistom.webp'
STATUES = 'ekskursiya-muzey-zala-skulptur.webp'
GUIDEMIC = 'ekskursiya-hid-z-mikrofonom-na-ploshchi.webp'
SCHOOL = 'ekskursiya-shkolyari-v-istorychnomu-muzei.webp'
GARDEN = 'ekskursiya-botanichnyi-sad-oranzhereya.webp'
BREWERY = 'ekskursiya-pyvovarnya-vyrobnytstvo.webp'
EVENING = 'ekskursiya-vechirnia-naberezhna.webp'
HANDOUT = 'ekskursiya-vydacha-navushnykiv.webp'
SENIORS = 'ekskursiya-litni-turysty-monastyr.webp'
VIEW = 'ekskursiya-ohliadovyi-maidanchyk.webp'
FORT = 'ekskursiya-fortetsia-brama.webp'
FRESCO = 'ekskursiya-freska-v-navushnykakh.webp'
RIVER = 'ekskursiya-richkovyi-teplokhid.webp'
PARK = 'ekskursiya-osinnii-park-simeina.webp'
LIB = 'ekskursiya-biblioteka.webp'

TITLE = 'Радіогід для екскурсій у навушниках — під ключ | SILENT'
DESC = ('Радіогід для екскурсій і турів: голос гіда звучить у бездротових навушниках кожного учасника. '
        'Від 40 навушників, супровід команди, Київ і виїзд по Україні.')
OG_T = 'Радіогід для екскурсій у навушниках | SILENT'
OG_D = 'Голос гіда в бездротових навушниках кожного учасника: гіду не треба кричати, групі не треба тіснитися. Київ і виїзд по Україні.'
OG_ALT = 'Гід розповідає групі в галереї, усі слухають у бездротових навушниках SILENT'

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
rep(old_desc, DESC, count=3)          # meta description + WebPage + Service
rep('Конференції в навушниках — Silent Disco | SILENT', OG_T, count=2)
rep('Аудіосупровід доповідей, воркшопів і бізнес-заходів у бездротових навушниках SILENT. Київ і виїзд по Україні.', OG_D, count=2)
rep('images/conferences/og-conferences.jpg', 'images/tours/og-tours.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Екскурсії",')
rep('"name": "Silent Disco для конференцій"', '"name": "Радіогід для екскурсій від SILENT"')
rep('"serviceType": "Silent disco"', '"serviceType": "Радіогід для екскурсій"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Гіди, турагенції, музеї, школи й організатори екскурсій"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-14"')
# FAQPage у head перезбере build_en.py (set_experience_faq_jsonld) з видимих питань.
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/tours/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/tours/')

rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/tours/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Екскурсії</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Радіогід для екскурсій</span> <span class="t-sub">у бездротових навушниках SILENT</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Гід говорить у мікрофон, а кожен учасник чує його в бездротових навушниках: і в кінці групи, і на гамірній вулиці. SILENT привозить систему, видає навушники на старті та забезпечує технічний супровід екскурсії.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="tours_hero_order">Обговорити екскурсію</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Голос гіда</b> <span>У навушниках кожного.</span></span>')

gal1 = [(RIVER, '50% 45%'), (SENIORS, '50% 40%'), (PARK, '50% 45%')]
gal2 = [(GARDEN, '60% 40%'), (EXPO, '50% 45%'), (LIB, '50% 45%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ РАДІОГІД: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="tours">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Гід розповідає групі відвідувачів галереї, усі слухають у бездротових навушниках SILENT"' % (IMG, GUIDE))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Гід розповідає групі біля мармурової статуї в музейній залі, усі в навушниках SILENT"' % (IMG, STATUES))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Жінка в навушниках SILENT торкається чаші й роздивляється стару фреску в храмі"' % (IMG, FRESCO))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Коли гіда не чути вже з третього ряду</h2>\n'
    '      <p>На вулиці шумить транспорт, у музеї прийнято говорити тихо, а група з кількох десятків людей розтягується на метри. Гід підвищує голос, задні ряди перепитують, і частина історії губиться.</p>\n'
    '      <p>З радіогідом гід говорить звичайним голосом у мікрофон, а учасники чують його в бездротових навушниках. Не треба тіснитися довкола гіда, щоб розібрати слова: можна роздивлятися фасад чи експонат і слухати водночас.</p>\n'
    '      <p>Навушники не відрізають від світу: звуки довкола лишаються чутними, а щоб поставити запитання, досить зняти їх на шию.</p>\n'
    '      <p class="story-sub story-close">Один гід. Уся група чує. Ніхто не кричить.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де радіогід особливо потрібен</h2>')
cards = [
    (STREET, '55% 45%', 'Гід веде групу в навушниках SILENT бруківкою старого міста', 'Пішохідні екскурсії містом',
     'Гід веде групу вулицями, а розповідь звучить у навушниках кожного. Шум транспорту й натовпу не заглушує історію, а групі не треба збиватися в щільне коло на кожній зупинці.'),
    (MUSEUM, '40% 45%', 'Група відвідувачів музею в навушниках SILENT на балконі над залою з картинами', 'Музеї та галереї',
     'У залах, де прийнято говорити тихо, гід розповідає впівголоса й не заважає іншим відвідувачам. Учасники стоять біля експоната, а не тісняться біля гіда.'),
    (VIEW, '40% 45%', 'Група в навушниках SILENT на оглядовому майданчику над містом на заході сонця', 'Тури за містом і на природі',
     'Стежка, оглядовий майданчик чи парк: гід розповідає на ходу, без мегафона й крику, навіть коли довкола вітер або гамір інших туристів.'),
    (BREWERY, '50% 40%', 'Екскурсія пивоварнею: група в захисних жилетах слухає гіда в навушниках SILENT', 'Виставки та екскурсії підприємствами',
     'Шоурум, виставка чи цех, де працює обладнання й гомонять відвідувачі: голос гіда звучить у навушниках, а не губиться в залі.'),
    (SCHOOL, '50% 40%', 'Школярі в навушниках SILENT роздивляються вітрину в історичному музеї', 'Шкільні та студентські екскурсії',
     'Великий клас чи курс слухає одного гіда, а вчителеві чи куратору не треба збирати всіх у тісне коло й перекрикувати групу.'),
    (EVENING, '55% 45%', 'Вечірня екскурсія набережною: гід із мікрофоном і група в навушниках SILENT', 'Вечірні прогулянки й тури',
     'Вечірня прогулянка містом чи тур до заходу сонця: гід розповідає тихо, у тон атмосфері, а група чує кожне слово.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працює радіогід SILENT</h2>')
rep_re(r'(<h2 class="exp-h2">Як працює радіогід SILENT</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Гід говорить у мікрофон</b> <span>Голос іде з портативного передавача прямо в бездротові навушники учасників. Гід веде групу маршрутом, як завжди, тільки без крику.</span></li>\n'
    '        <li><b>Кожен регулює гучність</b> <span>У навушниках є регулятор гучності: учасник налаштовує звук під себе.</span></li>\n'
    '        <li><b>Без розеток на маршруті</b> <span>Навушники бездротові й приїжджають зарядженими, заряду вистачає на 10+ годин.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники на старті, супроводжує екскурсію й збирає комплект після завершення відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Технічну частину екскурсії беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p><a href="/">SILENT</a> — це не просто навушники. Ми привозимо систему, налаштовуємо її й супроводжуємо екскурсію, щоб гід займався групою, а не технікою.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для всієї групи;</span></li>\n'
    '        <li><span>мікрофон і портативний передавач для гіда;</span></li>\n'
    '        <li><span>налаштування й перевірка звуку перед стартом;</span></li>\n'
    '        <li><span>видача навушників на початку й збір наприкінці;</span></li>\n'
    '        <li><span>технічний супровід протягом екскурсії.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Перед екскурсією туристам видають навушники SILENT з кейса"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Гід із мікрофоном-гарнітурою розповідає групі на старій площі"' % (IMG, GUIDEMIC))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Гід пояснює групі на виставці, учасники слухають у навушниках SILENT"' % (IMG, EXPO2))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від маршруту до першої зупинки</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з вашого маршруту, кількості учасників і тривалості. На цій основі визначаємо комплект і логістику.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Сім’ї з дітьми проходять крізь браму фортеці за гідом, усі в навушниках SILENT"' % (IMG, FORT))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, маршрут чи локацію, кількість учасників і тривалість екскурсії.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофон для гіда та технічні умови маршруту.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо точку зустрічі, час налаштування та видачу навушників.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо екскурсію</h3>\n        <p>Налаштовуємо систему, перевіряємо звук, видаємо навушники на старті й збираємо їх після завершення відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="tours_process_order">Обговорити екскурсію</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="culture"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Екскурсії" -->')

rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Ті самі навушники працюють не лише на екскурсіях. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші формати: <a href="/experiences/conferences/">конференції й виставки</a>, <a href="/experiences/school/">шкільні свята</a>, фестивалі й приватні вечірки. Як працює Silent Disco загалом, розповідаємо <a href="/experiences/silent-disco/">на окремій сторінці</a>, а поради для подій просто неба шукайте в <a href="/blog/">блозі</a>: <a href="/blog/yak-organizuvaty-zakhid-u-parku/">як організувати захід у парку</a> і <a href="/blog/yak-organizuvaty-zvuk-na-zakhodi-prosto-neba/">як організувати звук на заході просто неба</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про радіогід для екскурсій')
Q = [
 ('Чи може гід ходити разом із групою?', 'Так. Гід говорить у мікрофон із портативним передавачем і веде групу маршрутом, а учасники чують його в навушниках на ходу.', ''),
 ('Чим радіогід кращий за мегафон чи колонку?', 'Звук іде не в простір, а в навушники учасників. Гід говорить звичайним голосом, не заважає перехожим чи іншим відвідувачам музею, а розповідь чути навіть у кінці групи.', ''),
 ('Скільки коштує радіогід для екскурсії?', 'Базовий орієнтир — від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Яка мінімальна кількість навушників?', 'Базова пропозиція SILENT починається від 40 навушників на 4 години. Якщо група менша, вартість рахується за базовим комплектом.', ''),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає навушники й стежить за технікою?', 'Команда SILENT налаштовує систему, перевіряє звук, видає навушники на старті, забезпечує технічний супровід і збирає комплект після екскурсії.', ''),
 ('Чи можна користуватися радіогідом на вулиці?', 'Так. Навушники бездротові й приїжджають зарядженими, заряду вистачає на 10+ годин, тож розетка на маршруті не потрібна. На випадок дощу варто мати запасний план, обговоримо його під ваш маршрут.', ''),
 ('Чи можна налаштувати гучність у навушниках?', 'Так. У навушниках є регулятор та обмежувач гучності, а кожен учасник може налаштувати рівень звуку для себе. Обмежувач допомагає контролювати рівень звуку, але не є гарантією абсолютної безпеки для слуху.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="tours_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="tours_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштує радіогід для екскурсії</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо маршрут має особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте екскурсію? Обговорімо маршрут</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про маршрут, групу й дату. Ми підкажемо, як організувати звук, щоб гіда чули всі, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Дата, місце старту та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">радіогід</span> для екскурсії</h2>')
rep('зв’яжемося з вами, щоб узгодити формат і технічні деталі.</p>', 'зв’яжемося з вами, щоб узгодити маршрут і технічні деталі.</p>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Екскурсія</option>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x and 'конференції й виставки' not in x and '"/experiences/conferences/"' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
