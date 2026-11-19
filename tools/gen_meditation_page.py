"""Одноразовий генератор сторінки /experiences/meditation/ (медитація, 19.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Сценарії від власника: групова медитація з ведучим, медитація під музику
(чаші, гонг), медитація просто неба, wellness для команд і ретрити. Відрізняється від сторінки «Йога»
(рух, практика, ecstatic dance): тут нерухомість, заплющені очі, голос ведучого й спокійна музика.
Факти: ведучого запрошує клієнт; ведучий користується портативним передавачем із мікрофоном (дає SILENT);
спокійна музика й плейлисти SILENT; про голос разом із музикою пишемо впевнено: «попередьте команду, ми налаштуємо».
НЕ обіцяємо: лікувального чи терапевтичного ефекту, повної тиші навколо, безпеки слуху, дальності сигналу.
Фото: 19 кадрів із ChatGPT (inbox/meditation/gen → inbox/meditation/convert.py → images/meditation/);
у кожній сцені всі навушники ОДНОГО кольору (усі слухають одного ведучого на одному каналі).
Запуск: python3 tools/gen_meditation_page.py  (далі python3 tools/build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'meditation', 'index.html')
IMG = '../../images/meditation/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'meditation', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

STUDIO = 'hrupova-medytatsiia-u-svitlii-studii.webp'              # 01 картка 3:2 (сині)
GUIDE_PARK = 'providnytsia-medytatsii-v-parku-vrantsi.webp'       # 02 «Чому» 2:3 (зелені)
DAWN = 'svitanok-medytatsiia-na-travi-v-parku.webp'               # 03 картка 3:2 (зелені)
EVENING = 'vechirnie-rozsliablennia-na-matakh-pid-pledamy.webp'   # 04 картка 3:2 (сині)
BOWLS = 'spivochi-chashi-ta-honh-pry-svichkakh.webp'              # 05 картка 3:2 (сині)
OFFICE = 'medytatsiia-komandy-v-ofisi.webp'                       # 06 картка 3:2 (зелені)
RETREAT = 'rytreat-u-zali-z-vydom-na-lis.webp'                    # 07 картка 3:2 (сині)
PORTRAIT = 'portret-zakryti-ochi-medytatsiia.webp'                # 08 квадрат («Чому» s-a)
GARDEN = 'chotyry-liudy-na-matakh-v-sadu-na-zakhodi.webp'         # 09 квадрат («Чому» s-b, середній план)
G1 = 'litnii-cholovik-medytuie-bilia-ozera.webp'                  # 10–15 колаж 4:5
G2 = 'divchyna-na-terasi-na-zakhodi-medytatsiia.webp'
G3 = 'try-druzi-na-matakh-v-parku.webp'
G4 = 'zhinka-lezhyt-na-matu-pid-teplym-svitlom.webp'
G5 = 'mama-z-donkoiu-medytuiut-vdoma.webp'
G6 = 'dvi-zhinky-na-prystani-na-svitanku.webp'
HANDOUT = 'vydacha-navushnykiv-bilia-studii.webp'                 # 16 2:3 («Що входить» s-main)
LEADER = 'providnytsia-hovoryt-do-hrupy-z-peredavachem.webp'      # 17 квадрат («Що входить» s-a)
TECH = 'tekhnik-nalashtovuie-harnituru-providnyku.webp'           # 18 4:5 («Що входить» s-b)
FINAL = 'rankova-medytatsiia-v-parku-sorok-liudei.webp'           # 19 16:9 («Як замовити»)

TITLE = 'Медитація в навушниках: голос ведучого і спокійна музика | SILENT'
DESC = 'Бездротові навушники для групових медитацій у залі, парку чи на ретриті: голос ведучого й спокійна музика без колонок. Київ і виїзд по Україні.'
OG_T = 'Медитація в навушниках: голос ведучого і спокійна музика | SILENT'
OG_D = 'Групова медитація в залі, парку чи на ретриті: голос ведучого й спокійна музика звучать у навушниках кожного, без колонок.'
OG_ALT = 'Група людей медитує в світлій студії, ведуча говорить у мікрофон, усі в бездротових навушниках SILENT'

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
rep('images/conferences/og-conferences.jpg', 'images/meditation/og-meditation.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Медитація",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для медитації"')
rep('"serviceType": "Silent disco"', '"serviceType": "Навушники для групової медитації"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Ведучі медитацій, студії, wellness-команди й організатори ретритів"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-19"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/meditation/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/meditation/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/meditation/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Медитація</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long"><span class="t-lead">Медитація в навушниках</span> <span class="t-sub">голос ведучого й спокійна музика прямо у вухах</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Група сідає, заплющує очі й чує ведучого так само близько, ніби сидить у першому ряду. Голос і спокійна музика звучать у бездротових навушниках кожного, а колонки не потрібні: SILENT видає навушники й налаштовує передавач.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="meditation_hero_order">Обговорити медитацію</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Голос ведучого</b> <span>і спокійна музика в навушниках.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА МЕДИТАЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="meditation">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Ведуча медитації говорить у мікрофон, на траві за нею група слухає із заплющеними очима в навушниках SILENT"' % (IMG, GUIDE_PARK))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Жінка із заплющеними очима слухає в навушниках SILENT, у вікні розмите світло"' % (IMG, PORTRAIT))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Четверо людей сидять на матах у саду на заході сонця й медитують у навушниках SILENT"' % (IMG, GARDEN))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Голос ведучого звучить у кожного однаково близько</h2>\n'
    '      <p>Спокійний голос ведучого легко губиться: у великому залі його чути гірше в останніх рядах, у парку забирають вітер і голоси перехожих. Підняти гучність колонками означає зіпсувати саму практику.</p>\n'
    '      <p>У бездротових навушниках SILENT голос ведучого й музика звучать просто у вусі, тож кожну підказку чути ясно, навіть якщо ви сидите на краю лужка чи в кінці зали. У кожного свій регулятор гучності.</p>\n'
    '      <p>Ведучого запрошуєте ви. Він говорить у мікрофон портативного передавача, який налаштовує SILENT, а спокійна музика чи звук чаш звучить поруч із його голосом. Попередьте команду, і ми все налаштуємо.</p>\n'
    '      <p class="story-sub story-close">Тиша для практики. Голос ведучого в кожного. Без колонок.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де медитація в навушниках працює особливо добре</h2>')
cards = [
    (STUDIO, '50% 45%', 'Група медитує в світлій студії, ведуча говорить у мікрофон, усі в навушниках SILENT', 'Групова медитація в студії',
     'Ведуча говорить тихо, а голос чути в кожному навушнику однаково близько. Студія чи зал можуть бути будь-якого розміру, а колонки не потрібні.'),
    (DAWN, '50% 45%', 'Люди медитують на килимках у парку на світанку, ведучий сидить перед ними, усі в навушниках SILENT', 'Світанок у парку',
     'Килимки на траві, ранкова імла й ведучий попереду. Вітер і голоси парку не заважають чути підказки, бо голос іде просто в навушники.'),
    (EVENING, '50% 45%', 'Люди лежать на килимках під пледами у вечірній студії, усі в навушниках SILENT', 'Вечірнє розслаблення',
     'Приглушене світло, пледи й повільна музика. Гості лежать із заплющеними очима, а голос ведучого й мелодія звучать у навушниках кожного.'),
    (BOWLS, '50% 45%', 'Люди лежать на килимках при свічках, виконавець грає на співочих чашах і гонгу, усі в навушниках SILENT', 'Співочі чаші й гонг',
     'Звук чаш і гонгу виконавець (його запрошуєте ви) віддає в передавач, а SILENT підключає його до навушників. Гості слухають зблизька, без колонок у залі.'),
    (OFFICE, '50% 45%', 'Колеги сидять на стільцях в офісі із заплющеними очима, ведуча попереду, усі в навушниках SILENT', 'Wellness для команди',
     'Двадцять хвилин зупинки посеред робочого дня: у переговорній чи лофті, без узгодження гучності з сусідніми відділами.'),
    (RETREAT, '50% 45%', 'Люди сидять на подушках у дерев’яній залі з видом на сосновий ліс, ведучий поруч, усі в навушниках SILENT', 'Ретрит і виїзд за місто',
     'Зала з панорамними вікнами, ліс за склом і ранкова практика. Бездротові навушники працюють так само добре на виїзді, як у місті.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на медитації</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на медитації</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Голос ведучого</b> <span>Ведучого запрошуєте ви. Він бере портативний передавач із мікрофоном, а SILENT налаштовує його перед початком.</span></li>\n'
    '        <li><b>Спокійна музика поруч</b> <span>Музика чи звук чаш звучить у навушниках разом із голосом. Попередьте команду, ми налаштуємо. У кожного гостя свій регулятор гучності.</span></li>\n'
    '        <li><b>Три канали, якщо треба</b> <span>На вільних каналах можуть звучати плейлисти SILENT, наприклад до початку й після практики. Колір підсвітки показує, хто що слухає.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники на вході, супроводжує практику й збирає комплект після завершення відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук практики беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте практику й запрошуєте ведучого, а <a href="/">SILENT</a> відповідає за навушники, мікрофон і передавач: щоб кожен чув ведучого без напруги.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для учасників;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого;</span></li>\n'
    '        <li><span>плейлисти SILENT зі спокійною музикою;</span></li>\n'
    '        <li><span>видача навушників на вході й збір після практики;</span></li>\n'
    '        <li><span>технічний супровід протягом заходу.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="На вході в студію гостям видають навушники SILENT, решта лежать у дерев’яному ящику"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Ведуча медитації говорить до групи, на поясі в неї невеликий передавач SILENT"' % (IMG, LEADER))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає ведучому прилаштувати гарнітуру з мікрофоном і передає передавач"' % (IMG, TECH))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від ідеї практики до першого вдиху</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату практики й місця: де сидять чи лежать учасники, скільки їх, чи буде музика поруч із голосом. На цій основі визначаємо комплект.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Ранкова медитація в парку: близько сорока людей сидять на килимках у світних навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце, формат практики й орієнтовну кількість учасників.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофон для ведучого й те, яка музика звучатиме поруч із голосом.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час налаштування й порядок видачі навушників учасникам.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо практику</h3>\n        <p>Налаштовуємо передавач, перевіряємо звук разом із ведучим, видаємо навушники на вході й збираємо їх після практики відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="meditation_process_order">Обговорити медитацію</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="sport"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Медитація" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Медитація лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/yoga/">йога та ecstatic dance</a>, <a href="/experiences/runs-walks/">забіги й прогулянки</a>, <a href="/experiences/trainings/">тренінги й навчання</a> і <a href="/experiences/outdoor-cinema/">кіно просто неба</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/yak-organizuvaty-zakhid-u-parku/">як організувати захід у парку</a> і <a href="/blog/yak-provesty-treninh-dlia-velykoi-hrupy/">як провести тренінг для великої групи</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на медитації')
Q = [
 ('Чи надаєте ви ведучого медитації?', 'Ні, ведучого запрошуєте ви. SILENT дає навушники, портативний передавач із мікрофоном і супроводжує захід.', ''),
 ('Як голос ведучого потрапляє в навушники?', 'Ведучий говорить у мікрофон портативного передавача, який налаштовує SILENT. Передавач віддає голос у бездротові навушники учасників, і в кожного є свій регулятор гучності.', ''),
 ('Чи можна пустити спокійну музику разом із голосом?', 'Так. Попередьте команду, і ми налаштуємо так, щоб голос ведучого й музика чи звук чаш звучали в навушниках разом.', ''),
 ('Чи можна медитувати просто неба?', 'Так, навушники бездротові, тож практику можна провести в парку, саду чи на березі. Живлення для передавача й план на випадок дощу (навіс, намет чи приміщення) узгоджуємо заздалегідь.', ''),
 ('Скільки коштують навушники для медитації?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники на вході й збираємо після практики. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
 ('Чи можна налаштувати гучність у навушниках?', 'Так. У навушниках є регулятор та обмежувач гучності, а кожен учасник налаштовує рівень звуку для себе. Обмежувач допомагає контролювати рівень звуку, але не є гарантією абсолютної безпеки для слуху.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="meditation_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="meditation_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для медитації</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо потрібні додаткові мікрофони чи особливі умови, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте медитацію? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про практику, місце й кількість учасників. Ми підкажемо, як налаштувати голос ведучого й музику в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, місця й приблизної кількості учасників.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для медитації</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Медитація</option>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
# кадр техніка: опущений у рамці, щоб було видно обличчя (власник, 19.11)
s = s.replace('object-position:50% 50%" width="1254" height="1254" class="s-b" src="%s%s"' % (IMG, TECH), 'object-position:50% 14%" width="1254" height="1254" class="s-b" src="%s%s"' % (IMG, TECH))
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
