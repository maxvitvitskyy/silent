"""Одноразовий генератор сторінки /experiences/sport/ (спортивні події з навушниками, 15.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Факти погоджено з власником 15.11.2026: три сценарії (голос тренера в
навушниках на групових тренуваннях, розминка перед стартом, silent disco після змагань); тренера чи ведучого
запрошує організатор, мікрофон-передавач дає SILENT; зони для вболівальників НЕ пропонуємо; умови як для всіх
форматів. На кадрах тренувань і розминки всі навушники ОДНОГО кольору (один канал).
Запуск: python3 tools/gen_sport_page.py  (далі python3 tools/build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'sport', 'index.html')
IMG = '../../images/sport/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'sport', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

# Фото (15.11.2026): згенеровані в ChatGPT власника за референсом навушників; вихідники inbox/sport/gen/.
PARK = 'trenuvannia-v-parku.webp'                 # 01 картка 3:2 (один колір)
COACH = 'trener-z-mikrofonom-vede-hrupu.webp'     # 02 «Чому» 2:3 (один колір)
WARMUP = 'rozmynka-pered-startom.webp'            # 03 картка 3:2 (один колір)
DANCEFIT = 'tantsiuvalnyi-fitnes.webp'            # 04 картка 3:2 (один колір)
CORP = 'korporatyvnyi-sportyvnyi-den.webp'        # 05 картка 3:2 (один колір)
AFTER = 'silent-disco-pislia-zmahan.webp'         # 06 картка 3:2 (різні кольори)
CITY = 'trenuvannia-na-naberezhnii.webp'          # 07 картка 3:2 (один колір)
STRETCH = 'roztiazhka-pislia-trenuvannia.webp'    # 08 квадрат («Що входить» s-a, один колір)
EAR = 'uchasnytsia-reguliuie-huchnist.webp'       # 09 квадрат («Чому» s-a)
GEAR = 'navushnyky-i-mikrofon-na-lavi.webp'       # 10 квадрат («Чому» s-b)
G1 = 'biehunka-pislia-finishu-tantsiuie.webp'     # 11–16 колаж 4:5
G2 = 'druzi-z-medaliamy-tantsiuiut.webp'
G3 = 'trenuvannia-krupnyi-plan.webp'
G4 = 'komanda-pislia-turniru.webp'
G5 = 'zhinka-na-rozmyntsi.webp'
G6 = 'chempion-tantsiuie-vvecheri.webp'
HANDOUT = 'vydacha-navushnykiv-na-starti.webp'    # 17 2:3 («Що входить» s-main)
MIC = 'tekhnik-chiplyaie-mikrofon-treneru.webp'   # 18 4:5 («Що входить» s-b)
FINAL = 'afterparty-turniru-vvecheri.webp'        # 19 16:9 («Як замовити»)

TITLE = 'Бездротові навушники для спортивних подій і тренувань | SILENT'
DESC = ('Навушники для спортивних подій, групових тренувань і забігів: учасники чують тренера й музику без колонок. Обладнання під ключ, Київ і виїзд по Україні.')
OG_T = 'Спортивні події з бездротовими навушниками | SILENT'
OG_D = 'Голос тренера й музика в навушниках кожного учасника: тренування, розминка перед стартом і Silent Disco після змагань.'
OG_ALT = 'Учасники групового тренування в парку слухають тренера в бездротових навушниках SILENT'

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
rep('images/conferences/og-conferences.jpg', 'images/sport/og-sport.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Спортивні події",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для спортивних подій"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Організатори забігів, турнірів, спортивних днів і групових тренувань"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-15"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/sport/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/sport/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/sport/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Спортивні події</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long exp-title--split"><span class="t-lead">Спортивні події</span> <span class="t-sub">з бездротовими навушниками</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Голос тренера й музика звучать у бездротових навушниках кожного учасника, тож команди чути навіть у парку, на набережній чи серед шуму старту. Розминка перед забігом, групове тренування чи Silent Disco після змагань: SILENT привозить систему, дає мікрофон для тренера й видає навушники.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="sport_hero_order">Обговорити подію</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>Голос тренера</b> <span>Чути кожному учаснику.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА СПОРТИВНІЙ ПОДІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="sport">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Тренер із мікрофоном веде групове тренування, учасники слухають його в навушниках SILENT"' % (IMG, COACH))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Учасниця тренування налаштовує гучність на чаші навушників SILENT"' % (IMG, EAR))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Навушники SILENT і мікрофон тренера лежать на лаві біля спортивного майданчика"' % (IMG, GEAR))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Тренера чути, навіть коли довкола шумно</h2>\n'
    '      <p>На відкритому майданчику голос тренера розлітається: задні ряди не чують команд, а колонку поруч глушать вітер і шум міста. Тренерові доводиться кричати, а учасникам перепитувати.</p>\n'
    '      <p>У форматі SILENT тренер говорить у мікрофон, а кожен учасник чує його в бездротових навушниках так, ніби той стоїть поруч. Під голос можна пустити музику для темпу, і вона не заважає людям довкола.</p>\n'
    '      <p>Після змагань ті самі навушники стають вечіркою: на трьох каналах звучить різна музика, кожен перемикає її одним дотиком, а колір підсвітки показує, хто що слухає.</p>\n'
    '      <p class="story-sub story-close">Голос тренера. Музика для темпу. Вечірка після фінішу.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де навушники допомагають на спортивній події</h2>')
cards = [
    (PARK, '50% 45%', 'Групове тренування в парку: усі учасники слухають тренера в навушниках SILENT', 'Групове тренування в парку',
     'Функціональне тренування чи кардіо просто неба: тренер говорить у мікрофон, і його чує кожен у групі, навіть у задньому ряду.'),
    (WARMUP, '50% 45%', 'Учасники забігу розминаються перед стартом у навушниках SILENT', 'Розминка перед стартом',
     'Спільна розминка учасників забігу чи турніру під музику й голос ведучого в навушниках, без колонок, які перекрикують одна одну на старті.'),
    (DANCEFIT, '50% 45%', 'Танцювальний фітнес просто неба: група повторює рухи тренерки в навушниках SILENT', 'Танцювальний фітнес',
     'Музика й рахунок тренера звучать прямо у вухах, тож група тримає ритм навіть на вулиці, а перехожим не заважає гучний бас.'),
    (CORP, '50% 45%', 'Колеги на корпоративному спортивному дні тренуються в навушниках SILENT', 'Корпоративний спортивний день',
     'Спільне тренування для команди в межах спортивного дня: тренер веде групу через мікрофон, а ввечері ті самі навушники стають вечіркою.'),
    (AFTER, '50% 45%', 'Учасники турніру з медалями танцюють у різнокольорових навушниках SILENT', 'Silent Disco після змагань',
     'Після фінішу чи нагородження учасники й гості танцюють у навушниках на трьох каналах з різною музикою, а сусідні будинки не чують басу.'),
    (CITY, '50% 45%', 'Ранкове тренування на набережній: група слухає тренера в навушниках SILENT', 'Тренування в місті',
     'Набережна, площа чи двір, де колонки недоречні: тренування звучить лише в навушниках учасників, а місто довкола живе своїм життям.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на спортивній події</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на спортивній події</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Мікрофон для тренера</b> <span>Тренера чи ведучого запрошуєте ви, а SILENT дає мікрофон-передавач і налаштовує звук до старту.</span></li>\n'
    '        <li><b>Голос тренера й музика для темпу</b> <span>Учасники чують команди тренера разом із музикою. У кожного в навушниках свій регулятор гучності.</span></li>\n'
    '        <li><b>Три канали для вечірки</b> <span>Після змагань навушники перемикаються на вечірку: три канали з різною музикою, а колір підсвітки показує, хто що слухає.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники, супроводжує подію і збирає комплект після завершення відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук на спортивній події беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви збираєте учасників і запрошуєте тренера, а <a href="/">SILENT</a> відповідає за звук: команди чує кожен, а музика не заважає нікому довкола.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для учасників;</span></li>\n'
    '        <li><span>мікрофон-передавач для тренера чи ведучого;</span></li>\n'
    '        <li><span>плейлисти SILENT для тренування й вечірки;</span></li>\n'
    '        <li><span>видача навушників на старті й збір наприкінці;</span></li>\n'
    '        <li><span>технічний супровід протягом події.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="На старті учасникам видають навушники SILENT"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Розтяжка після тренування: група слухає тренерку в навушниках SILENT"' % (IMG, STRETCH))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає тренеру закріпити мікрофон перед тренуванням"' % (IMG, MIC))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від ідеї до першої команди тренера</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з формату, локації й кількості учасників: тренування, розминка, вечірка після змагань чи все разом. На цій основі визначаємо комплект і логістику.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Вечірка після турніру: учасники танцюють у світних навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, локацію, формат події й орієнтовну кількість учасників.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофони для тренерів, плейлисти, живлення й план на випадок дощу.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час монтажу й видачу навушників учасникам.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо мікрофон і сигнал, видаємо навушники, а після завершення збираємо комплект відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="sport_process_order">Обговорити подію</a>')

# ---------- Стрічка форматів ----------
rep('id="more" data-default-cat="business"', 'id="more" data-default-cat="sport"')
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Спортивні події" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Спортивна подія лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/yoga/">йога та ecstatic dance</a>, <a href="/experiences/festivals/">фестивалі</a>, <a href="/experiences/corporate/">корпоративи</a> і <a href="/experiences/public-spaces/">заходи в громадських просторах</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/yoga-na-pryrodi/">йога на природі</a> і <a href="/blog/yak-organizuvaty-zvuk-na-zakhodi-prosto-neba/">як організувати звук на заході просто неба</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на спортивних подіях')
Q = [
 ('Чи надаєте ви тренера?', 'Ні, тренера чи ведучого запрошуєте ви. SILENT дає мікрофон-передавач, налаштовує звук і видає учасникам навушники.', ''),
 ('Чи чутимуть учасники тренера на вулиці?', 'Так. Тренер говорить у мікрофон, і його голос звучить у навушниках кожного учасника, тож команди чути навіть серед шуму міста чи старту.', ''),
 ('Чи можна поєднати голос тренера з музикою?', 'Так, музика для темпу може звучати разом із голосом тренера: попередьте команду, ми налаштуємо.', ''),
 ('Чи можна після змагань влаштувати вечірку?', 'Так. Ті самі навушники перемикаються на Silent Disco: три канали з різною музикою, а сусіди не чують басу.', ''),
 ('Скільки коштують навушники на спортивну подію?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Чи можна провести подію просто неба?', 'Так, якщо поруч є живлення для передавача і є запасний план на дощ: намет, навіс чи приміщення. Умови локації обговорюємо заздалегідь.', ''),
 ('Чи можна налаштувати гучність у навушниках?', 'Так. У навушниках є регулятор та обмежувач гучності, а кожен гість налаштовує рівень звуку для себе. Обмежувач допомагає контролювати рівень звуку, але не є гарантією абсолютної безпеки для слуху.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="sport_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="sport_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для спортивної події</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо подія триває кілька днів чи потрібно кілька мікрофонів для тренерів, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте спортивну подію? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про формат, локацію й кількість учасників. Ми підкажемо, як організувати голос тренера й музику в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, локації, формату й приблизної кількості учасників.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для спортивної події</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Спортивна подія</option>')

# Фото техніка в «Що входить»: обличчя вгорі кадру, тож опускаємо видиму частину (власник, 15.11.2026).
rep_re(r'<img style="object-position:50% 50%"( width="\d+" height="\d+" class="s-b" src="\.\./\.\./images/sport/tekhnik-chiplyaie)',
       r'<img style="object-position:50% 12%"\g<1>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
