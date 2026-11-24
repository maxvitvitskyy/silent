"""Одноразовий генератор сторінки /experiences/quests/ (квести, 24.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: міський квест маршрутом, корпоративний
тімбілдинг-квест, дитячий квест і день народження, квест-детектив у приміщенні; додатково три команди в залі
й квест у парку. Сценарій і ведучого гри приносить клієнт; SILENT дає навушники з каналами (до трьох команд,
кожна на своєму), передавач із мікрофоном для ведучого й супровід. НЕ обіцяємо: дальності сигналу, безпеки слуху,
що живі розмови в залі не чутно. Фото: 19 кадрів із ChatGPT (inbox/quests/gen → convert.py → images/quests/).
Запуск: python3 tools/gen_quests_page.py (далі build_en.py). УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'quests', 'index.html')
IMG = '../../images/quests/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'quests', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

ROUTE = 'komanda-z-kartoiu-na-vulytsi-mista.webp'           # 01 картка 3:2
LISTEN = 'divchyna-slukhaie-pidkazku-v-navushnykakh.webp'     # 02 «Чому» 2:3
CORP = 'tiumbildynh-kvest-kolehy-za-stolom.webp'              # 03 картка 3:2
BDAY = 'kvest-na-den-narodzhennia-pidlitky.webp'              # 04 картка 3:2
DETECT = 'kvest-detektyv-u-kabineti.webp'                     # 05 картка 3:2
THREE = 'try-komandy-hraiut-u-odnomu-zali.webp'               # 06 картка 3:2
PARK = 'kvest-u-parku-komanda-z-kartoiu.webp'                 # 07b картка 3:2
THINK = 'cholovik-dumaie-nad-pidkazkoiu.webp'                 # 08 квадрат («Чому» s-a)
WHISPER = 'dvoie-shepochutsia-nad-kartoiu.webp'               # 09 квадрат («Чому» s-b)
G1 = 'zhinka-smiietsia-znaishovshy-pidkazku.webp'             # 10 колаж 4:5
G2 = 'cholovik-zdyvovano-dyvytsia.webp'                       # 11
G3 = 'dvi-uchasnytsi-diaiut-pyat.webp'                        # 12
G4 = 'khlopets-vidkryvaie-skarbnytsiu.webp'                   # 13
G5 = 'zhinka-zrozumila-vidpovid.webp'                         # 14
G6 = 'trio-sviatkuie-peremohu.webp'                           # 15
HANDOUT = 'vydacha-navushnykiv-bilia-kvestu.webp'             # 16 2:3
LEADER = 'vedouchyi-hry-hovoryt-do-komand.webp'               # 17 квадрат
TECH = 'tekhnik-nalashtovuie-harnituru-vedouchomu.webp'       # 18 4:5
FINAL = 'try-komandy-za-try-stoly-v-zali.webp'                # 19b 16:9

TITLE = 'Квести в навушниках: підказки чує лише команда | SILENT'
DESC = 'Бездротові навушники для квестів і тімбілдингів: кожна команда слухає свій канал, а чужі підказки не потрапляють до суперників. Київ і по Україні.'
OG_T = TITLE
OG_D = 'Квест у навушниках: підказки й голос ведучого звучать на каналі команди, а суперники їх не чують. Київ і по Україні.'
OG_ALT = 'Команда квесту схилилася над підказками за столом у бездротових навушниках SILENT'

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
rep('images/conferences/og-conferences.jpg', 'images/quests/og-quests.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Квести",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для квестів"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для квестів"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Організатори квестів, тімбілдингів, днів народження й міських ігор"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-24"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/quests/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/quests/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/quests/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Квести</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Квести<br>з підказками<br>в навушниках</span> <span class="t-sub">кожна команда чує лише свій канал</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Підказки й голос ведучого звучать просто у вусі кожного гравця, а суперники їх не чують: кожна команда слухає свій канал. Сценарій і ведучого гри приносите ви, а SILENT видає навушники, налаштовує канали й передавач.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="quests_hero_order">Обговорити квест</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Свій канал</b> <span>для кожної команди.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА КВЕСТІ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="quests">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Молода жінка підносить палець до вуха й уважно слухає підказку квесту в навушниках SILENT"' % (IMG, LISTEN))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Чоловік замислено тримає руку біля підборіддя, слухаючи підказку, у навушниках SILENT"' % (IMG, THINK))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Двоє товаришів по команді шепочуться над порожньою картою в навушниках SILENT"' % (IMG, WHISPER))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Підказка, яку чує лише своя команда</h2>\n'
    '      <p>У звичайному квесті команди стоять поруч і чують підказки одна одної. Ведучому доводиться говорити тихо, а змагання перестає бути чесним.</p>\n'
    '      <p>У бездротових навушниках SILENT кожна команда слухає свій канал: підказки й голос ведучого звучать лише для неї. Суперники не підслухають, а гучність кожен гравець налаштовує сам.</p>\n'
    '      <p>Сценарій і ведучого гри приносите ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT. Аудіопідказки з вашої гри теж можна пустити в навушники: попередьте команду, ми налаштуємо.</p>\n'
    '      <p class="story-sub story-close">Своя підказка. Свій канал. Чесна гра.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де квест у навушниках працює особливо добре</h2>')
cards = [
    (ROUTE, '50% 45%', 'Команда з порожньою паперовою картою на кутку старої вулиці, усі в синіх навушниках SILENT', 'Міський квест маршрутом',
     'Команда йде містом за картою, а підказки звучать у навушниках на кожній зупинці. Чужа команда їх не почує.'),
    (CORP, '50% 45%', 'Колеги за столом із порожньою коробкою й картками сміються над загадкою в зелених навушниках SILENT', 'Корпоративний тімбілдинг-квест',
     'Колеги діляться на команди, кожна слухає свій канал. Змагання чесне, бо підказки чує лише своя команда.'),
    (BDAY, '50% 45%', 'Підлітки на святі в кімнаті шукають підказки серед подушок і полиць у червоних навушниках SILENT', 'Квест на день народження',
     'Іменинники й гості шукають підказки по кімнатах, а ведучий керує грою просто в навушниках, без зайвого шуму.'),
    (DETECT, '50% 45%', 'Команда з лупами й ліхтариками біля порожньої коркової дошки з червоною ниткою в червоних навушниках SILENT', 'Квест-детектив у приміщенні',
     'Ваша гра з ролями й сюжетом: кожна команда чує свою частину історії, а розгадка лишається таємницею.'),
    (THREE, '50% 45%', 'Три команди грають в одному залі: червоні, зелені й сині навушники SILENT, кожна команда на своєму каналі', 'Три команди, три канали',
     'До трьох команд грають в одному залі одночасно, кожна на своєму каналі. Ніхто не чує чужих підказок.'),
    (PARK, '50% 45%', 'Команда в сонячному парку дивиться на порожню карту й шукає наступну підказку в зелених навушниках SILENT', 'Квест у парку',
     'Команди розходяться парком за картою. Голос ведучого й підказки звучать у навушниках, а парк лишається тихим.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на квесті</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на квесті</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Свій канал для команди</b> <span>До трьох команд грають одночасно, кожна на своєму каналі. Гравець перемикає канал одним дотиком, а SILENT налаштовує їх перед початком.</span></li>\n'
    '        <li><b>Голос ведучого</b> <span>Ведучого гри приносите ви. Він бере портативний передавач із мікрофоном і говорить на каналі потрібної команди.</span></li>\n'
    '        <li><b>Аудіопідказки</b> <span>Аудіопідказки з вашої гри можна пустити в навушники команди. Розкажіть про сценарій, і ми підкажемо, як усе налаштувати.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники гравцям, супроводжує квест і збирає комплект відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук квесту беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте сценарій і ведучого, а <a href="/">SILENT</a> відповідає за навушники, канали й передавач: щоб кожна команда чула лише свої підказки й сама керувала гучністю.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для гравців із регулятором гучності;</span></li>\n'
    '        <li><span>канали для команд, до трьох одночасно;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого гри;</span></li>\n'
    '        <li><span>видача навушників на старті й збір після квесту;</span></li>\n'
    '        <li><span>технічний супровід протягом гри.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT біля входу в квест віддає учасниці навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Ведучий гри говорить до команд, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає ведучому закріпити гарнітуру, у руці в ведучого портативний передавач"' % (IMG, TECH))
rep_re(r'<img style="object-position:50% 50%"( width="1254" height="1254" class="s-b" src="[^"]*tekhnik-nalashtovuie-harnituru-vedouchomu\.webp")',
       r'<img style="object-position:50% 8%"\g<1>')

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від дати до першої підказки</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату квесту, місця й кількості команд. На цій основі визначаємо комплект, канали й те, чи потрібні аудіопідказки.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Три команди за трьома столами в світлій залі схилилися над картками й коробкою: червоні, зелені й сині навушники SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат квесту, кількість гравців і команд.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, канали для команд, мікрофон для ведучого й аудіопідказки.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників гравцям.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо квест</h3>\n        <p>Налаштовуємо канали й передавач, перевіряємо звук разом із ведучим, видаємо навушники й збираємо комплект після відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="quests_process_order">Обговорити квест</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="business"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Квести" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Квест лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/corporate/">корпоративи</a>, <a href="/experiences/birthday/">дні народження</a>, <a href="/experiences/runs-walks/">забіги та прогулянки</a> і <a href="/experiences/trainings/">тренінги й навчання</a>. Поради шукайте в <a href="/blog/">блозі</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на квесті')
Q = [
 ('Чи може кожна команда слухати свій канал?', 'Так. До трьох команд грають одночасно, кожна на своєму каналі. Гравець перемикає канал одним дотиком, а SILENT налаштовує їх перед початком.', ''),
 ('Чи надаєте ви сценарій і ведучого?', 'Ні, сценарій і ведучого гри приносите ви. SILENT дає навушники, канали, портативний передавач із мікрофоном і супроводжує квест.', ''),
 ('Як голос ведучого потрапляє в навушники?', 'Ведучий говорить у мікрофон портативного передавача, який налаштовує SILENT. Передавач віддає голос на канал потрібної команди.', ''),
 ('Чи можна пустити аудіопідказки?', 'Так. Аудіопідказки з вашої гри можна пустити в навушники команди. Попередьте команду, і ми налаштуємо.', ''),
 ('Чи чують команди одна одну?', 'Підказки й голос ведучого кожна команда чує лише на своєму каналі. Живі розмови гравців поруч у залі чутно, як і зазвичай.', ''),
 ('Скільки коштують навушники для квесту?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники гравцям на старті й збираємо після квесту. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="quests_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="quests_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для квесту</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові канали чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте квест? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про квест, команди й місце. Ми підкажемо, як налаштувати канали й голос ведучого в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості гравців.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для квесту</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Квест</option>')
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
