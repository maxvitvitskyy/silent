"""Одноразовий генератор сторінки /experiences/workshops/ (майстеркласи, 20.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: творчі (малювання, кераміка, декор), кулінарні
(шеф, бариста, коктейлі), корпоративні для команди, дитячі й сімейні. До трьох майстрів одночасно, кожен на
своєму каналі (рішення власника). Майстра запрошує клієнт; передавач із мікрофоном і плейлисти дає SILENT.
НЕ обіцяємо: результату навчання, безпеки слуху, дальності сигналу.
Фото: 19 кадрів із ChatGPT (inbox/workshops/gen → convert.py → images/workshops/); у кожній сцені навушники
одного кольору, окрім кадру «три зони» (група = колір). Запуск: python3 tools/gen_workshops_page.py (далі build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'workshops', 'index.html')
IMG = '../../images/workshops/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'workshops', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

STUDIO = 'hrupove-maliuvannia-v-studii.webp'                     # 01 картка 3:2 (сині)
POTTER = 'honcharnyi-maistryklas-honcharnyi-krug.webp'           # 02 «Чому» 2:3 (зелені)
CERAM = 'keramika-za-dovhym-stolom.webp'                         # 03 картка 3:2 (зелені)
CHEF = 'kulinarnyi-maistryklas-shef-na-kukhni.webp'              # 04 картка 3:2 (сині)
BAR = 'koktejli-v-bari-maistryklas.webp'                         # 05 картка 3:2 (сині)
TEAM = 'komandnyi-maistryklas-u-lofti.webp'                      # 06 картка 3:2 (зелені)
KIDS = 'simeinyi-maistryklas-dity-ta-batky.webp'                 # 07 картка 3:2 (сині)
PORTRAIT = 'portret-khudozhnytsi-pry-molberti.webp'              # 08 квадрат («Чому» s-a)
FRIENDS = 'chotyry-druzi-rozpysuiut-kruzhky.webp'                # 09 квадрат («Чому» s-b)
G1 = 'honcharnyi-krug-krupnym-planom.webp'                       # 10–15 колаж 4:5
G2 = 'kulinarnyi-maistryklas-narizannia-ovochiv.webp'
G3 = 'divchynka-rozfarbovuie-figurku.webp'
G4 = 'tato-z-donkoiu-maliuiut.webp'
G5 = 'zhinka-hlazuruie-misku.webp'
G6 = 'barysta-latte-art-maistryklas.webp'
HANDOUT = 'vydacha-navushnykiv-bilia-studii.webp'                # 16 2:3 («Що входить» s-main)
LEADER = 'maistryna-hovoryt-do-hrupy.webp'                       # 17 квадрат («Що входить» s-a)
TECH = 'tekhnik-nalashtovuie-mikrofon-maistru.webp'              # 18 4:5 («Що входить» s-b)
FINAL = 'try-zony-maistryklasiv-v-odnomu-prostori.webp'          # 19 16:9 («Як замовити»)

TITLE = 'Майстеркласи в навушниках: голос майстра кожному | SILENT'
DESC = 'Бездротові навушники для майстеркласів: голос майстра чути кожному учаснику, до трьох майстрів одночасно в одному просторі. Київ і виїзд по Україні.'
OG_T = 'Майстеркласи в навушниках: голос майстра кожному | SILENT'
OG_D = 'Малювання, кераміка, кулінарія, бар: голос майстра звучить у навушниках кожного учасника, до трьох майстрів одночасно, без колонок.'
OG_ALT = 'Учасники майстеркласу малюють у світлій студії в бездротових навушниках SILENT, майстриня показує техніку'

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
rep('images/conferences/og-conferences.jpg', 'images/workshops/og-workshops.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Майстеркласи",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для майстеркласів"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для майстеркласів"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Організатори майстеркласів, творчі студії, кулінарні школи та бари"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-20"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/workshops/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/workshops/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/workshops/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Майстеркласи</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Майстеркласи в навушниках</span> <span class="t-sub">голос майстра прямо у вусі кожного учасника</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Майстер говорить у мікрофон, а кожен учасник чує кожен крок у бездротових навушниках: біля мольберта, за гончарним колом чи на кухні. У просторі може працювати до трьох майстрів одночасно, кожен на своєму каналі. SILENT видає навушники й налаштовує передавач.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="workshops_hero_order">Обговорити майстерклас</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>До 3 майстрів</b> <span>кожен на своєму каналі.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА МАЙСТЕРКЛАСІ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="workshops">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Майстер гончарної справи показує жінці за гончарним колом, як формувати глину, обоє в навушниках SILENT"' % (IMG, POTTER))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Зосереджена жінка малює пензлем на мольберті в навушниках SILENT"' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Четверо друзів сміються й розписують керамічні кружки в навушниках SILENT"' % (IMG, FRIENDS))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Кожен крок майстра чути однаково добре</h2>\n'
    '      <p>На майстерклас люди приходять вчитися, а не перепитувати. У великій студії задні столи гірше чують майстра, на кухні заважають витяжка й посуд, а в барі музика перекриває пояснення.</p>\n'
    '      <p>У бездротових навушниках SILENT голос майстра звучить просто у вусі кожного учасника. Руки зайняті глиною, пензлем чи ножем, а слухати не треба напружуватись. У кожного свій регулятор гучності.</p>\n'
    '      <p>Майстра запрошуєте ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT, а спокійна музика звучить поруч із його голосом. Якщо в просторі працюють кілька майстрів, у кожного свій канал, а колір підсвітки показує, хто в якій групі.</p>\n'
    '      <p class="story-sub story-close">Голос майстра. Зайняті руки. Кожен чує.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де майстерклас у навушниках працює особливо добре</h2>')
cards = [
    (STUDIO, '50% 45%', 'Учасники малюють на мольбертах у світлій студії, майстриня показує техніку, усі в навушниках SILENT', 'Малювання в студії',
     'Майстриня ходить між мольбертами й показує техніку, а голос звучить у навушниках кожного, навіть у кінці залу.'),
    (CERAM, '50% 45%', 'Учасники ліплять із глини за довгими столами в кераміці, майстер показує попереду, усі в навушниках SILENT', 'Кераміка й гончарний круг',
     'Руки в глині, а підказки майстра чути без напруги: як центрувати глину, як тримати форму, коли зупинитися.'),
    (CHEF, '50% 45%', 'Учасники кулінарного майстеркласу готують за довгою стійкою, шеф показує попереду, усі в навушниках SILENT', 'Кулінарний майстерклас',
     'Шеф показує на кухні, а учасники чують його крізь шум витяжки й посуду. Перепитувати не треба.'),
    (BAR, '50% 45%', 'Гості слухають бармена біля барної стійки в навушниках SILENT, поки він готує коктейль', 'Бар і кава',
     'Бармен чи бариста пояснює склад і техніку біля стійки, а гості слухають зблизька, навіть коли в барі грає музика.'),
    (TEAM, '50% 45%', 'Колеги працюють руками за довгими столами в лофті, майстер їх веде, усі в навушниках SILENT', 'Майстерклас для команди',
     'Колеги працюють руками за довгими столами, а майстер веде їх голосом у навушниках. Тімбілдинг без гамору й перекрикування.'),
    (KIDS, '50% 45%', 'Діти й батьки розфарбовують глиняні фігурки за столами, ведуча допомагає, усі в навушниках SILENT', 'Дитячі й сімейні',
     'Діти й батьки малюють разом, а голос ведучої звучить у кожному навушнику однаково близько. У кожного свій регулятор гучності.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на майстеркласі</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на майстеркласі</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Голос майстра</b> <span>Майстра запрошуєте ви. Він бере портативний передавач із мікрофоном, а SILENT налаштовує його перед початком.</span></li>\n'
    '        <li><b>До трьох майстрів одночасно</b> <span>Кожен майстер працює на своєму каналі, а колір підсвітки навушників показує, хто в якій групі.</span></li>\n'
    '        <li><b>Музика поруч із голосом</b> <span>Спокійна музика звучить у навушниках разом із голосом. Попередьте команду, ми налаштуємо. У кожного свій регулятор гучності.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники учасникам, супроводжує майстерклас і збирає комплект відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук майстеркласу беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте програму й запрошуєте майстра, а <a href="/">SILENT</a> відповідає за навушники, мікрофон і передавач: щоб кожен учасник чув майстра без напруги.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для учасників;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для кожного майстра;</span></li>\n'
    '        <li><span>плейлисти SILENT зі спокійною музикою;</span></li>\n'
    '        <li><span>видача навушників на вході й збір після майстеркласу;</span></li>\n'
    '        <li><span>технічний супровід протягом заходу.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT біля входу в студію віддає учасниці навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Майстриня говорить до групи, на поясі в неї невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT налаштовує гарнітуру з мікрофоном майстру, у руці в нього портативний передавач"' % (IMG, TECH))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від задуму до першого пензля</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату майстеркласу й простору: скільки учасників, скільки майстрів і де вони працюють. На цій основі визначаємо комплект.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Просторий творчий зал із трьома зонами: малювання, кераміка й кулінарія, кожна група в навушниках SILENT свого кольору"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат майстеркласу, кількість майстрів і учасників.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофони й канали для майстрів та музику.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників учасникам.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо майстерклас</h3>\n        <p>Налаштовуємо передавачі, перевіряємо звук разом із майстром, видаємо навушники й збираємо їх після відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="workshops_process_order">Обговорити майстерклас</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="education"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Майстеркласи" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Майстерклас лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/trainings/">тренінги й навчання</a>, <a href="/experiences/corporate/">корпоративи</a>, <a href="/experiences/kids/">дитячі свята</a> і <a href="/experiences/museums/">музеї та галереї</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/idei-dlia-timbildynhu/">ідеї для тімбілдингу</a> і <a href="/blog/yak-provesty-treninh-dlia-velykoi-hrupy/">як провести тренінг для великої групи</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на майстеркласі')
Q = [
 ('Чи надаєте ви майстра?', 'Ні, майстра запрошуєте ви. SILENT дає навушники, портативний передавач із мікрофоном і супроводжує захід.', ''),
 ('Скільки майстрів можуть працювати одночасно?', 'До трьох. Кожен майстер працює на своєму каналі, а колір підсвітки навушників показує, хто в якій групі.', ''),
 ('Як голос майстра потрапляє в навушники?', 'Майстер говорить у мікрофон портативного передавача, який налаштовує SILENT. Передавач віддає голос у бездротові навушники учасників, і в кожного є свій регулятор гучності.', ''),
 ('Чи можна пустити музику разом із голосом?', 'Так. Попередьте команду, і ми налаштуємо так, щоб голос майстра й музика звучали в навушниках разом.', ''),
 ('Чи підійде формат для кухні чи бару?', 'Так, навушники бездротові, тож майстерклас можна провести на кухні, біля барної стійки чи в студії. Живлення для передавача й порядок видачі навушників узгоджуємо заздалегідь.', ''),
 ('Скільки коштують навушники для майстеркласу?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники учасникам і збираємо після майстеркласу. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="workshops_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="workshops_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для майстеркласу</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні кілька майстрів чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте майстерклас? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про майстерклас, простір і кількість учасників. Ми підкажемо, як налаштувати голос майстра й музику в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості учасників.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для майстеркласу</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Майстерклас</option>')
rep('Залиште заявку — перевіримо доступність обладнання та зв’яжемося з вами, щоб узгодити формат і технічні деталі.', 'Залиште заявку, ми перевіримо доступність обладнання та зв’яжемося з вами, щоб узгодити формат і технічні деталі.')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x and 'conferences/' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
old = 'object-position:50% 50%" width="1254" height="1254" class="s-b" src="' + IMG + TECH + '"'
if s.count(old) == 1:
    s = s.replace(old, old.replace('50% 50%', '50% 14%'))
else:
    print('УВАГА: рядок s-b для техніка не знайдено, object-position не змінено')
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
