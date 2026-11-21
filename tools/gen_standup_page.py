"""Одноразовий генератор сторінки /experiences/standup/ (стендап і комедія, 21.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: стендап-вечір у клубі чи барі, стендап на
корпоративі й заході, комедія просто неба, стендап і тиха дискотека. Коміка запрошує клієнт; голос іде через
портативний передавач із мікрофоном (дає SILENT). НЕ обіцяємо: дальності сигналу, впливу на слух.
Фото: 19 кадрів із ChatGPT (inbox/standup/gen → convert.py → images/standup/); коміка показуємо БЕЗ навушників,
з окремою гарнітурою (гачок за вухом) і одним передавачем на поясі; глядачі в навушниках одного кольору.
Запуск: python3 tools/gen_standup_page.py (далі build_en.py). УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'standup', 'index.html')
IMG = '../../images/standup/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'standup', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

CLUB = 'vechir-stendapu-v-klubi.webp'                   # 01 картка 3:2
LAUGH = 'zhinka-smiietsia-na-stendapi.webp'             # 02 «Чому» 2:3
CORP = 'stendap-na-korporatyvi.webp'                    # 03 картка 3:2
COURT = 'komediia-u-dvori-pid-zirkamy.webp'             # 04 картка 3:2
DISCO = 'stendap-i-tykha-dyskoteka-v-bari.webp'         # 05 картка 3:2
BAR = 'stendap-u-bari-pid-prozhektorom.webp'            # 06 картка 3:2
ROOF = 'komediia-na-terasi-na-zakhodi.webp'             # 07 картка 3:2
PORTRAIT = 'portret-smiiuchoho-hliadacha.webp'          # 08 квадрат («Чому» s-a)
COMIC = 'komik-na-stseni-seredyni-zhartu.webp'          # 09 квадрат («Чому» s-b)
G1 = 'zhinka-vidkydaie-holovu-vid-smikhu.webp'          # 10 колаж 4:5
G2 = 'cholovik-zihnuvsia-vid-smikhu.webp'               # 11
G3 = 'dvoie-druziv-smiiutsia-do-sliz.webp'            # 12
G4 = 'litnii-cholovik-posmikhaietsia.webp'              # 13
G5 = 'divchyna-plieskaie-ta-smiietsia.webp'             # 14
G6 = 'para-smiietsia-pokhylyvshys.webp'                 # 15
HANDOUT = 'vydacha-navushnykiv-bilia-klubu.webp'        # 16 2:3 («Що входить» s-main)
LEADER = 'komik-hovoryt-do-zalu.webp'                   # 17 квадрат («Що входить» s-a)
TECH = 'tekhnik-nalashtovuie-harnituru-komiku.webp'     # 18 4:5 («Що входить» s-b)
FINAL = 'zal-komediinoho-klubu-smiietsia.webp'          # 19 16:9 («Як замовити»)

TITLE = 'Стендап і комедія в навушниках: жарти чути всім | SILENT'
DESC = 'Бездротові навушники для стендапу й комедійних вечорів: коміка чути кожному гостеві, навіть коли сміється зал, без колонок. Київ і виїзд по Україні.'
OG_T = TITLE
OG_D = 'Стендап у клубі, на корпоративі чи просто неба: голос коміка звучить у навушниках кожного гостя, без гучних колонок.'
OG_ALT = 'Гості стендап-вечора в клубі сміються в бездротових навушниках SILENT, коміка чути на сцені'

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
rep('images/conferences/og-conferences.jpg', 'images/standup/og-standup.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Стендап і комедія",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для стендапу й комедійних вечорів"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для стендапу"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Організатори стендап-вечорів, клуби, бари й корпоративні команди"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-21"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/standup/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/standup/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/standup/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Стендап і комедія</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Стендап<br>і комедія<br>в навушниках</span> <span class="t-sub">кожен жарт чути, навіть коли сміється зал</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Коміка запрошуєте ви: він говорить у мікрофон портативного передавача, а голос звучить просто у вусі кожного гостя. Жарти чути чітко навіть тоді, коли весь зал сміється, а гучних колонок немає. SILENT видає навушники й налаштовує передавач.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="standup_hero_order">Обговорити вечір</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Голос коміка</b> <span>у кожному навушнику.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА СТЕНДАПІ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="standup">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Жінка щиро сміється на стендапі, затуливши рот рукою, у навушниках SILENT"' % (IMG, LAUGH))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Молодий чоловік сміється на комедійному шоу в навушниках SILENT"' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Комік посеред жарту на невеликій сцені, перед сценою глядачі в навушниках SILENT"' % (IMG, COMIC))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Жарт, який чути кожному</h2>\n'
    '      <p>На стендапі найважливіше почути кожне слово. У залі з гучним сміхом, баром чи просто неба частина гостей ловить лише уривки, а гучні колонки заважають і сусідам.</p>\n'
    '      <p>У бездротових навушниках SILENT голос коміка звучить просто у вусі кожного, а гучність гість налаштовує сам. Жарти чути чітко навіть тоді, коли весь зал сміється.</p>\n'
    '      <p>Коміка запрошуєте ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT. Якщо потрібна музика до чи після виступу, попередьте команду, ми налаштуємо.</p>\n'
    '      <p class="story-sub story-close">Кожен жарт. Кожен чує. Усі сміються.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де стендап у навушниках працює особливо добре</h2>')
cards = [
    (CLUB, '50% 45%', 'Комік виступає на невеликій сцені біля цегляної стіни, глядачі за столиками сміються в навушниках SILENT', 'Стендап-вечір у клубі',
     'Комік на сцені, глядачі за столиками, а голос звучить у навушниках кожного. Жарти чути чітко навіть із останнього ряду.'),
    (BAR, '50% 45%', 'Комік під теплим прожектором у барі, глядачі перших рядів сміються в навушниках SILENT', 'Стендап у барі',
     'Бар живе своїм життям, а виступ лунає в навушниках гостей, тож ні шум, ні музика не заглушують коміка.'),
    (CORP, '50% 45%', 'Колеги дивляться стендап у стильному просторі офісної події в зелених навушниках SILENT', 'Стендап на корпоративі',
     'Комік виступає для команди чи гостей заходу, а колеги слухають зручно й не відриваються від програми вечора.'),
    (COURT, '50% 45%', 'Комедійний вечір просто неба у дворі: гості на складних стільцях під гірляндами в навушниках SILENT', 'Комедія просто неба',
     'Двір, дах чи майданчик: голос коміка звучить у навушниках, тож сусіди не страждають від колонок, а гості чують усе.'),
    (ROOF, '50% 45%', 'Комік виступає на терасі на заході сонця, гості на диванах сміються в зелених навушниках SILENT', 'Тераса на заході сонця',
     'Невеликий вечір на терасі чи даху: затишні дивани, відкрите небо й виступ, який чути кожному, не підвищуючи голосу.'),
    (DISCO, '50% 45%', 'У барі ліворуч гості слухають стендап у зелених навушниках, праворуч інші гості танцюють у синіх навушниках SILENT', 'Стендап і тиха дискотека',
     'На одному каналі звучить виступ, на іншому музика для танців. Гості самі обирають, де вони, а простір один.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на стендапі</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на стендапі</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Голос коміка</b> <span>Коміка запрошуєте ви. Він бере портативний передавач із мікрофоном, а SILENT налаштовує його перед виступом.</span></li>\n'
    '        <li><b>Власна гучність</b> <span>У навушниках є регулятор: кожен гість сам обирає, наскільки гучно слухати.</span></li>\n'
    '        <li><b>Виступ і музика</b> <span>На одному каналі звучить виступ, на іншому музика для тих, хто хоче танцювати. Гість перемикає канал одним дотиком. Попередьте команду, ми налаштуємо.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники гостям, супроводжує вечір і збирає комплект відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук стендап-вечора беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте програму й запрошуєте коміка, а <a href="/">SILENT</a> відповідає за навушники, мікрофон і передавач: щоб кожен гість чув виступ чітко й сам керував гучністю.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для гостей із регулятором гучності;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для коміка;</span></li>\n'
    '        <li><span>плейлисти SILENT для музики до й після виступу;</span></li>\n'
    '        <li><span>видача навушників на вході й збір після вечора;</span></li>\n'
    '        <li><span>технічний супровід протягом заходу.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT біля входу в клуб віддає гостеві навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Комік говорить до залу, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає комікові з гарнітурою, у руці в коміка портативний передавач"' % (IMG, TECH))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від дати до першого жарту</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату вечора, простору й кількості гостей. На цій основі визначаємо комплект і те, чи потрібен окремий канал для музики.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Затишний зал комедійного клубу: комік на сцені, гості за столиками сміються в навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат вечора, кількість гостей і чи потрібна музика після виступу.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофон для коміка, канали й музику.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників гостям.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо вечір</h3>\n        <p>Налаштовуємо передавач, перевіряємо звук разом із коміком, видаємо навушники й збираємо комплект після відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="standup_process_order">Обговорити вечір</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="culture"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Стендап і комедія" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Стендап лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/dj-set/">діджей-сет наживо</a>, <a href="/experiences/chamber-concerts/">камерні концерти</a>, <a href="/experiences/corporate/">корпоративи</a> і <a href="/experiences/public-spaces/">міські події</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/dj-set-u-navushnykakh/">діджей-сет у навушниках</a> і <a href="/blog/yak-organizuvaty-zakhid-u-parku/">як організувати захід у парку</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на стендапі')
Q = [
 ('Чи надаєте ви коміка?', 'Ні, коміка запрошуєте ви. SILENT дає навушники, портативний передавач із мікрофоном і супроводжує вечір.', ''),
 ('Як голос коміка потрапляє в навушники?', 'Комік говорить у мікрофон портативного передавача, який налаштовує SILENT. Передавач віддає голос у бездротові навушники гостей, і в кожного є свій регулятор гучності.', ''),
 ('Чи чути коміка, коли сміється зал?', 'Голос звучить просто в навушниках кожного гостя, тож сміх залу не заважає його чути. Гучність кожен налаштовує сам.', ''),
 ('Чи потрібні колонки?', 'Ні. Голос коміка й музика звучать у навушниках, тому гучні колонки не потрібні.', ''),
 ('Чи можна поєднати стендап і тиху дискотеку?', 'Так. На одному каналі звучить виступ, на іншому музика для танців. Попередьте команду, і ми налаштуємо.', ''),
 ('Скільки коштують навушники для стендапу?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники гостям і збираємо після вечора. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="standup_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="standup_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для стендапу</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові канали чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте стендап? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про вечір, гостей і місце. Ми підкажемо, як налаштувати голос коміка й музику в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості гостей.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для стендапу</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Стендап</option>')
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
