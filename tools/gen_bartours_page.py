"""Одноразовий генератор сторінки /experiences/bartours/ (бар-тури, 24.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: маршрут барами міста, дівич-вечір і день народження,
корпоративний бар-тур, тур із гідом-ведучим. Ведучого (гіда) запрошує клієнт; голос іде через портативний
передавач із мікрофоном (дає SILENT); навушники на старті видає й на фініші збирає команда SILENT. НЕ обіцяємо:
дальності сигналу, безпеки слуху, домовленостей із закладами. Про алкоголь не пишемо.
Фото: 19 кадрів із ChatGPT (inbox/bartours/gen → convert.py → images/bartours/); ведучий без навушників, з
гарнітурою й одним передавачем; гості в навушниках одного кольору.
Запуск: python3 tools/gen_bartours_page.py (далі build_en.py). УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'bartours', 'index.html')
IMG = '../../images/bartours/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'bartours', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

ROUTE = 'hrupa-druziv-yde-vulytseiu-mizh-barami.webp'   # 01 картка 3:2
LAUGH = 'divchyna-smiietsia-na-nichnii-vulytsi.webp'     # 02 «Чому» 2:3
HEN = 'divych-vechir-u-koktelnomu-bari.webp'              # 03 картка 3:2
BDAY = 'den-narodzhennia-u-bari.webp'                     # 04 картка 3:2
CORP = 'koleh-u-kraftovomu-bari.webp'                     # 05 картка 3:2
GUIDE = 'bar-tur-z-vedouchym-staroiu-vulytseiu.webp'      # 06 картка 3:2
DANCE = 'tantsi-bilia-vkhodu-v-bar.webp'                  # 07 картка 3:2
PORTRAIT = 'portret-cholovika-shcho-smiietsia.webp'       # 08 квадрат («Чому» s-a)
CHEERS = 'dvoie-druziv-chokaiutsia-koktelyamy.webp'       # 09 квадрат («Чому» s-b)
G1 = 'zhinka-tantsiuie-pidnialy-ruky.webp'                # 10 колаж 4:5
G2 = 'cholovik-kyvaie-holovoiu-pid-muzyku.webp'           # 11
G3 = 'dvi-podruhy-obiimaiutsia.webp'                      # 12
G4 = 'khlopets-spivaie-zakryvshy-ochi.webp'               # 13
G5 = 'zhinka-dyvytsia-na-nichne-nebo.webp'                # 14
G6 = 'para-smiietsia-bilia-baru.webp'                     # 15
HANDOUT = 'vydacha-navushnykiv-na-starti.webp'            # 16 2:3
LEADER = 'vedouchyi-hovoryt-do-hrupy.webp'                # 17 квадрат
TECH = 'tekhnik-nalashtovuie-harnituru-vedouchomu.webp'   # 18 4:5
FINAL = 'pishokhidna-vulytsia-nochi-hrupa-tantsiuie.webp' # 19 16:9

TITLE = 'Бар-тури з навушниками: музика йде з вами | SILENT'
DESC = 'Бездротові навушники для бар-турів, дівич-вечорів і корпоративів: музика й голос ведучого йдуть із групою від бару до бару, без колонок. Київ і по Україні.'
OG_T = TITLE
OG_D = 'Бар-тур у навушниках: музика й голос ведучого звучать у кожного гостя, а вечірка не залежить від колонок у закладі.'
OG_ALT = 'Група друзів іде нічною вулицею між барами, усі сміються в бездротових навушниках SILENT'

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
rep('images/conferences/og-conferences.jpg', 'images/bartours/og-bartours.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Бар-тури",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для бар-турів"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для бар-турів"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Компанії друзів, організатори дівич-вечорів, корпоративних бар-турів і міських подій"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-24"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/bartours/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/bartours/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/bartours/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Бар-тури</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Бар-тури<br>з музикою<br>в навушниках</span> <span class="t-sub">музика й голос ведучого йдуть із вами від бару до бару</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Група йде від бару до бару, а музика й голос ведучого звучать просто у вусі кожного гостя. Вечірка не залежить від колонок у закладі, а гучність у кожного своя. SILENT видає навушники на старті, налаштовує передавач і збирає комплект на фініші.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="bartours_hero_order">Обговорити бар-тур</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Музика з вами</b> <span>від бару до бару.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА БАР-ТУРІ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="bartours">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Молода жінка щиро сміється на нічній вулиці серед тепло освітлених барів у навушниках SILENT"' % (IMG, LAUGH))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Усміхнений чоловік сміється на нічній вулиці в навушниках SILENT"' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Двоє друзів усміхаються біля барної стійки в навушниках SILENT"' % (IMG, CHEERS))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Музика, яка йде з вами</h2>\n'
    '      <p>На бар-турі компанія щоразу переходить в нове місце, і кожен заклад грає свою музику. Вечірка то стихає, то заважає розмові, а настрій групи розсипається.</p>\n'
    '      <p>У бездротових навушниках SILENT музика й голос ведучого звучать просто у вусі кожного, а гучність гість налаштовує сам. Музика йде з групою від бару до бару й не залежить від колонок у закладі.</p>\n'
    '      <p>Ведучого чи гіда запрошуєте ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT. На одному каналі може звучати голос ведучого, на іншому музика: попередьте команду, ми налаштуємо.</p>\n'
    '      <p class="story-sub story-close">Одна компанія. Один маршрут. Одна музика на всіх.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де бар-тур у навушниках працює особливо добре</h2>')
cards = [
    (ROUTE, '50% 45%', 'Група друзів іде вечірньою вулицею між барами з теплими вікнами, усі в синіх навушниках SILENT', 'Маршрут барами міста',
     'Компанія йде від бару до бару, а музика йде разом із нею. Заклади змінюються, настрій вечора лишається.'),
    (HEN, '50% 45%', 'Дівич-вечір у стильному коктейль-барі: подруги сміються й підіймають келихи в червоних навушниках SILENT', 'Дівич-вечір',
     'Подруги, спільний плейлист і вечір, який не залежить від колонок у закладі. Усі чують музику й одна одну.'),
    (BDAY, '50% 45%', 'День народження в барі: друзі навколо високого столу з кульками й тортом сміються в зелених навушниках SILENT', 'День народження',
     'Святкова компанія й музика в навушниках: іменинник обирає плейлист, а гості підбирають гучність.'),
    (CORP, '50% 45%', 'Колеги в крафтовому барі за довгим дерев’яним столом сміються в синіх навушниках SILENT', 'Корпоративний бар-тур',
     'Команда знайомиться в неформальному форматі: маршрут, ведучий і музика на всіх, без нав’язливих колонок.'),
    (GUIDE, '50% 45%', 'Бар-тур зі старого міста: ведучий із піднятою рукою йде попереду групи, усі гості в синіх навушниках SILENT', 'Тур із гідом-ведучим',
     'Ведучий іде з групою й говорить у мікрофон передавача: розповідає про місця, дає завдання, веде конкурси. Голос чути кожному.'),
    (DANCE, '50% 45%', 'Друзі танцюють біля входу в бар з теплим світлом у зелених навушниках SILENT', 'Зупинка з танцями',
     'Між барами група може зупинитися й потанцювати під спільну музику в навушниках. Тихіше для всіх навколо.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на бар-турі</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на бар-турі</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Музика з групою</b> <span>Плейлист SILENT звучить у навушниках усієї компанії й іде з нею від бару до бару.</span></li>\n'
    '        <li><b>Голос ведучого</b> <span>Ведучого чи гіда запрошуєте ви. Він бере портативний передавач із мікрофоном, а SILENT налаштовує його перед стартом.</span></li>\n'
    '        <li><b>Власна гучність</b> <span>У кожних навушниках є регулятор: гість сам обирає, наскільки гучно слухати. Попередьте команду, якщо потрібні окремі канали для голосу й музики.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT видає навушники на старті, налаштовує обладнання, супроводжує бар-тур і збирає комплект на фініші відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук бар-туру беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви обираєте маршрут і запрошуєте ведучого, а <a href="/">SILENT</a> відповідає за навушники, мікрофон і передавач: щоб кожен гість чув усе чітко й сам керував гучністю.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для гостей із регулятором гучності;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого чи гіда;</span></li>\n'
    '        <li><span>плейлисти SILENT для музики на маршруті;</span></li>\n'
    '        <li><span>видача навушників на старті й збір на фініші;</span></li>\n'
    '        <li><span>технічний супровід протягом бар-туру.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT на старті маршруту віддає гостеві навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Ведучий бар-туру говорить до групи на вулиці, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає ведучому закріпити гарнітуру, у руці в ведучого портативний передавач"' % (IMG, TECH))
# обличчя на кадрі техніка біля верхнього краю: піднімаємо кадр
rep_re(r'<img style="object-position:50% 50%"( width="1254" height="1254" class="s-b" src="[^"]*tekhnik-nalashtovuie-harnituru-vedouchomu\.webp")',
       r'<img style="object-position:50% 8%"\g<1>')

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від дати до першої зупинки</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату бар-туру, маршруту й кількості гостей. На цій основі визначаємо комплект і те, чи потрібні окремі канали для голосу й музики.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent DISCO"'.replace('DISCO','Disco'),
    'src="%s%s" alt="Нічна пішохідна вулиця: група друзів іде й танцює між барами в синіх навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, район маршруту, формат бар-туру, кількість гостей і чи потрібен голос ведучого.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофон для ведучого, музику й канали.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо точку старту, час налаштування й порядок видачі навушників гостям.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо бар-тур</h3>\n        <p>Налаштовуємо передавач, перевіряємо звук разом із ведучим, видаємо навушники на старті й збираємо комплект на фініші відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="bartours_process_order">Обговорити бар-тур</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="party"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Бар-тури" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Бар-тур лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/hen-party/">дівич-вечір</a>, <a href="/experiences/birthday/">дні народження</a>, <a href="/experiences/runs-walks/">забіги та прогулянки</a> і <a href="/experiences/corporate/">корпоративи</a>. Поради шукайте в <a href="/blog/">блозі</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на бар-турі')
Q = [
 ('Чи потрібна музика в самих барах?', 'Ні. Музика звучить у навушниках, тож вечірка не залежить від колонок у закладі.', ''),
 ('Чи надаєте ви ведучого чи гіда?', 'Ні, ведучого чи гіда запрошуєте ви. SILENT дає навушники, портативний передавач із мікрофоном і супроводжує бар-тур.', ''),
 ('Як голос ведучого потрапляє в навушники?', 'Ведучий говорить у мікрофон портативного передавача, який налаштовує SILENT. Передавач віддає голос у бездротові навушники гостей.', ''),
 ('Чи можна кожному налаштувати гучність?', 'Так. У кожних навушниках є регулятор гучності, тож гість сам обирає, наскільки гучно слухати.', ''),
 ('Чи можна окремо голос ведучого й музику?', 'Так. На одному каналі може звучати голос ведучого, на іншому музика. Гість перемикає канал одним дотиком. Попередьте команду, і ми налаштуємо.', ''),
 ('Скільки коштують навушники для бар-туру?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники гостям на старті й збираємо на фініші. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="bartours_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="bartours_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для бар-туру</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові канали чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте бар-тур? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про компанію, маршрут і побажання. Ми підкажемо, як налаштувати музику й голос ведучого в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, району й приблизної кількості гостей.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для бар-туру</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Бар-тур</option>')
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
