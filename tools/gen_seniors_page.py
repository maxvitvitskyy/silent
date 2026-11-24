"""Одноразовий генератор сторінки /experiences/seniors/ (події для літніх, 24.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: вечір для друзів і родини, танцювальні вечори для 55+,
будинки й центри для літніх, екскурсії та лекції. Ведучого (гіда, лектора, співака) запрошує клієнт; голос іде через
портативний передавач із мікрофоном (дає SILENT). НЕ обіцяємо: дальності сигналу, впливу на слух чи здоров'я,
сумісності зі слуховими апаратами. Єдина обіцянка: власна гучність у кожному навушнику.
Фото: 19 кадрів із ChatGPT (inbox/seniors/gen → convert.py → images/seniors/); ведучий без навушників, з окремою
гарнітурою й одним передавачем; глядачі в навушниках одного кольору.
Запуск: python3 tools/gen_seniors_page.py (далі build_en.py). УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'seniors', 'index.html')
IMG = '../../images/seniors/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'seniors', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

DANCE = 'retro-vechir-dlia-55-plius.webp'                # 01 картка 3:2
SERENE = 'zhinka-v-navushnykakh-z-zakrytymy-ochyma.webp' # 02 «Чому» 2:3
FAMILY = 'simeine-sviato-za-stolom.webp'                 # 03 картка 3:2
GARDEN = 'vechir-druziv-u-sadu.webp'                     # 04 картка 3:2
CENTER = 'kontsert-u-tsentri-dlia-litnikh.webp'          # 05 картка 3:2
TOUR = 'ekskursiia-mistom-z-hidom.webp'                  # 06 картка 3:2
LECTURE = 'lektsiia-v-klubi.webp'                        # 07 картка 3:2
PORTRAIT = 'portret-usmikhnenoho-cholovika.webp'         # 08 квадрат («Чому» s-a)
COUPLE = 'para-povilno-tantsiuie.webp'                   # 09 квадрат («Чому» s-b)
G1 = 'zhinka-smiietsia-vidkynuvshy-holovu.webp'          # 10 колаж 4:5
G2 = 'cholovik-vystukuie-ritm.webp'                      # 11
G3 = 'dvi-podruhy-smiiutsia.webp'                        # 12
G4 = 'litnii-cholovik-z-radistiu.webp'                   # 13
G5 = 'zhinka-tantsiuie-pidnialy-ruky.webp'               # 14
G6 = 'para-trymaietsia-za-ruky.webp'                     # 15
HANDOUT = 'vydacha-navushnykiv-bilia-zalu.webp'          # 16 2:3 («Що входить» s-main)
LEADER = 'hid-hovoryt-do-hrupy.webp'                     # 17 квадрат («Що входить» s-a)
TECH = 'tekhnik-nalashtovuie-harnituru-lektoru.webp'     # 18 4:5 («Що входить» s-b)
FINAL = 'zal-tantsiu-i-slukhannia.webp'                  # 19 16:9 («Як замовити»)

TITLE = 'Події для літніх: навушники з власною гучністю | SILENT'
DESC = 'Бездротові навушники для вечорів, танців, екскурсій і лекцій для літніх людей: знайома музика й голос ведучого, а гучність кожен обирає сам. Київ і по Україні.'
OG_T = TITLE
OG_D = 'Вечори, танці, екскурсії й лекції для літніх: знайома музика й голос ведучого звучать у навушниках, а гучність кожен обирає сам.'
OG_ALT = 'Літні люди танцюють у бездротових навушниках SILENT у світлій залі, усі усміхаються'

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
rep('images/conferences/og-conferences.jpg', 'images/seniors/og-seniors.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Події для літніх",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для подій для літніх людей"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для подій для літніх"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Родини, клуби за інтересами, центри для літніх, організатори екскурсій і лекцій"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-24"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/seniors/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/seniors/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/seniors/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Події для літніх</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Події<br>для літніх<br>у навушниках</span> <span class="t-sub">знайома музика й голос ведучого, а гучність обирає кожен</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Ретро-вечір, сімейне свято, екскурсія чи лекція: у бездротових навушниках SILENT музика й голос ведучого звучать просто у вусі кожного гостя. Гучність у кожного своя, а гучних колонок немає. SILENT видає навушники й налаштовує передавач.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="seniors_hero_order">Обговорити подію</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Власна гучність</b> <span>у кожному навушнику.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ ДЛЯ ЛІТНІХ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="seniors">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Літня жінка зі сріблястим волоссям слухає музику із заплющеними очима й усмішкою в навушниках SILENT"' % (IMG, SERENE))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Усміхнений чоловік із сивою бородою в навушниках SILENT" ' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Літня пара повільно танцює й усміхається одне одному в навушниках SILENT"' % (IMG, COUPLE))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Музика й голос, які чути кожному</h2>\n'
    '      <p>На святі чи лекції важливо чути все, що звучить. У залі, на вулиці чи в групі на екскурсії частина гостей ловить лише уривки, а гучні колонки не підходять усім: комусь замало, комусь забагато.</p>\n'
    '      <p>У бездротових навушниках SILENT музика й голос ведучого звучать просто у вусі кожного, а гучність гість налаштовує сам. Один обирає тихіше, інший гучніше, і ніхто не заважає сусідові.</p>\n'
    '      <p>Ведучого, гіда чи лектора запрошуєте ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT. Якщо потрібна музика до виступу чи після нього, попередьте команду, ми налаштуємо.</p>\n'
    '      <p class="story-sub story-close">Знайома музика. Ясний голос. Своя гучність.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де навушники для літніх працюють особливо добре</h2>')
cards = [
    (DANCE, '50% 45%', 'Літні люди танцюють парами й групами в світлій залі, усі в синіх навушниках SILENT', 'Танцювальний вечір для 55+',
     'Знайомі мелодії молодості звучать у навушниках, а танцпол вільний. Кожен слухає з такою гучністю, яка зручна саме йому.'),
    (FAMILY, '50% 45%', 'Родинне свято за довгим столом: бабусі, дідусі, діти й онуки усміхаються в зелених навушниках SILENT', 'Сімейне свято й ювілей',
     'За одним столом бабусі, батьки й онуки. Музика звучить у навушниках, тож розмова не губиться, а гучність кожен підбирає сам.'),
    (GARDEN, '50% 45%', 'Вечір друзів у саду під гірляндами: літні люди сміються за столом із чаєм у навушниках SILENT', 'Вечір друзів у саду',
     'Чай, затишне світло й улюблені пісні для компанії. Ніяких колонок, які заважають сусідам чи тихому вечору.'),
    (CENTER, '50% 45%', 'Концерт у світлій залі громадського центру: літні слухачі в зручних кріслах у синіх навушниках SILENT', 'Концерт у центрі для літніх',
     'Співак чи музикант виступає, а слухачі в зручних кріслах чують усе чітко. Порядок видачі й супровід погоджуємо заздалегідь.'),
    (TOUR, '50% 45%', 'Літня група йде вузькою вулицею старого міста за гідом із піднятою рукою, усі в навушниках SILENT', 'Екскурсія з гідом',
     'Гід іде з групою й говорить у мікрофон передавача, а голос звучить у навушниках кожного. Чути навіть на людній вулиці.'),
    (LECTURE, '50% 45%', 'Лекція в залі клубу: літні слухачі з блокнотами в зелених навушниках SILENT, лектор біля екрана', 'Лекція в клубі за інтересами',
     'Лектор говорить спокійно, а голос чути чітко з будь-якого ряду. Гучність кожен налаштовує сам, а нотатки не завадять слуханню.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на події для літніх</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на події для літніх</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Власна гучність</b> <span>У кожних навушниках є регулятор: гість сам обирає, наскільки гучно слухати.</span></li>\n'
    '        <li><b>Знайома музика</b> <span>Плейлисти SILENT можна зібрати з пісень, які люблять гості. Розкажіть про вечір, і ми підкажемо, як їх налаштувати.</span></li>\n'
    '        <li><b>Голос ведучого</b> <span>Ведучого, гіда чи лектора запрошуєте ви. Він бере портативний передавач із мікрофоном, а SILENT налаштовує його перед початком.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники гостям, супроводжує подію й збирає комплект відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук події беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви обираєте формат і запрошуєте ведучого, а <a href="/">SILENT</a> відповідає за навушники, мікрофон і передавач: щоб кожен гість чув усе чітко й сам керував гучністю.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для гостей із регулятором гучності;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого, гіда чи лектора;</span></li>\n'
    '        <li><span>плейлисти SILENT для музики на вечорі;</span></li>\n'
    '        <li><span>видача навушників на вході й збір після події;</span></li>\n'
    '        <li><span>технічний супровід протягом заходу.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT біля входу в залу віддає літній жінці навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Гід говорить до групи літніх людей на історичній площі, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає лекторові закріпити гарнітуру, у руці в лектора портативний передавач"' % (IMG, TECH))

# обличчя на кадрі техніка біля верхнього краю: піднімаємо кадр, щоб не різало голови (24.11.2026)
rep_re(r'<img style="object-position:50% 50%"( width="1254" height="1254" class="s-b" src="[^"]*tekhnik-nalashtovuie-harnituru-lektoru\.webp")',
       r'<img style="object-position:50% 8%"\g<1>')

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від дати до першої мелодії</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату події, місця й кількості гостей. На цій основі визначаємо комплект і те, чи потрібен голос ведучого та музика.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Світла зала: літні люди танцюють і слухають музику, усі усміхаються в синіх навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат події, кількість гостей і чи потрібен голос ведучого.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофон для ведучого, музику й порядок видачі.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників гостям.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо подію</h3>\n        <p>Налаштовуємо передавач, перевіряємо звук разом із ведучим, видаємо навушники й збираємо комплект після відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="seniors_process_order">Обговорити подію</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="community"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Події для літніх" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Події для літніх лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/tours/">екскурсії з радіогідом</a>, <a href="/experiences/chamber-concerts/">камерні концерти</a>, <a href="/experiences/inclusive/">інклюзивні події</a> і <a href="/experiences/birthday/">дні народження</a>. Поради шукайте в <a href="/blog/">блозі</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на події для літніх')
Q = [
 ('Чи можна кожному налаштувати гучність?', 'Так. У кожних навушниках є регулятор гучності, тож гість сам обирає, наскільки гучно слухати.', ''),
 ('Чи підходить формат для літніх людей?', 'Так, навушники зручно одягати й знімати, гучність гість налаштовує сам, а музика й голос ведучого звучать просто у вусі. Деталі події узгоджуємо заздалегідь.', ''),
 ('Чи можна поставити знайому музику?', 'Так. Плейлисти SILENT можна зібрати з пісень, які люблять ваші гості. Розкажіть про вечір, і ми підкажемо, як усе налаштувати.', ''),
 ('Чи надаєте ви гіда чи лектора?', 'Ні, гіда, лектора чи ведучого запрошуєте ви. SILENT дає навушники, портативний передавач із мікрофоном і супроводжує подію.', ''),
 ('Чи потрібні колонки?', 'Ні. Музика й голос ведучого звучать у навушниках, тому гучні колонки не потрібні.', ''),
 ('Скільки коштують навушники для події?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники гостям і збираємо після події. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="seniors_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="seniors_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для події для літніх</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові канали чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте подію для літніх? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про подію, гостей і місце. Ми підкажемо, як налаштувати музику й голос ведучого в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості гостей.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для події для літніх</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Подія для літніх</option>')
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
