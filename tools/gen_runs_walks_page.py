"""Одноразовий генератор сторінки /experiences/runs-walks/ (забіги та прогулянки з навушниками, 16.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Факти погоджено з власником 16.11.2026: чотири сценарії (групова пробіжка
з тренером; музичний забіг під спільний плейлист; прогулянка з гідом; танцювальна хода містом). Тренера чи гіда
запрошує клієнт; портативний передавач із мікрофоном і музикою несе ведучий, група тримається разом із ним;
команда SILENT видає навушники на старті й збирає на фініші. Дальності сигналу НЕ обіцяємо. Умови як для всіх форматів.
На кадрах пробіжок і прогулянок усі навушники ОДНОГО кольору (один канал); різні кольори лише на танцях після фінішу.
Запуск: python3 tools/gen_runs_walks_page.py  (далі python3 tools/build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'runs-walks', 'index.html')
IMG = '../../images/runs-walks/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'runs-walks', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

# Фото: згенеровані в ChatGPT власника за референсом навушників; вихідники inbox/runs-walks/gen/.
RUN = 'hrupova-probizhka-z-trenerom.webp'          # 01 картка 3:2 (один колір)
COACH = 'trenerka-bizhyt-poperedu-hrupy.webp'      # 02 «Чому» 2:3 (один колір)
MUSICRUN = 'muzychnyi-zabih.webp'                  # 03 картка 3:2 (один колір)
GUIDE = 'prohulianka-z-hidom-mistom.webp'          # 04 картка 3:2 (один колір)
DANCEWALK = 'tantsiuvalna-khoda-mistom.webp'       # 05 картка 3:2 (один колір)
NATURE = 'prohulianka-parkom.webp'                 # 06 картка 3:2 (один колір)
CORP = 'korporatyvnyi-zabih.webp'                  # 07 картка 3:2 (один колір)
STRETCH = 'roztiazhka-na-finishi.webp'             # 08 квадрат («Що входить» s-a, один колір)
EAR = 'bihunka-reguliuie-huchnist.webp'            # 09 квадрат («Чому» s-a)
GEAR = 'navushnyky-i-peredavach-na-starti.webp'    # 10 квадрат («Чому» s-b)
G1 = 'bihunka-usmikhaietsia-na-bihu.webp'          # 11–16 колаж 4:5
G2 = 'hid-rozpovidaie-hrupi.webp'
G3 = 'hrupa-bizhyt-naberezhnoiu.webp'
G4 = 'tantsi-na-khodi.webp'
G5 = 'uchasnyk-slukhaie-hida.webp'
G6 = 'druzi-tantsiuiut-na-finishi.webp'
HANDOUT = 'vydacha-navushnykiv-na-starti.webp'     # 17 2:3 («Що входить» s-main)
MIC = 'tekhnik-daie-peredavach-trenerovi.webp'     # 18 4:5 («Що входить» s-b)
FINAL = 'tantsi-pislia-finishu.webp'               # 19 16:9 («Як замовити»)

TITLE = 'Забіги та прогулянки в навушниках: голос ведучого на ходу | SILENT'
DESC = ('Бездротові навушники для забігів і прогулянок: голос тренера чи гіда й музика звучать у навушниках '
        'усієї групи на ходу. Групові пробіжки, музичні забіги, прогулянки з гідом. Київ і виїзд по Україні.')
OG_T = 'Забіги та прогулянки з бездротовими навушниками | SILENT'
OG_D = 'Голос тренера чи гіда й музика в навушниках усієї групи на ходу: пробіжки, музичні забіги, прогулянки й танцювальна хода містом.'
OG_ALT = 'Група бігунів слухає тренера в бездротових навушниках SILENT під час пробіжки'

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
rep('images/conferences/og-conferences.jpg', 'images/runs-walks/og-runs-walks.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Забіги та прогулянки",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для забігів і прогулянок"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Бігові клуби, тренери, гіди, організатори забігів і міських прогулянок"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-16"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/runs-walks/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/runs-walks/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/runs-walks/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Забіги та прогулянки</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long exp-title--split"><span class="t-lead">Забіги та прогулянки</span> <span class="t-sub">з бездротовими навушниками</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Тренер чи гід веде групу з портативним передавачем, а його голос і музика звучать у бездротових навушниках кожного учасника просто на ходу. Пробіжка, музичний забіг, прогулянка містом чи танцювальна хода: SILENT дає передавач із мікрофоном і видає навушники на старті.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="runs_walks_hero_order">Обговорити маршрут</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Звук на ходу</b> <span>Передавач рухається з групою.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА ЗАБІГУ ЧИ ПРОГУЛЯНЦІ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="runs-walks">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Тренерка з мікрофоном біжить попереду групи, бігуни слухають її в навушниках SILENT"' % (IMG, COACH))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Бігунка на ходу налаштовує гучність на чаші навушників SILENT"' % (IMG, EAR))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Навушники SILENT і портативний передавач лежать на лаві перед стартом"' % (IMG, GEAR))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Ведучого чути навіть на ходу</h2>\n'
    '      <p>Коли група рухається, голос тренера чи гіда не доходить до тих, хто позаду: заважають вітер, машини й кроки. Колонку на маршруті з собою не понесеш, а кричати всю дорогу неможливо.</p>\n'
    '      <p>У форматі SILENT ведучий несе портативний передавач і говорить у мікрофон, а кожен учасник чує його в бездротових навушниках так, ніби той іде поруч. Під голос можна пустити музику для темпу чи настрою, і вона не заважає людям довкола.</p>\n'
    '      <p>На фініші ті самі навушники стають вечіркою: на трьох каналах звучить різна музика, кожен перемикає її одним дотиком, а колір підсвітки показує, хто що слухає.</p>\n'
    '      <p class="story-sub story-close">Голос ведучого. Музика для темпу. Танці на фініші.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де навушники допомагають на маршруті</h2>')
cards = [
    (RUN, '50% 45%', 'Групова пробіжка: бігуни слухають тренера в навушниках SILENT', 'Групова пробіжка з тренером',
     'Тренер біжить разом із групою й підказує темп і техніку в мікрофон, а його чує кожен бігун, навіть у хвості групи.'),
    (MUSICRUN, '50% 45%', 'Учасники музичного забігу біжать під спільний плейлист у навушниках SILENT', 'Музичний забіг',
     'Розважальний забіг під спільний плейлист у навушниках: музика задає темп усій групі, а на маршруті не потрібні колонки.'),
    (GUIDE, '50% 45%', 'Гід веде групу вулицями міста, учасники слухають його в навушниках SILENT', 'Прогулянка з гідом',
     'Міська прогулянка чи екскурсія пішки: гід говорить у мікрофон, і кожен у групі чує розповідь навіть на гамірній вулиці.'),
    (DANCEWALK, '50% 45%', 'Група танцює на ходу вулицею міста в навушниках SILENT', 'Танцювальна хода містом',
     'Група йде маршрутом під музику в навушниках і зупиняється потанцювати, а місто довкола чує лише сміх і кроки.'),
    (NATURE, '50% 45%', 'Прогулянка парком: група слухає ведучу в навушниках SILENT', 'Прогулянка парком',
     'Прогулянка парком чи стежкою: ведучий розповідає про місце, а тиша довкола лишається для птахів і перехожих.'),
    (CORP, '50% 45%', 'Колеги на корпоративному забігу біжать у навушниках SILENT', 'Корпоративний забіг',
     'Спільна пробіжка для команди: тренер веде групу через мікрофон, а на фініші ті самі навушники стають вечіркою.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на маршруті</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на маршруті</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Передавач у ведучого</b> <span>Тренера чи гіда запрошуєте ви, а SILENT дає портативний передавач із мікрофоном, який ведучий несе з собою.</span></li>\n'
    '        <li><b>Група тримається разом</b> <span>Учасники рухаються поруч із ведучим і чують його голос разом із музикою. У кожного в навушниках свій регулятор гучності.</span></li>\n'
    '        <li><b>Три канали для фінішу</b> <span>На фініші навушники перемикаються на вечірку: три канали з різною музикою, а колір підсвітки показує, хто що слухає.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT налаштовує обладнання, видає навушники на старті, супроводжує подію і збирає комплект на фініші відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук на маршруті беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви прокладаєте маршрут і запрошуєте тренера чи гіда, а <a href="/">SILENT</a> відповідає за звук: ведучого чує кожен, а музика не заважає нікому довкола.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для учасників;</span></li>\n'
    '        <li><span>портативний передавач із мікрофоном для ведучого;</span></li>\n'
    '        <li><span>плейлисти SILENT для темпу й танців на фініші;</span></li>\n'
    '        <li><span>видача навушників на старті й збір на фініші;</span></li>\n'
    '        <li><span>технічний супровід протягом події.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="На старті учасникам видають навушники SILENT"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Розтяжка на фініші: група слухає тренерку в навушниках SILENT"' % (IMG, STRETCH))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT передає тренеру портативний передавач із мікрофоном перед стартом"' % (IMG, MIC))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від маршруту до першого кроку</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату, маршруту й кількості учасників: пробіжка, забіг, прогулянка чи хода, танці на фініші чи ні. На цій основі визначаємо комплект і логістику.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Танці після фінішу: учасники забігу танцюють у світних навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, місце старту й фінішу, формат і орієнтовну кількість учасників.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, передавачі для ведучих, плейлисти й точки видачі та збору.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час на старті й порядок видачі навушників учасникам.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо подію</h3>\n        <p>Налаштовуємо передавач і мікрофон, видаємо навушники на старті, а на фініші збираємо комплект відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="runs_walks_process_order">Обговорити маршрут</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="sport"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Забіги та прогулянки" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Забіги й прогулянки лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/sport/">спортивні події</a>, <a href="/experiences/tours/">екскурсії з радіогідом</a>, <a href="/experiences/yoga/">йога та ecstatic dance</a> і <a href="/experiences/public-spaces/">заходи в громадських просторах</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/radiohid-dlia-ekskursii/">радіогід для екскурсії</a> і <a href="/blog/yak-organizuvaty-zakhid-u-parku/">як організувати захід у парку</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на забігах і прогулянках')
Q = [
 ('Чи надаєте ви тренера чи гіда?', 'Ні, тренера чи гіда запрошуєте ви. SILENT дає портативний передавач із мікрофоном, налаштовує звук і видає учасникам навушники.', ''),
 ('Як учасники чують ведучого на ходу?', 'Ведучий несе портативний передавач і говорить у мікрофон, а група рухається разом із ним і чує його голос у навушниках.', ''),
 ('Чи можна поєднати голос ведучого з музикою?', 'Так, музика для темпу чи настрою може звучати разом із голосом: попередьте команду, ми налаштуємо.', ''),
 ('Чи можна на фініші влаштувати танці?', 'Так. Ті самі навушники перемикаються на Silent Disco: три канали з різною музикою, кожен обирає свій одним дотиком.', ''),
 ('Скільки коштують навушники на забіг чи прогулянку?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Хто видає й збирає навушники?', 'Команда SILENT: видаємо навушники на старті й збираємо на фініші. Порядок видачі погоджуємо з організатором заздалегідь.', ''),
 ('Чи можна налаштувати гучність у навушниках?', 'Так. У навушниках є регулятор та обмежувач гучності, а кожен учасник налаштовує рівень звуку для себе. Обмежувач допомагає контролювати рівень звуку, але не є гарантією абсолютної безпеки для слуху.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="runs_walks_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="runs_walks_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для забігу чи прогулянки</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо подія триває кілька днів чи потрібно кілька передавачів для груп, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте забіг чи прогулянку? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про формат, маршрут і кількість учасників. Ми підкажемо, як організувати голос ведучого й музику в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, маршруту, формату й приблизної кількості учасників.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для забігу чи прогулянки</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Забіг чи прогулянка</option>')

# Інші формати: H1 не про Silent Disco (правило власника, 15.11.2026).
rep('<h2 class="h2 reveal">Інші формати подій від SILENT</h2>', '<h2 class="h2 reveal">Інші формати подій від SILENT</h2>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
# 16.11.2026 власник: фото техніка опустити, щоб було видно обличчя (слот s-b горизонтальний, кадр 4:5)
rep_re(r'<img style="object-position:50% 50%"( width="\d+" height="\d+" class="s-b" src="\.\./\.\./images/runs-walks/tekhnik-daie)',
       r'<img style="object-position:50% 12%"\g<1>')
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
