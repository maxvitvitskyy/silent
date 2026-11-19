"""Одноразовий генератор сторінки /experiences/brand-activation/ (бренд-активації, 19.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: Silent-зона на виставці й фесті, запуск продукту
й презентація, флешмоб / вуличний промо, торговий центр / pop-up. Брендування навушників пропонуємо (рішення
власника 19.11), умови й терміни «обговорюємо окремо», без цін і технічних подробиць.
Факти: промоутера чи ведучого запрошує клієнт; передавач із мікрофоном і плейлисти дає SILENT; про голос разом
із музикою пишемо впевнено: «попередьте команду, ми налаштуємо». Дозвіл на майданчик узгоджує клієнт із його
власником. НЕ обіцяємо: дальності сигналу, кількості відвідувачів чи конверсії, безпеки слуху.
Фото: 19 кадрів із ChatGPT (inbox/brand-activation/gen → convert.py → images/brand-activation/); на кожному
кадрі навушники одного кольору, без логотипів брендів (стенди порожні й абстрактні).
Запуск: python3 tools/gen_brand_page.py  (далі python3 tools/build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'brand-activation', 'index.html')
IMG = '../../images/brand-activation/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'brand-activation', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

STAND = 'stend-na-vystavtsi-hosti-v-navushnykakh.webp'            # 01 картка 3:2 (сині)
VISITOR = 'vidviduvach-stendu-slukhaie-v-navushnykakh.webp'      # 02 «Чому» 2:3 (сині)
LAUNCH = 'zapusk-produktu-hosti-v-zelenykh-navushnykakh.webp'    # 03 картка 3:2 (зелені)
PRES = 'zakryta-prezentatsiia-dlia-hostei.webp'                  # 04 картка 3:2 (сині)
FLASH = 'flashmob-na-ploshchi-v-navushnykakh.webp'               # 05 картка 3:2 (сині)
POPUP = 'pop-up-v-torhovomu-tsentri-tantsi.webp'                 # 06 картка 3:2 (зелені)
FEST = 'brend-zona-na-festyvali-vvecheri.webp'                   # 07 картка 3:2 (сині)
PORTRAIT = 'portret-divchyny-na-stendi.webp'                     # 08 квадрат («Чому» s-a)
FRIENDS = 'chotyry-druzi-tantsiuiut-v-torhovomu-tsentri.webp'    # 09 квадрат («Чому» s-b)
G1 = 'cholovik-tantsiuie-na-flashmobi.webp'                      # 10–15 колаж 4:5
G2 = 'divchyna-z-paketom-v-torhovomu-tsentri.webp'
G3 = 'dvi-podruhy-na-festyvali.webp'
G4 = 'zhinka-iz-zakrytymy-ochyma-na-stendi.webp'
G5 = 'pidlitky-tantsiuiut-na-flashmobi.webp'
G6 = 'cholovik-v-pidzhaku-na-zapusku-produktu.webp'
HANDOUT = 'vydacha-navushnykiv-na-stendi.webp'                   # 16 2:3 («Що входить» s-main)
LEADER = 'veduchyi-hovoryt-do-hostei-z-peredavachem.webp'        # 17 квадрат («Що входить» s-a)
TECH = 'tekhnik-nalashtovuie-mikrofon-veduchomu.webp'            # 18 4:5 («Що входить» s-b)
FINAL = 'velykyi-flashmob-na-ploshchi-v2.webp'                      # 19 16:9 («Як замовити»)

TITLE = 'Бренд-активація в навушниках без колонок | SILENT'
DESC = 'Бездротові навушники для бренд-активацій на виставках, у ТРЦ, на фестивалях і вулицях: повідомлення бренду й музика без колонок. Київ і виїзд по Україні.'
OG_T = 'Бренд-активація в навушниках без колонок | SILENT'
OG_D = 'Silent-зона на виставці, запуск продукту, флешмоб чи pop-up у ТРЦ: повідомлення бренду й музика звучать у навушниках гостей, без колонок.'
OG_ALT = 'Гості біля виставкового стенда слухають промоутера в бездротових навушниках SILENT'

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
rep('images/conferences/og-conferences.jpg', 'images/brand-activation/og-brand-activation.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Бренд-активації",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для бренд-активацій"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для бренд-активацій"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Бренди, маркетингові агенції та організатори виставок і промо-акцій"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-19"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/brand-activation/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/brand-activation/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/brand-activation/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Бренд-активації</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Бренд-активація в навушниках</span> <span class="t-sub">повідомлення бренду й музика прямо у вухах гостей</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Гість надягає бездротові навушники й чує ваш бренд зблизька: голос ведучого, музику, новинку в момент запуску. Колонки не потрібні, а голосу сусідніх стендів і торгового залу він не заважає. SILENT видає навушники й налаштовує передавач.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="brand_hero_order">Обговорити активацію</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Брендування</b> <span>навушників під ваш бренд.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ В БРЕНД-АКТИВАЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="brand-activation">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Відвідувач виставкового стенда в навушниках SILENT уважно слухає промоутера"' % (IMG, VISITOR))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Усміхнена дівчина в навушниках SILENT на виставковому стенді"' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Четверо друзів сміються й танцюють у навушниках SILENT на pop-up у торговому центрі"' % (IMG, FRIENDS))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Повідомлення бренду чує той, кому воно адресоване</h2>\n'
    '      <p>На виставці, в торговому центрі чи на фестивалі бренд змагається за увагу з десятками колонок і голосів. Підняти гучність означає додати шуму, який дратує сусідів і самих гостей.</p>\n'
    '      <p>У бездротових навушниках SILENT голос ведучого й музика звучать просто у вусі кожного гостя. Він слухає зблизька, а на майданчику не з’являється ще одна колонка. У кожного свій регулятор гучності.</p>\n'
    '      <p>Промоутера чи ведучого запрошуєте ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT, а музика звучить поруч із його голосом. Навушники можна забрендувати під ваш бренд, умови обговоримо окремо.</p>\n'
    '      <p class="story-sub story-close">Голос бренду в кожного гостя. Без колонок.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де бренд-активація в навушниках працює особливо добре</h2>')
cards = [
    (STAND, '50% 45%', 'Гості біля світлого виставкового стенда слухають промоутера в навушниках SILENT', 'Silent-зона на виставці',
     'Біля стенда гості надягають навушники й слухають повідомлення бренду та музику. Колонки не заважають сусіднім стендам.'),
    (FEST, '50% 45%', 'Гості відпочивають і танцюють на фестивалі під навісом із гірляндами в навушниках SILENT', 'Бренд-зона на фестивалі',
     'Навіс, мішки-крісла й гірлянди: гості відпочивають і танцюють у навушниках, а на території не з’являються ще одні колонки.'),
    (LAUNCH, '50% 45%', 'Гості на запуску продукту слухають ведучого в зелених навушниках SILENT біля накритого постаменту', 'Запуск продукту',
     'Ведучий розповідає про новинку, а голос і музика звучать у навушниках кожного гостя. Момент відкриття стає особистим.'),
    (PRES, '50% 45%', 'Гості закритої презентації слухають промовця на диванах у лофті в навушниках SILENT', 'Закрита презентація',
     'Невелика група гостей слухає презентацію в навушниках, ніби це розмова віч-на-віч. Вечір для своїх без колонок.'),
    (FLASH, '50% 45%', 'Люди танцюють флешмоб на сонячній міській площі в навушниках SILENT, перехожі дивляться', 'Флешмоб на вулиці',
     'Група танцює площею під музику, яку чують лише учасники, а перехожі зупиняються й дивляться. Для ведучого SILENT дає передавач із мікрофоном.'),
    (POPUP, '50% 45%', 'Гості танцюють на круглій платформі в атріумі торгового центру в навушниках SILENT', 'Pop-up у торговому центрі',
     'Кругла платформа в атріумі: гості танцюють у навушниках, а покупці дивляться навколо. Гучні колонки в ТРЦ не потрібні.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники в бренд-активації</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники в бренд-активації</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Голос ведучого</b> <span>Промоутера чи ведучого запрошуєте ви. Він бере портативний передавач із мікрофоном, а SILENT налаштовує його перед початком.</span></li>\n'
    '        <li><b>Музика поруч із голосом</b> <span>Музика звучить у навушниках разом із голосом. Попередьте команду, ми налаштуємо. У кожного гостя свій регулятор гучності.</span></li>\n'
    '        <li><b>Брендування навушників</b> <span>Навушники можна забрендувати під ваш бренд. Умови й терміни узгоджуємо окремо під вашу активацію.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники гостям, супроводжує активацію й збирає комплект відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук активації беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте активацію й запрошуєте ведучого, а <a href="/">SILENT</a> відповідає за навушники, мікрофон і передавач: щоб кожен гість чув бренд без напруги.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для гостей;</span></li>\n'
    '        <li><span>брендування навушників під ваш бренд;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого;</span></li>\n'
    '        <li><span>плейлисти SILENT;</span></li>\n'
    '        <li><span>видача, збір і технічний супровід протягом заходу.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="Співробітник SILENT на стенді віддає гостю навушники, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Ведучий активації говорить до гостей, на поясі в нього невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT налаштовує гарнітуру з мікрофоном ведучому, у руці в нього портативний передавач"' % (IMG, TECH))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від ідеї активації до першого гостя</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату активації й майданчика: де стоїть стенд чи проходить акція, скільки гостей і яку музику ви хочете. На цій основі визначаємо комплект.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Великий флешмоб на сонячній міській площі: сотні людей танцюють у світних синіх навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, майданчик, формат активації й орієнтовну кількість гостей.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофон для ведучого, музику й чи потрібне брендування навушників.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників гостям.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо активацію</h3>\n        <p>Налаштовуємо передавач, перевіряємо звук разом із ведучим, видаємо навушники гостям і збираємо їх після активації відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="brand_process_order">Обговорити активацію</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="business"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Бренд-активації" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Бренд-активація лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/corporate/">корпоративи</a>, <a href="/experiences/conferences/">конференції</a>, <a href="/experiences/festivals/">фестивалі</a> і <a href="/experiences/markets/">ярмарки та маркети</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/silent-disco-na-festyvali/">Silent Disco на фестивалі</a> і <a href="/blog/yak-orhanizuvaty-yarmarok/">як організувати ярмарок</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на бренд-активації')
Q = [
 ('Чи надаєте ви ведучого чи промоутера?', 'Ні, ведучого запрошуєте ви. SILENT дає навушники, портативний передавач із мікрофоном і супроводжує захід.', ''),
 ('Чи можна забрендувати навушники під наш бренд?', 'Так, пропонуємо брендування навушників. Умови й терміни обговорюємо окремо під вашу активацію.', ''),
 ('Як голос ведучого потрапляє в навушники?', 'Ведучий говорить у мікрофон портативного передавача, який налаштовує SILENT. Передавач віддає голос у бездротові навушники гостей, і в кожного є свій регулятор гучності.', ''),
 ('Чи можна пустити музику разом із голосом?', 'Так. Попередьте команду, і ми налаштуємо так, щоб голос ведучого й музика звучали в навушниках разом.', ''),
 ('Чи підійде формат для вуличної акції чи ТРЦ?', 'Так, навушники бездротові, тож активацію можна провести на площі, у торговому центрі чи на фестивалі. Дозвіл на майданчик ви узгоджуєте з його власником чи адміністрацією, а ми допомагаємо з технічною частиною. Живлення для передавача й запасний план на випадок дощу узгоджуємо заздалегідь.', ''),
 ('Скільки коштують навушники для бренд-активації?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники гостям і збираємо після активації. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="brand_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="brand_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для бренд-активації</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні брендування, додаткові мікрофони чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте бренд-активацію? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про активацію, майданчик і кількість гостей. Ми підкажемо, як налаштувати голос ведучого й музику в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, майданчика й приблизної кількості гостей.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для бренд-активації</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Бренд-активація</option>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x and 'conferences/' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
# кадр техніка (вертикальний 4:5): опущений у рамці, щоб було видно обличчя
old = 'object-position:50% 50%" width="1254" height="1254" class="s-b" src="' + IMG + TECH + '"'
if s.count(old) == 1:
    s = s.replace(old, old.replace('50% 50%', '50% 14%'))
else:
    print('УВАГА: рядок s-b для техніка не знайдено, object-position не змінено')
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
