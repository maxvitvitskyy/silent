"""Одноразовий генератор сторінки /experiences/trainings/ (тренінги та навчання з навушниками, 16.11.2026).

Бере каркас /experiences/conferences/ і підміняє кожен текст і картинку на свої (кожна заміна має збігтися
рівно один раз, інакше скрипт падає). Факти погоджено з власником 16.11.2026: чотири сценарії (голос тренера
в навушниках; до трьох груп в одному залі, кожна на своєму каналі зі своїм мікрофоном; навчання на виїзді й
просто неба, зокрема на виробництві чи складі; Silent Disco після навчання). Тренера запрошує клієнт,
мікрофон-передавач дає SILENT; умови як для всіх форматів. На кадрах навчання всі навушники ОДНІЄЇ групи
одного кольору (один канал); різні кольори лише на кадрі з кількома групами (кожна група свій колір) і на вечірці.
Запуск: python3 tools/gen_trainings_page.py  (далі python3 tools/build_en.py)
УВАГА: запуск ПЕРЕЗАПИСУЄ сторінку; після ручних правок у ній його не запускати.
"""
import base64, io, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'experiences', 'conferences', 'index.html')
DST = os.path.join(ROOT, 'experiences', 'trainings', 'index.html')
IMG = '../../images/trainings/'

def lqip(name):
    im = Image.open(os.path.join(ROOT, 'images', 'trainings', name)).convert('RGB')
    im.thumbnail((24, 24))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

# Фото: згенеровані в ChatGPT власника за референсом навушників; вихідники inbox/trainings/gen/.
HALL = 'trening-u-velykii-zali.webp'               # 01 картка 3:2 (один колір)
COACH = 'trenerka-z-mikrofonom-vede-trening.webp'  # 02 «Чому» 2:3 (один колір)
GROUPS = 'try-hrupy-v-odnii-zali.webp'             # 03 картка 3:2 (три групи, у кожної свій колір)
OUTDOOR = 'trening-prosto-neba.webp'               # 04 картка 3:2 (один колір)
PLANT = 'navchannia-na-vyrobnytstvi.webp'          # 05 картка 3:2 (один колір)
OFFSITE = 'vyiznyi-trening-na-bazi.webp'           # 06 картка 3:2 (один колір)
AFTER = 'silent-disco-pislia-navchannia.webp'      # 07 картка 3:2 (різні кольори)
NOTES = 'uchasnyk-robyt-notatky.webp'              # 08 квадрат («Що входить» s-a, один колір)
EAR = 'uchasnytsia-reguliuie-huchnist.webp'        # 09 квадрат («Чому» s-a)
GEAR = 'navushnyky-i-mikrofon-na-stoli-v2.webp'    # 10 квадрат («Чому» s-b); v2 16.11.2026: довгий шнур мікрофона
G1 = 'uchasnytsia-slukhaie-trenera.webp'           # 11–16 колаж 4:5
G2 = 'robota-v-parakh.webp'
G3 = 'trener-pokazuie-na-fliptchart.webp'
G4 = 'hrupa-v-krugu-prosto-neba.webp'
G5 = 'uchasnyk-pidnimaie-ruku.webp'
G6 = 'kolehy-tantsiuiut-vvecheri.webp'
HANDOUT = 'vydacha-navushnykiv-na-reiestratsii.webp'   # 17 2:3 («Що входить» s-main)
MIC = 'tekhnik-nalashtovuie-mikrofon-trenerci.webp'    # 18 4:5 («Що входить» s-b)
FINAL = 'vechirka-pislia-treningu.webp'                # 19 16:9 («Як замовити»)

TITLE = 'Тренінги й навчання в навушниках: голос тренера кожному | SILENT'
DESC = ('Бездротові навушники для тренінгів і навчання: голос тренера чути кожному учаснику, до трьох груп '
        'в одному залі, навчання на виїзді й просто неба, Silent Disco після програми. Київ і виїзд по Україні.')
OG_T = 'Тренінги й навчання з бездротовими навушниками | SILENT'
OG_D = 'Голос тренера в навушниках кожного учасника: до трьох груп в одному залі, навчання на виїзді й Silent Disco після програми.'
OG_ALT = 'Учасники тренінгу у великій залі слухають тренера в бездротових навушниках SILENT'

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
rep('images/conferences/og-conferences.jpg', 'images/trainings/og-trainings-v2.jpg', count=2)
rep('Учасники конференції за столами в бездротових навушниках Silent Disco', OG_ALT, count=2)
rep('"name": "Конференції",', '"name": "Тренінги й навчання",')
rep('"name": "Silent Disco для конференцій"', '"name": "Бездротові навушники SILENT для тренінгів і навчання"')
rep('"name": "Організатори конференцій, форумів і бізнес-подій"', '"name": "Тренери, HR і L&D-команди, організатори навчальних програм"')
rep_re(r'"dateModified": "[0-9-]+"', '"dateModified": "2026-11-16"')
s = s.replace('https://silent.org.ua/experiences/conferences/', 'https://silent.org.ua/experiences/trainings/')
s = s.replace('https://silent.org.ua/en/experiences/conferences/', 'https://silent.org.ua/en/experiences/trainings/')
rep('<a href="/en/experiences/conferences/" hreflang="en" lang="en">EN</a>', '<a href="/en/experiences/trainings/" hreflang="en" lang="en">EN</a>')

# ---------- HERO ----------
rep('<span class="crumb-now">Конференції</span>', '<span class="crumb-now">Тренінги й навчання</span>')
rep('<h1 class="exp-title exp-title--long"><span class="t-lead">Бездротові навушники</span> <span class="t-sub">для конференцій та бізнес-заходів</span></h1>',
    '<h1 class="exp-title exp-title--long exp-title--split"><span class="t-lead">Тренінги й навчання</span> <span class="t-sub">з бездротовими навушниками</span></h1>')
rep_re(r'<p class="exp-lead">Доповіді, воркшопи.*?</p>',
    '<p class="exp-lead">Тренер говорить у мікрофон, а кожен учасник чує його в бездротових навушниках, навіть у великій залі, у цеху чи просто неба. В одному просторі можуть працювати до трьох груп, кожна на своєму каналі. SILENT привозить систему, дає мікрофони для тренерів і видає навушники.</p>')
rep('data-cta="conferences_hero_order">Обговорити конференцію</a>', 'data-cta="trainings_hero_order">Обговорити навчання</a>')
rep('<span class="f-txt"><b>3 аудіоканали</b> <span>Стандартний формат.</span></span>',
    '<span class="f-txt"><b>До трьох груп</b> <span>В одному залі одночасно.</span></span>')

gal1 = [(G1, '50% 40%'), (G2, '50% 40%'), (G3, '50% 40%')]
gal2 = [(G4, '50% 40%'), (G5, '50% 40%'), (G6, '50% 40%')]
def col(items):
    return '\n'.join('        <img style="object-position:%s" width="640" height="640" src="%s%s" alt="">' % (pos, IMG, n) for n, pos in items * 2)
rep_re(r'(<div class="gallery-col gallery-col-1">\n).*?(\n      </div>\n      <div class="gallery-col gallery-col-2">\n).*?(\n      </div>\n    </div>\n  </div>\n</section>)',
       r'\g<1>' + col(gal1).replace('\\', '\\\\') + r'\g<2>' + col(gal2).replace('\\', '\\\\') + r'\g<3>')

# ---------- Чому навушники ----------
rep('<!-- ТИХИЙ ЗВУК НА КОНФЕРЕНЦІЇ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="conferences">',
    '<!-- ЧОМУ НАВУШНИКИ НА ТРЕНІНГУ: знімки ліворуч, текст праворуч -->\n<section class="exp-section exp-story" id="trainings">')
rep('src="../../images/conferences/konferentsiya-velyka-zala-zi-stsenoyu.webp" alt="Велика конференц-зала зі сценою, учасники слухають доповідь у навушниках Silent Disco"',
    'src="%s%s" alt="Тренерка з мікрофоном веде тренінг, учасники слухають її в навушниках SILENT"' % (IMG, COACH))
rep('class="s-a" src="../../images/conferences/konferentsiya-uchasnyky-za-stolamy-v-navushnykakh.webp" alt="Учасники конференції за столами слухають доповідь у навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Учасниця тренінгу налаштовує гучність на чаші навушників SILENT"' % (IMG, EAR))
rep('class="s-b" src="../../images/conferences/konferentsiya-pereklad-v-navushnykakh.webp" alt="Учасниця конференції з бейджем налаштовує бездротові навушники Silent Disco"',
    'class="s-b" src="%s%s" alt="Навушники SILENT і мікрофон тренера лежать на столі перед тренінгом"' % (IMG, GEAR))
rep_re(r'<h2 class="exp-h2">Коли звичайного звуку недостатньо</h2>.*?<p class="story-sub story-close">.*?</p>',
    '<h2 class="exp-h2">Кожен учасник чує тренера так, ніби сидить у першому ряду</h2>\n'
    '      <p>У великій залі голос тренера губиться: задні ряди перепитують, колонки дають луну, а в цеху чи на вулиці говорити доводиться крізь шум. Тренер втомлюється, учасники відволікаються.</p>\n'
    '      <p>У форматі SILENT тренер говорить у мікрофон, а кожен учасник чує його в бездротових навушниках чисто й поруч. Гучність кожен налаштовує для себе. Якщо в одному просторі працюють кілька груп, у кожної свій канал і свій тренер, і групи не заважають одна одній.</p>\n'
    '      <p>Коли програма закінчується, ті самі навушники стають вечіркою: на трьох каналах звучить різна музика, кожен перемикає її одним дотиком, а колір підсвітки показує, хто що слухає.</p>\n'
    '      <p class="story-sub story-close">Голос тренера. Кілька груп в одному залі. Вечірка після програми.</p>')

# ---------- Сценарії ----------
rep('<h2 class="exp-h2">Як використовувати SILENT на конференції</h2>', '<h2 class="exp-h2">Де навушники допомагають на навчанні</h2>')
cards = [
    (HALL, '50% 45%', 'Учасники тренінгу у великій залі слухають тренера в навушниках SILENT', 'Тренінг у великій залі',
     'Тренер говорить у мікрофон, і його однаково чують і в першому, і в останньому ряду, без колонок і луни.'),
    (GROUPS, '50% 45%', 'Три групи навчаються в одному залі, у кожної навушники свого кольору', 'Кілька груп в одному залі',
     'До трьох груп працюють одночасно: у кожної свій тренер, свій мікрофон і свій канал, тож групи не перекрикують одна одну.'),
    (OUTDOOR, '50% 45%', 'Тренінг просто неба: група на траві слухає тренера в навушниках SILENT', 'Тренінг просто неба',
     'Сесія в парку чи на терасі: вітер і шум міста не заважають, бо голос тренера звучить у навушниках кожного учасника.'),
    (PLANT, '50% 45%', 'Навчання на виробництві: працівники слухають інструктора в навушниках SILENT', 'Навчання на виробництві',
     'Інструктаж чи екскурсія цехом або складом: інструктор веде групу, і його чути навіть поруч із працюючим обладнанням.'),
    (OFFSITE, '50% 45%', 'Виїзний тренінг на базі відпочинку: команда в навушниках SILENT', 'Виїзний тренінг',
     'Стратегічна сесія чи навчання команди на базі відпочинку, де немає зали зі звуком: усе потрібне ми привозимо із собою.'),
    (AFTER, '50% 45%', 'Учасники навчання танцюють увечері в різнокольорових навушниках SILENT', 'Silent Disco після навчання',
     'Після програми дня учасники танцюють у навушниках на трьох каналах з різною музикою. Ті самі навушники, нічого не треба перевозити.'),
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
rep('<h2 class="exp-h2">Що дає формат конференції в навушниках</h2>', '<h2 class="exp-h2">Як працюють навушники на тренінгу</h2>')
rep_re(r'(<h2 class="exp-h2">Як працюють навушники на тренінгу</h2>\n      <ol class="gear-steps">\n).*?(\n      </ol>)',
    r'\g<1>'
    '        <li><b>Мікрофон для тренера</b> <span>Тренера запрошуєте ви, а SILENT дає мікрофон-передавач і налаштовує звук до початку програми.</span></li>\n'
    '        <li><b>До трьох груп одночасно</b> <span>Кожна група слухає свого тренера на своєму каналі, а колір підсвітки навушників показує, хто в якій групі.</span></li>\n'
    '        <li><b>Своя гучність у кожного</b> <span>У навушниках є регулятор і обмежувач гучності, тож кожен учасник налаштовує звук для себе.</span></li>\n'
    '        <li><b>Технічна організація під ключ</b> <span>SILENT привозить і налаштовує обладнання, видає навушники, супроводжує навчання і збирає комплект після завершення відповідно до погоджених умов.</span></li>'
    r'\g<2>')

# ---------- Що входить ----------
rep('<h2 class="exp-h2">Організацію аудіоформату беремо на себе</h2>', '<h2 class="exp-h2">Звук на навчанні беремо на себе</h2>')
rep('<p><a href="/">SILENT</a> — це не просто навушники. Ми організовуємо технічну частину аудіоформату, щоб вам не довелося самостійно розбиратися з обладнанням.</p>',
    '<p>Ви готуєте програму й запрошуєте тренерів, а <a href="/">SILENT</a> відповідає за звук: кожен учасник чує свого тренера, хай де проходить навчання.</p>')
rep_re(r'(<ul class="gear-steps gear-steps--plain">\n).*?(\n      </ul>)',
    r'\g<1>'
    '        <li><span>бездротові навушники для учасників;</span></li>\n'
    '        <li><span>мікрофони-передавачі для тренерів, до трьох груп одночасно;</span></li>\n'
    '        <li><span>плейлисти SILENT для перерв і вечірки;</span></li>\n'
    '        <li><span>видача навушників на реєстрації й збір наприкінці;</span></li>\n'
    '        <li><span>технічний супровід протягом програми.</span></li>'
    r'\g<2>')
rep('class="s-main" src="../../images/conferences/konferentsiya-hala-vecheria-stoly.webp" alt="Накриті столи в залі, на столах бездротові навушники Silent Disco"',
    'class="s-main" src="%s%s" alt="На реєстрації учасникам тренінгу видають навушники SILENT"' % (IMG, HANDOUT))
rep('class="s-a" src="../../images/conferences/konferentsiya-audytoriya-v-synikh-navushnykakh.webp" alt="Повна зала учасників конференції слухає виступ у світних синіх навушниках Silent Disco"',
    'class="s-a" src="%s%s" alt="Учасник тренінгу робить нотатки, слухаючи тренера в навушниках SILENT"' % (IMG, NOTES))
rep('class="s-b" src="../../images/conferences/konferentsiya-velyka-zala-z-navushnykamy-na-stiltsyakh.webp" alt="Велика конференц-зала: на кожному стільці висять сині навушники Silent Disco, на сцені три екрани"',
    'class="s-b" src="%s%s" alt="Технік SILENT допомагає тренерці закріпити мікрофон перед тренінгом"' % (IMG, MIC))

# ---------- Як замовити ----------
rep('<h2 class="exp-h2">Від планування до готового аудіорішення</h2>', '<h2 class="exp-h2">Від програми до першого слова тренера</h2>')
rep('<p class="process-lead reveal">Починаємо з вашої програми, простору та кількості учасників. На цій основі визначаємо, яка конфігурація SILENT підійде для події.</p>',
    '<p class="process-lead reveal">Починаємо з програми, простору й кількості учасників: одна група чи кілька, зала, цех чи просто неба, вечірка після навчання чи ні. На цій основі визначаємо комплект і логістику.</p>')
rep('src="../../images/conferences/konferentsiya-afterparty-v-atriumi.webp" alt="Вечірня подія в атріумі: гості слухають музику в навушниках Silent Disco"',
    'src="%s%s" alt="Вечірка після тренінгу: учасники танцюють у світних навушниках SILENT"' % (IMG, FINAL))
rep('<p>Дізнаємося дату, локацію, кількість гостей, формат конференції та потреби в аудіосупроводі.</p>',
    '<p>Дізнаємося дату, локацію, програму, кількість груп і учасників.</p>')
rep('<h3>Узгоджуємо конфігурацію</h3>\n        <p>Визначаємо кількість навушників, джерела звуку, канали та технічні умови.</p>',
    '<h3>Узгоджуємо комплект</h3>\n        <p>Визначаємо кількість навушників, мікрофони для тренерів, канали для груп і живлення на локації.</p>')
rep('<p>Погоджуємо логістику, час монтажу та організацію видачі навушників.</p>',
    '<p>Погоджуємо логістику, час монтажу й видачу навушників учасникам.</p>')
rep('<h3>Супроводжуємо подію</h3>\n        <p>Встановлюємо систему, перевіряємо її роботу, забезпечуємо технічний супровід і збираємо обладнання після завершення відповідно до узгодженого пакета.</p>',
    '<h3>Супроводжуємо навчання</h3>\n        <p>Встановлюємо систему, перевіряємо мікрофони й канали, видаємо навушники, а після завершення збираємо комплект відповідно до узгодженого пакета.</p>')
rep('data-cta="conferences_process_order">Обговорити конференцію</a>', 'data-cta="trainings_process_order">Обговорити навчання</a>')

# ---------- Стрічка форматів ----------
rep('<!-- UC-STRIP:START exclude="Конференції" -->', '<!-- UC-STRIP:START exclude="Тренінги й навчання" -->')
rep_re(r'<p class="section-lead reveal">SILENT працює не лише для конференцій\..*?</p>',
    '<p class="section-lead reveal">Навчання лише один із форматів. У розділі «<a href="/experiences/">Тихі враження</a>» зібрано інші: <a href="/experiences/conferences/">конференції</a>, <a href="/experiences/translation/">синхронний переклад</a>, <a href="/experiences/corporate/">корпоративи</a> і <a href="/experiences/tours/">екскурсії з радіогідом</a>. Поради шукайте в <a href="/blog/">блозі</a>: <a href="/blog/idei-dlia-timbildynhu/">ідеї для тімбілдингу</a> і <a href="/blog/navushnyky-na-konferentsii-stsenarii/">навушники на конференції: сценарії</a>.</p>')

# ---------- FAQ ----------
rep('Поширені запитання про Silent Disco для конференцій', 'Поширені запитання про навушники на тренінгах і навчанні')
Q = [
 ('Чи надаєте ви тренера?', 'Ні, тренера запрошуєте ви. SILENT дає мікрофон-передавач, налаштовує звук і видає учасникам навушники.', ''),
 ('Скільки груп може навчатися в одному залі?', 'До трьох груп одночасно. Кожна слухає свого тренера на своєму каналі, у кожного тренера свій мікрофон.', ''),
 ('Чи можна провести навчання просто неба чи на виробництві?', 'Так. Голос тренера звучить у навушниках, тож його чути на вулиці й поруч із працюючим обладнанням. Потрібне живлення для передавача; для вулиці варто мати запасний план на дощ.', ''),
 ('Чи можна після навчання влаштувати вечірку?', 'Так. Ті самі навушники перемикаються на Silent Disco: три канали з різною музикою, кожен обирає свій одним дотиком.', ''),
 ('Скільки коштують навушники на тренінг?', 'Базовий орієнтир: від 12 000 грн за 40 навушників на 4 години. Фінальна вартість залежить від дати, локації, тривалості та кількості навушників.', 'calc'),
 ('Чи працюєте ви за межами Києва?', 'Так, SILENT працює в Києві та виїжджає по Україні. Вартість і можливість виїзду узгоджуємо з урахуванням локації та дати.', 'date'),
 ('Чи можна пустити в навушники презентацію чи відео?', 'Так, звук із ноутбука тренера можна подати в навушники разом із голосом: попередьте команду, ми налаштуємо.', ''),
 ('Чи можна налаштувати гучність у навушниках?', 'Так. У навушниках є регулятор та обмежувач гучності, а кожен учасник налаштовує рівень звуку для себе. Обмежувач допомагає контролювати рівень звуку, але не є гарантією абсолютної безпеки для слуху.', ''),
]
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'
PLUS = '<div class="faq-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg></div>'
def item(i, q, a, cta):
    extra = ''
    if cta == 'calc': extra = '<a href="#price" class="faq-cta" data-cta="trainings_faq_calculator">Порахувати вартість%s</a>' % ARROW
    if cta == 'date': extra = '<a href="#book" class="faq-cta" data-cta="trainings_faq_check_date">Перевірити дату%s</a>' % ARROW
    return ('        <div class="faq-item reveal">\n'
            '          <div class="faq-q" role="button" tabindex="0" aria-expanded="false" aria-controls="bq%d"><h3>%s</h3>%s</div>\n'
            '          <div class="faq-a" id="bq%d" role="region"><p>%s</p>%s</div>\n        </div>' % (i, q, PLUS, i, a, extra))
left = '\n'.join(item(i + 1, *Q[i]) for i in range(4)); right = '\n'.join(item(i + 1, *Q[i]) for i in range(4, 8))
rep_re(r'(<div class="faq-list">\n      <div class="faq-col">\n).*?(\n      </div>\n      <div class="faq-col">\n).*?(\n      </div>\n    </div>\n    <div class="faq-more">)',
       r'\g<1>' + left.replace('\\', '\\\\') + r'\g<2>' + right.replace('\\', '\\\\') + r'\g<3>')

# ---------- Калькулятор, заклик, форма ----------
rep('<h2>Скільки коштує SILENT для конференції</h2>', '<h2>Скільки коштують навушники для тренінгу</h2>')
rep('<p>Для стандартного формату скористайтеся калькулятором. Якщо потрібні додаткові аудіопотоки, переклад чи особливі технічні вимоги, вартість узгоджуємо індивідуально.</p>',
    '<p>Для стандартного формату скористайтеся калькулятором: база розрахована на 40 навушників і 4 години. Якщо навчання триває кілька днів чи потрібні мікрофони для кількох груп, вартість узгоджуємо індивідуально.</p>')
rep('<h2>Плануєте конференцію? Обговорімо аудіоформат</h2>', '<h2>Плануєте тренінг? Обговорімо звук</h2>')
rep('<p>Розкажіть про вашу подію, програму та локацію. Ми допоможемо визначити, чи підійде SILENT для вашого формату, і запропонуємо наступний крок.</p>',
    '<p>Розкажіть про програму, локацію й кількість груп. Ми підкажемо, як організувати голос тренера в навушниках, і запропонуємо наступний крок.</p>')
rep('<p>Дата, локація та приблизна кількість учасників — цього достатньо, щоб почати розмову.</p>',
    '<p>Щоб почати розмову, досить дати, локації, кількості груп і приблизної кількості учасників.</p>')
rep('<h2>Обговорити <span class="em">Silent Disco</span> для конференції</h2>', '<h2>Обговорити <span class="em">навушники</span> для навчання</h2>')
rep('<option selected>Конференція</option>', '<option>Конференція</option>\n                <option selected>Тренінг чи навчання</option>')

# Фото техніка в «Що входить»: обличчя вгорі кадру, тож опускаємо видиму частину (власник, 16.11.2026).
rep_re(r'<img style="object-position:50% 50%"( width="\d+" height="\d+" class="s-b" src="\.\./\.\./images/trainings/tekhnik-nalashtovuie)',
       r'<img style="object-position:50% 15%"\g<1>')

# ---------- контроль ----------
a = s.index('<!-- HERO:'); b = s.index('<!-- Список роликів')
left_over = re.findall(r'.{0,40}(?:конференц|Конференц|conferen).{0,40}', s[a:b])
left_over = [x for x in left_over if '<option>Конференція</option>' not in x and 'conferences/' not in x
             and 'konferentsii' not in x and 'конференції</a>' not in x and 'конференції: сценарії' not in x]
if left_over:
    sys.exit('Лишилися конференції в основному вмісті:\n' + '\n'.join(left_over))
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(s)
print('OK ->', DST, len(s))
