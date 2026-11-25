"""Одноразовий генератор сторінки /experiences/impostor/ (гра «Імпостер», 24.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: вечірка друзів, корпоратив і тімбілдинг, день
народження й родина, студентська або шкільна подія. Механіка від власника (25.11): гравці (звично до п'яти, можна й більше) одягають навушники,
в усіх грає одна музика, усі танцюють, а в одного грає інша; йому треба танцювати, ніби чує те саме, і не видати себе. Гру ведете ви; SILENT видає навушники, налаштовує
канали, за потреби дає передавач із мікрофоном для ведучого. НЕ обіцяємо: правил гри понад картку, дальності сигналу,
безпеки слуху. Фото: 19 кадрів із ChatGPT (inbox/impostor/gen → convert.py → images/impostor/): на кожному кадрі всі
в навушниках одного кольору, а один гравець у іншому (саме так показуємо самозванця).
Запуск: python3 tools/gen_impostor_page.py (далі build_en.py). УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'impostor', 'index.html')
IMG = '../../images/impostor/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'impostor', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

FRIENDS = 'druzi-tantsiuiut-odyn-chuie-inshe.webp'                    # 01 картка 3:2
POKER = 'divchyna-z-pokerfeis-v-chervonykh-navushnykakh.webp'    # 02 «Чому» 2:3
CORP = 'kolehy-tantsiuiut-v-lounzhi.webp'                # 03 картка 3:2
FAMILY = 'simia-tantsiuie-na-dni-narodzhennia.webp'     # 04 картка 3:2
STUDENTS = 'studenty-tantsiuiut-u-spilnii-kimnati.webp'                    # 05 картка 3:2
SCHOOL = 'pidlitky-tantsiuiut-u-shkilnii-zali.webp'      # 06 картка 3:2
VOTE = 'khtos-tantsiuie-ne-v-takt.webp'            # 07 картка 3:2
SUSPECT = 'cholovik-pidozriuie-impostora.webp'                   # 08 квадрат («Чому» s-a)
PAIR = 'dvoie-druziv-pidozriuiut-odne-odnoho.webp'               # 09 квадрат («Чому» s-b)
G1 = 'zhinka-z-nevynnoiu-usmishkoiu.webp'                        # 10 колаж 4:5
G2 = 'cholovik-tantsiuie-zakryvshy-ochi.webp'                       # 11
G3 = 'zhinka-kopiiuie-rukhy-inshykh.webp'                          # 12
G4 = 'khlopets-pidozriuie-susida-pid-chas-tantsiu.webp'                       # 13
G5 = 'zhinka-zakryla-rot-vid-zdyvuvannia.webp'                   # 14
G6 = 'cholovik-zdaietsia-smiiuchys.webp'                         # 15
HANDOUT = 'vydacha-navushnykiv-na-vkhodi.webp'                   # 16 2:3
LEADER = 'vedouchyi-hry-hovoryt-do-hrupy.webp'                   # 17 квадрат
TECH = 'tekhnik-nalashtovuie-harnituru-vedouchomu.webp'          # 18 4:5
FINAL = 'velyke-kolo-hravtsiv-v-lounzhi.webp'                    # 19 16:9

TITLE = 'Гра «Імпостер» у навушниках: танцюй і не видай себе | SILENT'
DESC = 'Гра «Імпостер» у бездротових навушниках SILENT: усі танцюють під одну музику, а в одного грає інша, і він має не видати себе. Київ і по Україні.'
OG_T = TITLE
OG_D = 'Усі танцюють під одну музику, а в одного грає інша. Гра «Імпостер» у навушниках для вечірок, корпоративів і свят.'
OG_ALT = 'Друзі танцюють у вітальні: четверо в синіх навушниках SILENT, один у червоних і трохи не в такт'

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
rep('images/conferences/og-conferences.jpg', 'images/impostor/og-impostor.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Гра «Імпостер»",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для гри «Імпостер»"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для гри «Імпостер»"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Компанії друзів, організатори корпоративів, днів народження й шкільних та студентських подій"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-24"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/impostor/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/impostor/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/impostor/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Гра «Імпостер»</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Гра<br>«Імпостер»<br>в навушниках</span> <span class="t-sub">усі танцюють під одну музику, а в одного грає інша</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Гравці одягають навушники, і в усіх вмикається одна музика. Усі танцюють, але в одного грає інша. Йому треба не видати себе й танцювати так, ніби він чує те саме. Інші намагаються його викрити. SILENT видає навушники й налаштовує канали.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="impostor_hero_order">Обговорити гру</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Інша музика</b> <span>лише для самозванця.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ В ГРІ «ІМПОСТЕР»: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="impostor">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Дівчина в червоних навушниках SILENT з лукавою напівусмішкою й незворушним виглядом, поруч гравці в синіх"' % (IMG, POKER))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Чоловік у синіх навушниках SILENT підозріло примружився й підняв брову, придивляючись до інших гравців"' % (IMG, SUSPECT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Двоє друзів підозріло дивляться одне на одного: один у синіх навушниках SILENT, другий у червоних"' % (IMG, PAIR))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Танець, у якому в одного грає інша музика</h2>\n'
    '      <p>У грі «Імпостер» гравці одягають навушники, і в усіх вмикається одна музика. Усі танцюють. Але в одного з них грає зовсім інша.</p>\n'
    '      <p>Йому треба не видати себе: зробити вигляд, що він танцює так само, як усі. Інші стежать за рухами й намагаються зрозуміти, хто чує інше.</p>\n'
    '      <p>Колонки тут не потрібні, бо музика грає лише у вухах гравців. З боку це схоже на тиху дискотеку, у якій в одного гравця звучить інший трек.</p>\n'
    '      <p>Гру проводите ви: обираєте самозванця й вирішуєте, як вести обговорення. Правила можна змінювати, тож розкажіть, як ви хочете грати, і ми налаштуємо канали.</p>\n'
    '      <p class="story-sub story-close">Усі танцюють. Хтось чує інше.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де гра «Імпостер» у навушниках особливо добре заходить</h2>')
cards = [
    (FRIENDS, '50% 45%', 'П’ятеро друзів танцюють у вітальні: четверо в синіх навушниках SILENT, чоловік у червоних танцює з награною усмішкою', 'Вечірка друзів',
     'Компанія танцює під одну музику, а в одного грає інша. Він копіює рухи інших і намагається не видати себе.'),
    (CORP, '50% 45%', 'Колеги танцюють в офісному лаунжі: п’ятеро в зелених навушниках SILENT, одна жінка в червоних зосереджено стежить за рухами інших', 'Корпоратив і тімбілдинг',
     'Проста гра для вечора або зустрічі команди. Усі рухаються, сміються й придивляються одне до одного.'),
    (FAMILY, '50% 45%', 'Родина танцює у вітальні серед кульок: п’ятеро в синіх навушниках SILENT, підліток у червоних', 'День народження й родина',
     'Бабусі й дідусі, батьки та діти танцюють разом. У когось інша музика, і вся родина шукає, у кого саме.'),
    (STUDENTS, '50% 45%', 'Вісім студентів танцюють у спільній кімнаті: сім у синіх навушниках SILENT, один у червоних', 'Студентська подія',
     'Гра для вечора у вітальні гуртожитку, клубі чи на заході факультету. Чим більше гравців, тим важче викрити самозванця.'),
    (SCHOOL, '50% 45%', 'Сім підлітків танцюють у шкільній залі: шестеро в зелених навушниках SILENT, один у червоних', 'Шкільний вечір',
     'Клас або загін танцює під одну музику, а в одного звучить інша. Правила прості, тому підліткам не треба довго пояснювати.'),
    (VOTE, '50% 45%', 'Четверо друзів у синіх навушниках SILENT показують пальцями на друга в червоних, який танцює не в такт і винувато усміхається', 'Хто танцює не в такт?',
     'Самозванець старанно копіює рухи, але хтось помічає, що він трохи не в такт. Після розкриття гру можна почати знову.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працює гра «Імпостер» у навушниках</h2>')
rep_re(r'(<h2 class="exp-h2">Як працює гра «Імпостер» у навушниках</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Усі в навушниках</b> <span>Гравці одягають навушники, і музика вмикається в усіх одночасно. Колонки не потрібні: звук грає лише у вухах.</span></li>\n'
    '        <li><b>Одному грає інше</b> <span>У самозванця звучить інша музика. Самозванця обираєте ви, тому інші про це не знають.</span></li>\n'
    '        <li><b>Танцюємо й стежимо</b> <span>Усі танцюють. Самозванець намагається рухатися так само, як решта, а інші придивляються й намагаються його викрити.</span></li>\n'
    '        <li><b>Усе налаштовує SILENT</b> <span>Ми привозимо навушники, налаштовуємо канали, видаємо їх гравцям і збираємо після гри. Гучність у кожного своя: є регулятор.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук гри беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви проводите гру, а <a href="/">SILENT</a> дає навушники й налаштовує канали, щоб кожен чув свою музику.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для гравців із регулятором гучності;</span></li>\n'
    '        <li><span>канали: один для більшості гравців, інший для самозванця;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого, якщо він потрібен;</span></li>\n'
    '        <li><span>видача навушників на вході й збір після гри;</span></li>\n'
    '        <li><span>технічний супровід протягом вечора.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT біля входу видає гостеві навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Ведучий гри говорить до гравців, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає ведучому закріпити гарнітуру, у руці в ведучого портативний передавач"' % (IMG, TECH))
rep_re(r'<img style="object-position:50% 50%"( width="1254" height="1254" class="s-b" src="[^"]*tekhnik-nalashtovuie-harnituru-vedouchomu\.webp")',
       r'<img style="object-position:50% 8%"\g<1>')

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від дати до першого танцю</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату вечора, місця й кількості гравців. На цій основі підбираємо комплект, канали й музику.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Велике коло гравців у світлому лаунжі: усі в синіх навушниках SILENT, один у червоних, усі сміються й придивляються одне до одного"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат вечора й кількість гравців.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, канали й музику, а також мікрофон для ведучого, якщо він потрібен.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників гравцям.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо гру</h3>\n        <p>Налаштовуємо канали, перевіряємо звук, видаємо навушники й збираємо комплект після гри відповідно до погодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="impostor_process_order">Обговорити гру</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="party"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Гра «Імпостер»" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Гра «Імпостер» лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/quests/">квести</a>, <a href="/experiences/birthday/">дні народження</a>, <a href="/experiences/students/">студентські події</a> й <a href="/experiences/corporate/">корпоративи</a>. Поради шукайте в <a href="/blog/">блозі</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про гру «Імпостер» у навушниках')
Q = [
 ('Як працює гра «Імпостер» у навушниках?', 'Усі гравці одягають навушники, і в них грає одна музика. Усі танцюють, але в одного грає інша. Йому треба не видати себе й танцювати так, ніби він чує те саме.', ''),
 ('Скільки гравців може бути?', 'Зазвичай грають до п’яти людей, але можна й більше. Розкажіть про компанію, і ми підкажемо, скільки навушників взяти.', ''),
 ('Хто проводить гру?', 'Гру проводите ви: обираєте самозванця й стежите за грою. SILENT дає навушники, налаштовує канали й супроводжує вечір.', ''),
 ('Чи можна змінити правила?', 'Так, у гри є різні варіації. Розкажіть, як ви хочете грати, і ми налаштуємо канали під ваші правила.', ''),
 ('Чи можна кожному налаштувати гучність?', 'Так. У кожних навушниках є регулятор гучності, тож гравець сам обирає, наскільки гучно слухати.', ''),
 ('Скільки коштують навушники для гри?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники гравцям на вході й збираємо після гри. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="impostor_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="impostor_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для гри «Імпостер»</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові канали чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте гру «Імпостер»? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про вечір, гравців і місце. Ми підкажемо, як налаштувати канали для гри, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості гравців.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для гри «Імпостер»</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Гра «Імпостер»</option>')
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
