"""Одноразовий генератор сторінки /experiences/dj-set/ (діджей-сет наживо в навушниках, 14.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Факти погоджено з власником 14.11.2026: діджея запрошує клієнт; діджей
грає на своїй апаратурі (пульт, ноутбук), SILENT підключає її вихід до передавача; одночасно до трьох діджеїв,
кожен на своєму каналі; на вільних каналах можуть звучати плейлисти SILENT; умови як для всіх форматів.
Запити з підказок Google: «діджей сет», «silent disco dj (battle, set)».
Запуск: python3 tools/gen_dj_page.py  (далі python3 tools/build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'dj-set', 'index.html')
IMG = '../../images/dj-set/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'dj-set', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

# Фото (14.11.2026): згенеровані в ChatGPT власника за референсом його навушників; вихідники inbox/dj-set/gen/.
ROOF = 'dj-set-na-dakhu-na-zakhodi.webp'
BOOTH = 'dj-za-pultom-krupno.webp'
BATTLE = 'dj-batl-dva-pulty.webp'
CORP = 'dj-set-na-korporatyvi-u-lofti.webp'
WED = 'dj-set-na-vesilli-v-sadu.webp'
FEST = 'dj-set-na-festyvali-pid-shatrom.webp'
MUSEUM = 'dj-set-u-muzei.webp'
HANDS = 'dj-za-pultom-u-sadu.webp'
SWITCH = 'hostia-peremykaie-kanal.webp'
TABLE = 'navushnyky-na-stoli-dj.webp'
YARD = 'dj-set-u-dvori-vnochi.webp'
BEACH = 'dj-set-na-plyazhi.webp'
POOL = 'dj-set-bilia-baseinu.webp'
OFFICE = 'dj-set-v-ofisi-pislia-roboty.webp'
POV = 'natovp-ochyma-dj.webp'
FRIENDS = 'druzi-smiiutsia-na-dj-seti.webp'
HANDOUT = 'vydacha-navushnykiv-hostiam.webp'
CABLE = 'tekhnik-pereviriaie-navushnyky.webp'
FINAL = 'finalnyi-set-ruky-vhoru.webp'

TITLE = 'Діджей-сет у навушниках: до трьох діджеїв одночасно | SILENT'
DESC = ('Діджей-сет наживо в бездротових навушниках: ваш діджей грає, гості чують сет у навушниках, а довкола тихо. '
        'До трьох діджеїв на трьох каналах. Київ і виїзд по Україні.')
OG_T = 'Діджей-сет наживо в бездротових навушниках | SILENT'
OG_D = 'Ваш діджей грає, гості чують сет у бездротових навушниках, а довкола тихо. До трьох діджеїв одночасно.'
OG_ALT = 'Діджей грає наживо, гості танцюють у бездротових навушниках SILENT з піднятими руками'

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
rep('images/conferences/og-conferences.jpg', 'images/dj-set/og-dj-set.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Діджей-сет наживо",')
rep('"name": "Silent Disco для конференцій"', '"name": "Діджей-сет у навушниках від SILENT"')
rep('"serviceType": "Silent disco"', '"serviceType": "Silent disco з живим діджеєм"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Організатори вечірок, корпоративів, весіль, фестивалів і діджеї"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-14"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/dj-set/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/dj-set/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/dj-set/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Діджей-сет наживо</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Діджей-сет наживо</span> <span class="t-sub">у бездротових навушниках SILENT</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Ваш діджей грає наживо, а гості чують сет у бездротових навушниках, тож довкола тихо: можна на даху, просто неба чи там, де звук обмежений. До трьох діджеїв одночасно, кожен на своєму каналі. SILENT підключає пульт, видає навушники й супроводжує вечір.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="djset_hero_order">Обговорити сет</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>До 3 діджеїв</b> <span>Кожен на своєму каналі.</span></span>')

gal1 = [(YARD, '50% 45%'), (BEACH, '50% 45%'), (POOL, '50% 45%')]
gal2 = [(OFFICE, '50% 45%'), (POV, '50% 45%'), (FRIENDS, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому діджей у навушниках ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ ДІДЖЕЙ-СЕТ У НАВУШНИКАХ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="dj-set">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Діджей у навушниках SILENT грає сет за пультом, позаду танцюють гості"' % (IMG, BOOTH))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Гостя торкається чаші навушників SILENT, щоб перемкнутися на інший канал"' % (IMG, SWITCH))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Навушники SILENT лежать на столі поруч із діджейським пультом"' % (IMG, TABLE))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Живий сет там, де колонки недоречні</h2>\n'
    '      <p>Дах із видом на місто, двір історичного будинку, тераса ресторану чи зал музею: саме тут найкраще звучить живий сет, і саме тут найчастіше кажуть «після десятої тихо» або «колонки не можна».</p>\n'
    '      <p>У форматі SILENT діджей грає як завжди, на своєму пульті, а звук іде не в колонки, а в бездротові навушники гостей. На танцполі драйв, а за двадцять метрів тиша, і вечір не впирається в сусідів чи правила локації.</p>\n'
    '      <p>У навушниках три канали. На кожному може грати окремий діджей, а якщо діджей один, на вільних каналах звучать плейлисти SILENT. Колір підсвітки показує, хто кого слухає.</p>\n'
    '      <p class="story-sub story-close">Живий сет. До трьох діджеїв. Ззовні тиша.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де живий сет у навушниках особливо доречний</h2>')
cards = [
    (ROOF, '50% 45%', 'Діджей грає на даху на заході сонця, гості танцюють у навушниках SILENT', 'Дахи, тераси й просто неба',
     'Захід сонця, вид на місто й живий сет без скарг від сусідів: звук лишається в навушниках гостей, тож вечір можна не згортати о десятій.'),
    (BATTLE, '50% 45%', 'Діджей-батл: два пульти поруч, гості в червоних і синіх навушниках', 'Діджей-батл',
     'Два чи три діджеї грають одночасно, кожен на своєму каналі, а гості голосують ногами, перемикаючись між ними. Колір підсвітки показує, хто веде.'),
    (CORP, '50% 45%', 'Корпоратив у лофті: діджей грає, колеги танцюють у навушниках SILENT', 'Корпоративи',
     'Діджей-сет в офісі, лофті чи ресторані без проблем зі звуком. Хто хоче поговорити, знімає навушники на шию, а танцпол живе далі.'),
    (WED, '50% 40%', 'Весільна вечірка в саду: діджей за пультом, гості танцюють у навушниках SILENT', 'Весілля й афтепаті',
     'Ваш весільний діджей продовжує сет після того, як локація просить вимкнути колонки. Молодь на одному каналі, батьки на іншому.'),
    (FEST, '50% 45%', 'Тихий танцпол під шатром на фестивалі, діджей грає для гостей у навушниках', 'Фестивалі й міські події',
     'Окрема тиха сцена, яка не перекрикує головну: діджеї грають у навушники, а танцпол світиться кольорами каналів.'),
    (MUSEUM, '50% 45%', 'Нічний діджей-сет у залі музею, гості танцюють серед експонатів у навушниках', 'Незвичні локації',
     'Музей, галерея, бібліотека чи двір пам’ятки: живий сет там, де звичайна вечірка неможлива через акустику чи правила.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працює діджей-сет у навушниках</h2>')
rep_re(r'(<h2 class="exp-h2">Як працює діджей-сет у навушниках</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Діджей грає на своєму пульті</b> <span>Діджей приходить зі своєю апаратурою, а SILENT підключає її вихід до передавача. Звук іде в бездротові навушники гостей, а не в колонки.</span></li>\n'
    '        <li><b>До трьох діджеїв одночасно</b> <span>Кожен діджей грає на своєму каналі. Якщо діджей один, на вільних каналах звучать плейлисти SILENT.</span></li>\n'
    '        <li><b>Гість обирає, кого слухати</b> <span>Канал перемикається одним дотиком, а колір підсвітки показує, хто на якому сеті. У кожного свій регулятор гучності.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, підключає пульти, видає навушники, супроводжує вечір і збирає комплект після завершення відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Технічну частину сету беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p><a href="/">SILENT</a> — це не просто навушники. Діджея запрошуєте ви, а ми робимо так, щоб його сет почули всі гості: привозимо систему, підключаємо пульт і супроводжуємо вечір.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для всіх гостей;</span></li>\n'
    '        <li><span>передавач і підключення пульта кожного діджея;</span></li>\n'
    '        <li><span>плейлисти SILENT на вільних каналах;</span></li>\n'
    '        <li><span>видача навушників на вході й збір наприкінці;</span></li>\n'
    '        <li><span>технічний супровід протягом вечора.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Гостям на вході видають навушники SILENT перед діджей-сетом"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Діджей у навушниках SILENT за пультом на вечірці в саду"' % (IMG, HANDS))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT перевіряє навушники перед вечіркою біля кейса з комплектом"' % (IMG, CABLE))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від ідеї до першого треку</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з локації, кількості гостей і того, скільки діджеїв гратиме. На цій основі визначаємо комплект і логістику.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Фінальний сет вечора: натовп у навушниках SILENT з піднятими руками"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, локацію, кількість гостей і скільки діджеїв гратиме.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, канали для діджеїв і плейлистів, місце для пульта й живлення.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час монтажу, підключення апаратури діджеїв і видачу навушників.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо вечір</h3>\n        <p>Підключаємо пульти, перевіряємо звук із кожним діджеєм, видаємо навушники й збираємо їх після завершення відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="djset_process_order">Обговорити сет</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="party"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Діджей-сет наживо" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Живий сет лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/silent-disco/">Silent Disco з плейлистами</a>, <a href="/experiences/corporate/">корпоративи</a>, <a href="/experiences/wedding/">весілля</a> і <a href="/experiences/festivals/">фестивалі</a>. Поради для вечірок шукайте в <a href="/blog/">блозі</a>: <a href="/blog/vechirka-bez-shumu-sysidy/">як провести вечірку, щоб не заважати сусідам</a> і <a href="/blog/afterparty-festyvalyu/">афтепаті фестивалю</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про діджей-сет у навушниках')
Q = [
 ('Чи надаєте ви діджея?', 'Ні, діджея запрошуєте ви. SILENT забезпечує технічну частину: підключає апаратуру діджея до передавача, видає гостям навушники й супроводжує вечір.', ''),
 ('Скільки діджеїв можуть грати одночасно?', 'До трьох. Кожен діджей грає на своєму каналі, а гості перемикаються між сетами одним дотиком.', ''),
 ('На якій апаратурі грає діджей?', 'На своїй: пульт, ноутбук чи інша апаратура, з якою він звик грати. SILENT підключає її вихід до передавача й перевіряє звук до старту.', ''),
 ('Що звучить на каналах, де не грає діджей?', 'Плейлисти SILENT, які ми готуємо наперед під формат вечора. Так у гостей завжди є вибір, навіть якщо діджей один.', ''),
 ('Скільки коштує діджей-сет у навушниках?', 'Базовий орієнтир — від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників. Гонорар діджея в цю суму не входить.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Чи можна провести сет просто неба?', 'Так, якщо поруч є живлення для пульта й передавача і є запасний план на дощ: намет, навіс чи приміщення. Умови локації обговорюємо заздалегідь.', ''),
 ('Чи можна налаштувати гучність у навушниках?', 'Так. У навушниках є регулятор та обмежувач гучності, а кожен гість налаштовує рівень звуку для себе. Обмежувач допомагає контролювати рівень звуку, але не є гарантією абсолютної безпеки для слуху.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="djset_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="djset_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштує діджей-сет у навушниках</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Гонорар діджея у вартість не входить. Якщо діджеїв кілька чи локація має особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте вечір із діджеєм? Обговорімо сет</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про локацію, кількість гостей і діджеїв. Ми підкажемо, як зробити живий сет у навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Дата, локація, кількість діджеїв і приблизна кількість гостей — цього достатньо, щоб почати розмову.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">діджей-сет</span> у навушниках</h2>')
rep('зв’яжемося з вами, щоб узгодити формат і технічні деталі.</p>', 'зв’яжемося з вами, щоб узгодити сет і технічні деталі.</p>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Діджей-сет</option>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
