#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Збирає en/index.html з index.html.

Українська сторінка — єдине джерело правди. Англійська не редагується руками:
вона щоразу генерується заново, тож структура, класи, порядок блоків і будь-яка
правка розмітки приходять в англійську версію самі. Тут лежить тільки те, чим
дві версії різняться, — словник рядків, шляхи до файлів і SEO-теги.

Запуск:  python3 tools/build_en.py
Після зміни тексту в index.html прогнати ще раз.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, 'index.html')
DST  = os.path.join(ROOT, 'en', 'index.html')
SRC404 = os.path.join(ROOT, '404.html')
DST404 = os.path.join(ROOT, 'en', '404.html')

NB = ' '   # нерозривний пробіл, яким в українському тексті склеєні прийменники

# ---------------------------------------------------------------- SEO / head
HEAD = [
 ('<html lang="uk">', '<html lang="en">'),
 ('<title>SILENT — одна вечірка. Три музичні світи.</title>',
  '<title>SILENT — one party. Three worlds of music.</title>'),
 ('<meta name="description" content="Silent Disco під ключ у Києві та по Україні: бездротові LED-навушники, 3 канали музики, доставка, налаштування та супровід.">',
  '<meta name="description" content="Full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, 3 music channels, delivery, setup and on-site support.">'),
 ('<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="en_US">'),
 ('<meta property="og:title" content="SILENT — одна вечірка. Три музичні світи.">',
  '<meta property="og:title" content="SILENT — one party. Three worlds of music.">'),
 ('<meta property="og:description" content="Silent Disco під ключ у Києві та по Україні: бездротові LED-навушники, 3 канали музики, доставка, налаштування та супровід.">',
  '<meta property="og:description" content="Full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, 3 music channels, delivery, setup and on-site support.">'),
 ('<meta property="og:url" content="https://silent.org.ua/">',
  '<meta property="og:url" content="https://silent.org.ua/en/">'),
 ('<meta name="twitter:title" content="SILENT — одна вечірка. Три музичні світи.">',
  '<meta name="twitter:title" content="SILENT — one party. Three worlds of music.">'),
 ('<meta name="twitter:description" content="Silent Disco під ключ у Києві та по Україні: бездротові LED-навушники, 3 канали музики, доставка, налаштування та супровід.">',
  '<meta name="twitter:description" content="Full-service silent disco in Kyiv and across Ukraine: wireless LED headphones, 3 music channels, delivery, setup and on-site support.">'),
 ('<link rel="canonical" href="https://silent.org.ua/">',
  '<link rel="canonical" href="https://silent.org.ua/en/">'),
 # JSON-LD: сутність та сама (ті самі @id), змінюється лише мова опису
 ('"description": "SILENT — Silent Disco під ключ у Києві та по Україні: LED-навушники, 3 канали музики, доставка, налаштування та супровід. Для весіль, корпоративів, вечірок, фестивалів, таборів і приватних подій.",',
  '"description": "SILENT — full-service silent disco in Kyiv and across Ukraine: LED headphones, 3 music channels, delivery, setup and on-site support. For weddings, company parties, private events, festivals and camps.",'),
 ('"knowsLanguage": "uk-UA"', '"knowsLanguage": ["uk-UA", "en"]'),
 ('"description": "Організація Silent Disco та інших подій",',
  '"description": "Silent disco and event production",'),
]

# ------------------------------------------------------- SEO / head 404
# Шляхів тут немає: у 404.html усі адреси абсолютні (файл віддають замість
# будь-якої неіснуючої адреси, тож відносні не працюють), і для англійської
# версії їх міняти не треба.
HEAD404 = [
 ('<html lang="uk">', '<html lang="en">'),
 ('<title>Сторінки немає — SILENT</title>', '<title>Page not found — SILENT</title>'),
 ('<meta name="description" content="Сторінки за цією адресою немає. Повертайтесь на головну SILENT — silent disco під ключ у Києві та по Україні.">',
  '<meta name="description" content="There is no page at this address. Head back to the SILENT homepage — full-service silent disco in Kyiv and across Ukraine.">'),
 ('<meta property="og:locale" content="uk_UA">', '<meta property="og:locale" content="en_US">'),
 ('<meta property="og:title" content="Сторінки немає — SILENT">',
  '<meta property="og:title" content="Page not found — SILENT">'),
 ('<meta property="og:description" content="Сторінки за цією адресою немає. Повертайтесь на головну SILENT.">',
  '<meta property="og:description" content="There is no page at this address. Head back to the SILENT homepage.">'),
]

SWITCH_UA_404 = """    <span class="lang-switch" role="group" aria-label="Мова сайту">
      <span class="lang-cur" aria-current="true">UA</span>
      <a href="/en/" hreflang="en" lang="en">EN</a>
    </span>"""
SWITCH_EN_404 = """    <span class="lang-switch" role="group" aria-label="Site language">
      <a href="/" hreflang="uk" lang="uk">UA</a>
      <span class="lang-cur" aria-current="true">EN</span>
    </span>"""

# ------------------------------------------------------------------- шляхи
# Сторінка лежить на рівень глибше за корінь, тож усі відносні адреси
# піднімаються на крок вище. Абсолютні (http, #, mailto:) не чіпаємо.
PATHS = [
 ('href="assets/site.css"', 'href="../assets/site.css"'),
 ('src="assets/site.js"',   'src="../assets/site.js"'),
 ('href="images/',  'href="../images/'),
 ('src="images/',   'src="../images/'),
 ('data-poster="images/', 'data-poster="../images/'),
 ('data-video="video/',   'data-video="../video/'),
 ("url('images/",  "url('../images/"),
]

# --------------------------------------------------------------- перемикач
SWITCH_UA = """    <span class="lang-switch" role="group" aria-label="Мова сайту">
      <span class="lang-cur" aria-current="true">UA</span>
      <a href="en/" hreflang="en" lang="en">EN</a>
    </span>"""
SWITCH_EN = """    <span class="lang-switch" role="group" aria-label="Site language">
      <a href="../" hreflang="uk" lang="uk">UA</a>
      <span class="lang-cur" aria-current="true">EN</span>
    </span>"""

# ------------------------------------------------------------------- рядки
# Ключ — точний рядок з index.html, значення — переклад. Порядок тут довільний:
# застосовуються від найдовших до найкоротших, щоб короткий рядок не з'їв
# частину довшого.
T = {
# --- меню й підвал -------------------------------------------------------
'Перейти до вмісту': 'Skip to content',

# --- сторінка 404 --------------------------------------------------------
'Помилка 404': 'Error 404',
'Тут тиша — і цього разу не тому, що ми так задумали.':
  "It's quiet here — and this time we didn't plan it that way.",
'Сторінки за цією адресою немає. Схоже, посилання застаріло або в адресі загубився символ. Решта сайту на місці.':
  'There is no page at this address. The link has probably gone stale, or a character got lost on the way. The rest of the site is where you left it.',
'На головну': 'Go to the homepage',
'Розділи сайту': 'Site sections',

'На початок сторінки': 'Back to top',
'Нагору сторінки': 'Back to top',
'Як це працює': 'How it works',
'Що входить': "What's included",
'Сценарії': 'Scenarios',
'Ціна': 'Pricing',
'Перевірити дату': 'Check a date',
'Перевірити доступність дати': 'Check if your date is free',

# --- hero ----------------------------------------------------------------
'Silent Disco під ключ': 'Full-service silent disco',
'Сайлент Диско в навушниках': 'Silent disco in headphones',
'Сайлент Диско': 'Silent disco',
'Тиха вечірка під ключ': 'Full-service quiet party',
'9 800 грн': '9,800 UAH',
'40 гостей': '40 guests',
'Київ та Україна': 'Kyiv and across Ukraine',
'від <b>': 'from <b>',
'Три хвилі музики': 'Three waves of music',
'грають одночасно —': 'playing all at once —',
'ви обираєте <span class="accent-lime">свою</span>.': 'you pick <span class="accent-lime">yours</span>.',
'Три канали звучать паралельно в'+NB+'навушниках кожного гостя. Хтось танцює під хаус, хтось під поп'+NB+'— і'+NB+'всі поруч, в'+NB+'одному залі.':
  "Three channels play at the same time in every guest's headphones. Some dance to house, some to pop — and all of them side by side, in the same room.",

'Оберіть канал': 'Pick a channel',
'Увімкнути звук': 'Turn sound on',
'Deep &amp; Dance — електроніка, хаус, ритм': 'Deep &amp; Dance — electronic, house, rhythm',
'Pop &amp; Throwback — хіти, під які всі знають слова': 'Pop &amp; Throwback — the hits everyone knows the words to',
'Chill &amp; Soul — повільне, тепле, близьке': 'Chill &amp; Soul — slow, warm, close',

# --- чому silent disco ---------------------------------------------------
'Чому silent disco': 'Why silent disco',
'Звичайна вечірка змушує обирати за всіх. Ця — дає обрати кожному.':
  'An ordinary party makes you choose for everyone. This one lets everyone choose.',
'Чорно-білий кадр: сцена з колонками і темна зала глядачів':
  'Black-and-white shot: a stage with speakers and a dark room of guests',
'Як зазвичай': 'The usual way',
'Колонки на всю залу': 'Speakers blasting the whole room',
'Один плейлист на всіх. Хтось нудьгує, комусь голосно. О 23:00 — сусіди, охорона, «зробіть тихіше». Фото виходять темні й однакові.':
  "One playlist for everybody. Some are bored, others find it too loud. At 11pm it's the neighbours, security, “turn it down”. The photos come out dark and all alike.",
'Компанія друзів сміється у світних зелених навушниках':
  'A group of friends laughing in glowing green headphones',
'Із silent disco': 'With silent disco',
'Вечір, який кожен збирає собі': 'A night everyone puts together for themselves',
'Сайлент Диско — формат, де кожен чує своє, але всі разом: три канали під різний настрій, гучність під себе, світло LED у кожному кадрі.':
  'Silent disco is a format where everyone hears their own thing and still stays together: three channels for different moods, volume set by each guest, LED light in every shot.',

# --- як це працює --------------------------------------------------------
'Як насправді влаштована тиха вечірка?': 'How does a quiet party actually work?',
'Музика йде не з колонок, а одразу в навушники кожного гостя. Один передавач роздає три канали, і людина сама обирає, який слухати і на якій гучності. Колонок немає, тож ззовні залишається тиша. Ми привозимо навушники із запасними комплектами, збираємо систему на місці й лишаємось на вечір. Від вас потрібні тільки дата й приблизна кількість гостей. Працюємо в Києві й виїжджаємо по всій Україні.':
  "The music doesn't come from speakers — it goes straight into every guest's headphones. One transmitter carries three channels, and each person chooses which one to listen to and how loud. There are no speakers, so outside it stays quiet. We bring the headphones with spare sets, assemble the system on site and stay for the evening. All we need from you is a date and a rough number of guests. We work in Kyiv and travel anywhere in Ukraine.",
'Заявка': 'Request',
'Дата, місце, гості': 'Date, venue, guests',
'Форма займає хвилину': 'The form takes a minute',
'Дзвонити не обов’язково': 'No phone call needed',
'Розрахунок': 'Quote',
'Рахуємо вартість': 'We work out the cost',
'Відповідаємо протягом дня': 'We reply the same day',
'Ціна залежить від дати й тривалості': 'The price depends on the date and the hours',
'Монтаж': 'Setup',
'Ми приїжджаємо': 'We arrive',
'Близько 30 хвилин до старту': 'About 30 minutes before the start',
'Показуємо, як перемикати канали': 'We show you how to switch channels',
'Вечірка': 'The party',
'Ви танцюєте': 'You dance',
'Гості перемикають канали самі': 'Guests switch channels themselves',
'Демонтаж і вивіз на нас': 'Teardown and pickup are on us',

# --- досвід гостя --------------------------------------------------------
'Досвід гостя': 'The guest experience',
'Що відчують ваші гості на танцполі.': 'What your guests will feel on the dancefloor.',
'Три канали одночасно': 'Three channels at once',
'RED, GREEN, BLUE звучать паралельно. У кожного гостя — свій ефір, і всі танцюють в одному залі.':
  'RED, GREEN and BLUE play in parallel. Every guest gets their own broadcast, and everyone dances in the same room.',
'Кожен обирає свій настрій': 'Everyone picks their own mood',
'Драйв, хіти чи повільне — гість перемикає канал одним дотиком і залишається там, де йому добре.':
  'High energy, big hits or something slow — a guest switches channel with one tap and stays where it feels good.',
'Особиста гучність': 'Personal volume',
'Кожен виставляє звук під себе. Ніхто не виходить із дзвоном у вухах — комфортно й дітям, і старшим.':
  'Everyone sets the level for themselves. Nobody leaves with ringing ears — it suits children and older guests alike.',
'Можна нормально спілкуватися': 'You can actually talk',
'Навушники на шию — і розмова йде звичайним голосом. Без «що?» і «повтори!» крізь гуркіт колонок.':
  'Headphones down to the neck and the conversation runs at a normal voice. No “what?” or “say that again!” over booming speakers.',
'LED-візуал у кожному кадрі': 'LED visuals in every shot',
'Підсвітка на кожному гості перетворює зал на готову картинку. Фото й відео виходять яскравими без окремого світлового обладнання.':
  'The glow on every guest turns the room into a ready-made picture. Photos and video come out bright with no separate lighting rig.',
'Формат, якого ще не бачили': "A format they haven't seen before",
'Танці «в тиші» — незвичне відчуття вже з перших хвилин. Гості проводять час не так, як на звичайній вечірці.':
  "Dancing “in silence” feels unfamiliar from the first minutes. Guests spend the evening in a way they simply don't at an ordinary party.",

# --- що входить ----------------------------------------------------------
'Що саме ви отримуєте за свої гроші.': 'Exactly what you get for your money.',
'Silent disco під ключ — комплект обладнання, логістика й супровід у межах однієї послуги.':
  'Full-service silent disco — the equipment, the logistics and the on-site support all within one service.',
'Обладнання': 'Equipment',
'Від 40 бездротових LED-навушників, 3 канали, передавачі та запасні навушники в комплекті.':
  'From 40 wireless LED headphones, 3 channels, transmitters and spare headsets included.',
'Доставка й монтаж': 'Delivery and setup',
'Привозимо, збираємо систему, налаштовуємо канали й тестуємо сигнал до старту.':
  'We deliver, assemble the system, set up the channels and test the signal before the start.',
'Підготовлені плейлисти': 'Playlists prepared in advance',
"Три канали, зібрані під ваш настрій і формат події — діджей не обов'язковий.":
  'Three channels put together for your mood and the type of event — a DJ is optional.',
'Супровід і демонтаж': 'On-site support and teardown',
'Ведемо технічну частину протягом вечора, а після завершення забираємо все обладнання.':
  'We run the technical side through the evening and take all the equipment away afterwards.',
'Короткий reels': 'A short reel',
'Ролик вашого вечора, готовий до сторіз і публікації.':
  'A clip of your evening, ready for stories and posts.',
'у базовій ціні': 'in the base price',
'за бажанням': 'optional',
'Колонки, підсилювачі та окремий звук орендувати додатково не потрібно — комплект замінює всю звукову частину вечора.':
  "There's no need to rent speakers, amplifiers or separate sound — the kit replaces the whole audio side of the evening.",

# --- галерея -------------------------------------------------------------
'Атмосфера події, гортайте вбік': 'Event atmosphere, scroll sideways',
'Атмосфера': 'Atmosphere',
'SILENT звучить однаково в залі й на даху, в музеї й під небом.':
  'SILENT sounds the same in a hall or on a rooftop, in a museum or under open sky.',
'Гортайте вбік, щоб побачити більше кадрів': 'Scroll sideways for more shots',
'Попередні кадри': 'Previous shots',
'Наступні кадри': 'Next shots',
'Дивитися відео: ': 'Watch video: ',
'Навушники для гостей на вході': 'Headphones waiting for guests at the entrance',
'Гості танцюють у червоному світлі': 'Guests dancing in red light',
'Дискокуля над залою': 'A mirror ball above the room',
'Ряди навушників перед подією': 'Rows of headphones before the event',
'Танці серед колон': 'Dancing between the columns',
'Юрба перед сценою': 'A crowd in front of the stage',
'Вечірка за склом, тиша назовні': 'A party behind glass, silence outside',
'Пара в обіймах серед гостей': 'A couple holding each other among the guests',
'Біля бару, кожен у своїх навушниках': 'At the bar, everyone in their own headphones',
'Подруги перепочивають на дивані': 'Friends taking a break on the sofa',
'Танцпол просто неба': 'An open-air dancefloor',
'Щільний танцпол у фіолетовому світлі': 'A packed dancefloor in purple light',
'Розмова в синьому світлі': 'A conversation in blue light',
'Навушник на столі': 'A headset on the table',
'Ранкове тренування на вулиці': 'A morning workout outdoors',
'Святковий стіл у рожевому світлі': 'A celebration table in pink light',
'Кінопоказ просто неба': 'An open-air film screening',
'Повний двір у навушниках': 'A full courtyard in headphones',
'Дівчина танцює серед вогнів': 'A woman dancing among the lights',
'Вечірка на даху над містом': 'A rooftop party above the city',
'Сет на заході сонця': 'A set at sunset',
'Навушник зблизька': 'A headset up close',
'Танці у дворі надвечір': 'Dancing in the courtyard at dusk',
'Гостя озирається на танцполі': 'A guest glancing back on the dancefloor',
'Синє світло над танцполом': 'Blue light over the dancefloor',
'Гості співають разом у синьому світлі': 'Guests singing together in blue light',
'Гостя з коктейлем серед танцполу': 'A guest with a cocktail in the middle of the dancefloor',
'Перший танець молодят': "The newlyweds' first dance",
'Дах із панорамою нічного міста': 'A rooftop with the night city below',
'Захід сонця над пляжним танцполом': 'Sunset over a beach dancefloor',
'Йога-сет на світанку біля моря': 'A sunrise yoga set by the sea',
'Лазери й екран у залі': 'Lasers and a screen in the hall',
'Руки вгору на танцполі': 'Hands in the air on the dancefloor',
'Сервірований стіл із навушниками': 'A laid table with headphones',
'Дві подруги сміються': 'Two friends laughing',
'Лазери над залою в навушниках': 'Lasers over a room in headphones',
'Компанія танцює разом': 'A group dancing together',
'Гості в залі музею': 'Guests in a museum hall',
'Гості співають разом': 'Guests singing together',
'Гостя вибирає свій канал': 'A guest choosing her channel',
'Повний двір гостей': 'A courtyard full of guests',

# --- silent-досвіди ------------------------------------------------------
'Silent-досвіди': 'Silent experiences',
'Silent disco — це лише один зі сценаріїв. Тихий звук працює всюди, де важливо чути.':
  'Silent disco is only one of the scenarios. Quiet sound works anywhere it matters to hear.',
'Одна технологія — десятки форматів. Від приватних свят і весілля до екскурсії музеєм: гортайте нижче й дивіться, що вже можна зробити.':
  'One technology, dozens of formats. From private celebrations and weddings to a museum tour: scroll on and see what is already possible.',
'Сценарії подій, гортайте вбік': 'Event scenarios, scroll sideways',
'Замовити цей досвід': 'Book this experience',
'Гортайте вбік, щоб побачити всі формати': 'Scroll sideways to see every format',
'Попередні сценарії': 'Previous scenarios',
'Наступні сценарії': 'Next scenarios',
'<option>Весілля</option>': '<option>Wedding</option>',
'Весілля': 'Weddings',
'Гості самі обирають: танцювати чи говорити. Жодного гуркоту на всю залу — і жодних дзвінків від готелю о другій ночі.':
  'Guests choose for themselves: dance or talk. Nothing booming across the room, and no call from the hotel at two in the morning.',
'Кіно просто неба': 'Open-air cinema',
'Двір, дах, парк — звук у навушниках, тиша навколо. Фільм до ночі без питань від сусідів.':
  'A courtyard, a rooftop, a park — sound in the headphones, quiet all around. A film that runs late with no questions from the neighbours.',
'Студентські події': 'Student events',
'Посвята, випускний, вечірка гуртожитку — гучно для своїх і тихо для адміністрації.':
  'Initiations, graduations, a dorm party — loud for your own people and quiet for the administration.',
'Презентація релізу': 'Release listening party',
'Послухайте новий альбом у деталях — разом і водночас особисто. Камерний формат для перших слухачів.':
  'Hear a new album in detail — together and privately at the same time. An intimate format for its first listeners.',
'Драйв-ін формат': 'Drive-in format',
'Майданчик, екран і звук у навушниках — подія там, де немає жодної звукової інфраструктури.':
  'An empty lot, a screen and sound in the headphones — an event where there is no audio infrastructure at all.',
'Музичні коледжі': 'Music colleges',
'Камерне прослуховування студентських програм: чути кожну партію без гучних моніторів у залі.':
  'Intimate listening sessions for student programmes: every part audible without loud monitors in the hall.',
'Фестивалі': 'Festivals',
'Додаткова сцена, яка не конфліктує з головною і не впирається в комендантську годину.':
  "An extra stage that doesn't clash with the main one and doesn't run into curfew.",
'Музеї та галереї': 'Museums and galleries',
'Аудіосупровід, синхронізований із простором. Відвідувач занурюється, не порушуючи тиші зали.':
  'An audio track synced to the space. Visitors get drawn in without breaking the quiet of the room.',
'Благодійні гала': 'Charity galas',
'Аукціон і танці в одному залі. Гості чують ведучого, не борючись із фоновою музикою.':
  'An auction and dancing in the same room. Guests hear the host without fighting the background music.',
'Шкільні свята': 'School events',
'Події та збори коштів, які діти чекають. Без перевантаження звуком у спортзалі.':
  'Events and fundraisers children look forward to. Without overloading the gym with sound.',
'Церковні та молодіжні табори': 'Church and youth camps',
'Ранкові зібрання, тихі години роздумів і вечірні дискотеки — на одному комплекті обладнання.':
  'Morning gatherings, quiet hours for reflection and evening discos — on one set of equipment.',
'Той самий формат у чистому вигляді: три канали, навушники й танцпол, який не заважає нікому навколо.':
  'The format in its purest form: three channels, headphones and a dancefloor that bothers nobody around it.',
'Дні народження': 'Birthdays',
'Від дитячого свята до дорослої вечірки: гучність під вік і настрій кожної компанії.':
  "From a children's party to a grown-up one: volume to match the age and mood of each group.",
'Конференції': 'Conferences',
'Кілька сцен в одному залі й тихі обговорення в групах. Кожен чує свого спікера, не заважаючи сусідній секції.':
  'Several stages in one hall and quiet breakout discussions. Everyone hears their own speaker without disturbing the section next door.',
'Екскурсії': 'Guided tours',
'Гід говорить упівголоса, а чути однаково добре і в першому ряду, і в останньому. Без крику й мегафона.':
  'The guide speaks softly and is heard just as well at the front as at the back. No shouting, no megaphone.',
'Табори та молодіжні збори': 'Camps and youth gatherings',
'Ранкові розминки, командні ігри, вечірня дискотека — один комплект на всі активності зміни.':
  'Morning warm-ups, team games, an evening disco — one kit for every activity of the session.',
'Діджей-сет наживо': 'Live DJ set',
'Резидент або запрошений діджей мікшує просто у ваші навушники — з реакцією на зал.':
  'A resident or guest DJ mixes straight into your headphones, reading the room as they go.',
'Церковні служби та зібрання': 'Church services and gatherings',
'Проповідь і музика звучать чітко для кожного — у залі, у дворі чи на виїзному служінні.':
  'The sermon and the music come through clearly for everyone — in the hall, in the yard or at an outdoor service.',
'Корпоративи': 'Corporate events',
'Формат для тімбілдингу чи корпоративу, у якому команда нарешті розкривається. Працює і в офісі, і в лофті — без узгодження гучності з орендодавцем.':
  'A format for team building or a company party where the team finally opens up. Works in an office or a loft, with no volume to negotiate with the landlord.',
'Йога та ecstatic dance': 'Yoga and ecstatic dance',
'Голос інструктора просто у вусі, музика — на власній гучності. Ніщо не збиває з практики.':
  "The instructor's voice right in your ear, the music at your own volume. Nothing pulls you out of the practice.",
'Камерні концерти': 'Intimate concerts',
'Прослуховування, де чути кожен нюанс виконання. Публіка максимально близько до звуку.':
  'Sessions where every nuance of the performance comes through. The audience as close to the sound as it gets.',
'Інклюзивні події': 'Inclusive events',
'Кожен регулює гучність під себе — подія стає доступною для гостей із сенсорною чутливістю.':
  'Everyone sets their own volume, which makes the event accessible to guests with sensory sensitivities.',
'Громадські зібрання': 'Community gatherings',
'Лекції, покази, зустрічі спільноти — чути кожне слово навіть на відкритому майданчику.':
  'Talks, screenings, community meetings — every word audible even in an open space.',
'Ярмарки та маркети': 'Fairs and markets',
'Музична зона просто серед рядів — гості танцюють, а торгівля поруч іде своїм ходом.':
  'A music zone right among the stalls — guests dance while trading carries on beside them.',
'Іммерсивні театри': 'Immersive theatre',
'Голос акторів і саундтрек звучать просто у вусі глядача. Сцену можна розгорнути навіть просто неба.':
  "The actors' voices and the soundtrack play right in the audience's ear. The stage can be set up even in the open air.",
'Спортивні події': 'Sports events',
'Забіги, тренування, розминки: команда чує тренера, а не вітер і вуличний шум.':
  'Runs, training, warm-ups: the team hears the coach, not the wind and the street noise.',

# --- калькулятор ---------------------------------------------------------
'Калькулятор': 'Calculator',
'Порахуйте бюджет вечора до заявки.': 'Work out the budget for the evening before you enquire.',
'Мінімальне замовлення — 40 навушників на 4 години. Посуньте повзунок і додайте опції, щоб побачити орієнтовний бюджет для вашої події.':
  'The minimum order is 40 headphones for 4 hours. Move the slider and add options to see a rough budget for your event.',
'Навушники SILENT із логотипом і підсвіткою трьох каналів — зеленого, синього та червоного':
  'SILENT headphones with the logo and the three channel colours lit — green, blue and red',
'мінімум навушників': 'headphones minimum',
'базова тривалість': 'base duration',
'музичні канали': 'music channels',
'налаштування на місці': 'setup on site',
'Навушники': 'Headphones',
'Орієнтир': 'Estimate',
'Кількість навушників': 'Number of headphones',
'Тривалість': 'Duration',
'Менше годин': 'Fewer hours',
'Більше годин': 'More hours',
'виїзд по'+NB+'Україні': 'travel across Ukraine',
'короткий reels': 'a short reel',
'дим і'+NB+'світло': 'smoke and lights',
'База 40 навушників / 4 години': 'Base: 40 headphones / 4 hours',
'Додаткові навушники': 'Extra headphones',
'Додаткові години': 'Extra hours',
'Опції': 'Options',
'Ціна за гостя': 'Price per guest',
'Це орієнтир. Фінальна ціна залежить від дати, локації, тривалості та формату — і не є публічною офертою.':
  "This is an estimate. The final price depends on the date, the venue, the hours and the format, and it isn't a public offer.",

# --- гарантія ------------------------------------------------------------
'Наша гарантія': 'Our guarantee',
'Якщо в перші пів години гості не танцюють — знімаємо частину суми.':
  'If nobody is dancing in the first half hour, we take part of the fee off the bill.',
'Ми відповідаємо за результат вечора, тож фінансовий ризик беремо на себе.':
  "We're accountable for how the evening turns out, so we carry the financial risk.",

# --- відгуки -------------------------------------------------------------
'Відгуки': 'Reviews',
'Що кажуть ті, хто це відчув.': "What people who've felt it say.",
'Короткі враження гостей і організаторів після київських подій.':
  'Short impressions from guests and organisers after events in Kyiv.',
'Боялася, що гості просто постоять із навушниками в руках і підуть. За півгодини танцювали всі, включно з моєю мамою. О другій ночі вимикали самі, бо ніхто не збирався додому.':
  'I was afraid the guests would just stand around holding the headphones and leave. Half an hour in, everyone was dancing, my mum included. At two in the morning we were the ones switching it off, because nobody was going home.',
'Олена К.': 'Olena K.',
'весілля · Київ, вересень': 'wedding · Kyiv, September',
'Лофт із житловими апартаментами через стіну. Скарг нуль, а це для нас було головне питання. Приїхали за дві години до старту й підключили все без нашої участі.':
  'A loft with flats on the other side of the wall. Zero complaints, and that was the main question for us. They arrived two hours before the start and set everything up without us.',
'Дмитро П.': 'Dmytro P.',
'корпоратив на 120 гостей': 'company party for 120 guests',
'Три канали врятували вечір. Друзі слухають зовсім різне, і замість компромісного плейлиста кожен просто крутнув перемикач на своєму.':
  'The three channels saved the evening. My friends listen to completely different things, and instead of a compromise playlist everyone just flicked the switch on their own headset.',
'Марина Ц.': 'Maryna Ts.',
'день народження, 35': 'birthday, 35',
'Найкраще навіть не музика. Ми з класним керівником спокійно розмовляли посеред танцполу, не зриваючи голос.':
  "The best part wasn't even the music. Our form teacher and I had a proper conversation in the middle of the dancefloor without wrecking our voices.",
'Артем В.': 'Artem V.',
'випускний на даху': 'rooftop graduation',
'Ранкова практика на 40 килимків просто неба. Голос інструктора чути навіть в останньому ряду. З колонками половина групи щоразу випадала.':
  "A morning practice on 40 mats in the open air. The instructor's voice carried even to the back row. With speakers, half the group used to drop out every time.",
'Софія Р.': 'Sofiia R.',
'йога-сет у парку': 'yoga set in the park',
'Показували фільм у внутрішньому дворі до одинадцятої вечора. Без навушників нас зупинили б на двадцятій хвилині.':
  "We screened a film in the inner courtyard until eleven at night. Without headphones we'd have been stopped twenty minutes in.",
'Ігор М.': 'Ihor M.',
'кінопоказ у дворі': 'film screening in the courtyard',
'Боялася, що дівич-вечір на сорок людей — це вже занадто гучно для затишної компанії. З навушниками вийшло навпаки: кожна чула тільки свою музику, а разом все одно танцювали як одна команда.':
  'I worried that a hen party for forty would be far too loud for a close group. With the headphones it came out the other way round: each of us heard only her own music, and we still danced together like one crew.',
'Катерина Л.': 'Kateryna L.',
'дівич-вечір, 40 гостей': 'hen party, 40 guests',
'Брали як активність на виїзд. Ефект неочікуваний: люди, які на корпоративах зазвичай сидять у кутку, того вечора танцювали.':
  'We booked it as an off-site activity. The effect was unexpected: the people who normally sit in the corner at company parties were dancing that night.',
'Богдан Ш.': 'Bohdan Sh.',
'тимбілдинг для команди': 'team building day',
'Попередні відгуки': 'Previous reviews',
'Наступні відгуки': 'Next reviews',
'Гортайте вбік, щоб побачити більше відгуків': 'Scroll sideways for more reviews',

# --- FAQ -----------------------------------------------------------------
'Питання наперед': 'Questions up front',
'Те, що зазвичай питають перед замовленням.': 'What people usually ask before booking.',
'Скільки місця потрібно на танцполі?': 'How much dancefloor space do we need?',
'Орієнтовно <strong>1 м² на людину</strong> для активних танців, менше — якщо частина гостей сидітиме. Скажіть нам розмір залу й кількість гостей — порахуємо, чи вистачить простору, і порадимо оптимальну кількість навушників.':
  "Roughly <strong>1 m² per person</strong> for active dancing, less if some of the guests will be seated. Tell us the size of the room and the number of guests and we'll work out whether there's enough space, then suggest how many headsets to take.",
'Чи можна на вулиці?': 'Can it be outdoors?',
'Так, але обладнання залежить від живлення і не любить вологу. У дощ або без розетки поруч потрібен запасний план — намет, навіс або перенесення в приміщення. Обговорюємо це заздалегідь, коли дізнаємось локацію.':
  "Yes, but the equipment needs power and doesn't like damp. In rain, or with no socket nearby, you need a backup plan — a tent, a canopy or moving indoors. We work that out in advance, once we know the venue.",
'Це справді тихо ззовні?': 'Is it really quiet from the outside?',
'Гості танцюють, співають і сміються — це не безшумно. Але сумарний шум навіть від сотні людей у навушниках — мала частка того, що дають звичайні колонки. І коли хтось хоче поговорити, він просто знімає навушники на шию і спілкується звичайним голосом.':
  "Guests dance, sing and laugh, so it isn't soundless. But the total noise from even a hundred people in headphones is a small fraction of what ordinary speakers make. And when someone wants to talk, they simply slide the headphones down to their neck and speak at a normal voice.",
'Наскільки довго тримає заряд?': 'How long does the battery last?',
'Навушники працюють <strong>10+ годин</strong> без підзарядки — вистачає на будь-який вечір з запасом. Приїжджаємо із зарядженим комплектом, тож про це можна не думати.':
  "The headphones run <strong>10+ hours</strong> on one charge — enough for any evening with room to spare. We arrive with the kit fully charged, so it isn't something you need to think about.",
'Чи потрібен окремо DJ?': 'Do we need a DJ as well?',
"Не обов'язково. Наймати живого DJ — це окрема стаття витрат, зазвичай суттєва сума за вечір. Ми наперед готуємо три плейлисти під ваш настрій, тож DJ потрібен, лише якщо хочете живий мікс саме на місці.":
  'Not necessarily. Hiring a live DJ is a separate line in the budget, usually a sizeable one for the evening. We prepare three playlists in advance to match your mood, so a DJ is only needed if you want a live mix on the night.',
'Чи підходить для дітей?': 'Is it suitable for children?',
'Так. У кожного гостя — особиста гучність, тож дитячий слух легко вберегти від зайвого звуку. Для подій із малими дітьми радимо одразу обмежити гучність на нижчому рівні — про це подбаємо ще до початку.':
  "Yes. Every guest has their own volume, so it's easy to keep children's hearing away from too much sound. For events with small children we suggest capping the volume lower from the outset — we take care of that before it starts.",
'Як повертаються навушники наприкінці?': 'How do the headphones come back at the end?',
'Ставимо один пункт видачі й повернення на вході, щоб нічого не губилося. При потребі використовуємо просту систему обліку, щоб наприкінці вечора точно знати, що все зібрано — без незручних питань до гостей.':
  'We set up a single hand-out and return point at the entrance so nothing goes astray. If needed we use a simple tracking system, so by the end of the evening we know for certain everything is back — without awkward questions to guests.',
'Що якщо навушники загубляться або пошкодяться?': 'What if headphones get lost or damaged?',
'Таке трапляється на живих вечірках, тому ми закладаємо невеликий заставний внесок за комплект, який повертається одразу після того, як усе обладнання здано в цілості. Якщо один-два навушники не повернули чи пошкодили — покриваємо це із застави, без додаткових розбирань із вами. Про суму й умови домовляємось заздалегідь, до самого івенту.':
  "It happens at live parties, so we take a small refundable deposit on the kit, returned as soon as all the equipment is handed back intact. If one or two headsets don't come back or are damaged, we cover it from the deposit, with nothing further to sort out on your side. We agree the amount and the terms in advance, before the event itself.",

# --- форма ---------------------------------------------------------------
'Перевірте дату <span class="em">своєї</span> події': 'Check the date of <span class="em">your</span> event',
"Залиште заявку — ми зв'яжемося, перевіримо, чи вільна дата, підберемо формат і підтвердимо бронь після узгодження.":
  "Send a request and we'll get in touch, check whether the date is free, work out the format and confirm the booking once it's agreed.",
'Один вечір — одна подія, тож дати розбирають наперед':
  'One evening, one event — dates get taken well in advance',
"Заявка ні до чого не зобов'язує — це перевірка доступності":
  "A request commits you to nothing — it's an availability check",
'Попередній місяць': 'Previous month',
'Наступний місяць': 'Next month',
'<span>Пн</span><span>Вт</span><span>Ср</span><span>Чт</span><span>Пт</span><span>Сб</span><span>Нд</span>':
  '<span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>',
'Оберіть дату — вона підставиться у форму': 'Pick a date and it will fill the form',
'Як вас звати': 'Your name',
"Ім'я": 'Name',
'Телефон або Instagram': 'Phone or Instagram',
'+380… або @нік': '+380… or @handle',
'Що ви плануєте?': 'What are you planning?',
'Хочу дізнатися ціну': 'I want to know the price',
'Планую подію': "I'm planning an event",
'Шукаю формат для клієнта': 'Looking for a format for a client',
'Хочу обговорити нестандартний сценарій': "I'd like to discuss something out of the ordinary",
'День народження': 'Birthday',
'Корпоратив': 'Company party',
'Випускний': 'Graduation',
'Тімбілдинг': 'Team building',
'Фестиваль': 'Festival',
'Скільки гостей орієнтовно': 'Roughly how many guests',
'Бажана дата': 'Preferred date',
"Як ви про нас дізналися? (необов'язково)": 'How did you hear about us? (optional)',
'Оберіть варіант': 'Choose one',
'Рекомендація': 'Recommendation',
'Інше': 'Other',
"Коментар (необов'язково)": 'Comment (optional)',
'Розкажіть більше про подію, побажання щодо локації, часу тощо':
  'Tell us more about the event, the venue you have in mind, the timing and anything else',
'Надіслати заявку': 'Send the request',
"Натискаючи, ви погоджуєтесь, що ми зв'яжемося з вами щодо події.":
  'By sending this you agree that we may contact you about the event.',
'Заявку прийнято ✦': 'Request received ✦',
"Дякуємо! Ми зв'яжемося найближчим часом, щоб узгодити деталі й підтвердити дату вашого вечора.":
  "Thank you. We'll be in touch shortly to agree the details and confirm the date of your evening.",

# --- числа, одиниці, ініціали --------------------------------------------
# Формат числа міняється разом із локаллю: uk-UA ставить нерозривний пробіл
# (9 800), en-US — кому (9,800). Скрипт друкує суми через Intl і зробить це
# сам; тут ті самі числа, але вписані в розмітку руками.
'9 800': '9,800',
'грн': 'UAH',
'<small>шт.</small>': '<small>units</small>',
'<small>год</small>': '<small>hrs</small>',
'<b>4 год</b>': '<b>4 hrs</b>',
'<b>~30 хв</b>': '<b>~30 min</b>',
'<div class="tst-avatar">ОК</div>': '<div class="tst-avatar">OK</div>',
'<div class="tst-avatar">ДП</div>': '<div class="tst-avatar">DP</div>',
'<div class="tst-avatar">МЦ</div>': '<div class="tst-avatar">MT</div>',
'<div class="tst-avatar">АВ</div>': '<div class="tst-avatar">AV</div>',
'<div class="tst-avatar">СР</div>': '<div class="tst-avatar">SR</div>',
'<div class="tst-avatar">ІМ</div>': '<div class="tst-avatar">IM</div>',
'<div class="tst-avatar">КЛ</div>': '<div class="tst-avatar">KL</div>',
'<div class="tst-avatar">БШ</div>': '<div class="tst-avatar">BS</div>',

# --- підвал --------------------------------------------------------------
'Тиша ззовні, драйв усередині. Silent disco під ключ у Києві та по Україні.':
  'Quiet outside, everything happening inside. Full-service silent disco in Kyiv and across Ukraine.',
'Залишити заявку': 'Send a request',
'Про формат': 'About the format',
'Перед замовленням': 'Before you book',
'Чого очікувати': 'What to expect',
'Пошта': 'Email',
'Пишіть у будь-який месенджер — відповідаємо швидко.':
  'Message us on any of these — we reply quickly.',
'Silent disco під ключ · Київ · 2026': 'Full-service silent disco · Kyiv · 2026',
'Ціни орієнтовні й не є публічною офертою': 'Prices are indicative and not a public offer',

# --- лайтбокс і вікно подяки ---------------------------------------------
'Відео з події': 'Video from the event',
'Пауза або відтворення': 'Pause or play',
'Закрити': 'Close',
'Попереднє відео': 'Previous video',
'Наступне відео': 'Next video',
"Залишайтесь на зв'язку — стежте за майбутніми подіями та кулісами SILENT:":
  'Stay in touch — follow upcoming events and what happens behind the scenes at SILENT:',
}

# ------------------------------------------------- англійський блок рядків
I18N_EN = """<!-- Рядки, які скрипт виводить сам. Усе інше — статичний текст у розмітці
     нижче. Оголошується ДО site.js: той читає window.SILENT_I18N при старті. -->
<script>
window.SILENT_I18N = {
  base: '../',
  locale: 'en-US',
  currency: 'UAH',
  hero: [
    {
      lines: ['Three waves of music', 'playing all at once —', 'you pick {yours}.'],
      mLines: [
        ['Three waves of', ''],
        ['music playing', ''],
        ['all at once —', ''],
        ['you pick', 'sr'],
        ['{yours}.', '']
      ],
      mSub: 'One night, three different dancefloors.',
      sub: "Three channels play at the same time in every guest's headphones. Some dance to house, some to pop — and all of them side by side, in the same room."
    },
    {
      lines: ['Rooftop, flat, {office} —', 'the venue is no', 'longer a limit.'],
      mLines: [
        ['Rooftop, flat,', ''],
        ['{office} — the venue', ''],
        ['is no longer', 'sr'],
        ['a limit.', '']
      ],
      mSub: 'The party goes wherever you say.',
      sub: 'The whole sound system fits into the headphones: no speakers, no acoustic requirements, no negotiating the volume. You choose where the party happens.'
    },
    {
      lines: ['Dance like', '{nobody}', 'can hear you.'],
      mLines: [
        ['Dance like', ''],
        ['{nobody}', 'sr'],
        ['can hear you.', '']
      ],
      mSub: 'Because nobody can — and the night runs as long as you want.',
      sub: 'Because nobody can. Outside it stays quiet, so the evening lasts exactly as long as you want it to, not as long as the clock allows.'
    }
  ],
  sound: { on: 'Sound on', off: 'Turn sound on', mute: 'Turn sound off' },
  calc: {
    outside: 'travel across Ukraine',
    reel: 'a short reel',
    smoke: 'smoke and lights',
    opts: (list) => `, options: ${list.join(', ')}`,
    summary: (qty, hours, opts, total) =>
      `From the calculator: ${qty} headphones, ${hours} hrs${opts}. Estimated budget: ${total} UAH.`,
    note: (qty, hours, total) =>
      `✓ Pulled in from the calculator: <b>${qty} headphones, ${hours} hrs, ~${total} UAH</b>. Check the comment below — you can add to it.`
  },
  uc: {
    order: 'Book this experience',
    line: (name) => `Interested in: ${name}.`,
    note: (name) => `✓ Chosen experience: <b>${name}</b>. It is already in the comment below — add any details you like.`
  },
  cal: { foot: 'Date in the form: ' },
  video: { clip: (n) => 'Clip ' + n, prev: 'Previous video', next: 'Next video' },
  form: { required: 'Please leave a name and a contact so we can get back to you.' }
};
</script>
<script src="../assets/site.js"></script>"""


# Зіставляємо не буквально: в українському тексті пробіли між прийменником і
# словом нерозривні, а апостроф трапляється і прямий, і типографський. Шукати
# кожен варіант окремо означало б тримати словник у двох-трьох копіях.
def flexible(key):
    out = []
    for ch in key:
        if ch == ' ':
            out.append('[ \u00a0]')
        elif ch in "'\u2019\u02bc":
            out.append("['\u2019\u02bc]")
        else:
            out.append(re.escape(ch))
    return re.compile(''.join(out))


def translate(s):
    # Від найдовших рядків до найкоротших, щоб короткий не з'їв частину довшого.
    for k in sorted(T, key=len, reverse=True):
        s = flexible(k).sub(lambda m, v=T[k]: v, s)
    return s


def assert_translated(s, name):
    # Жодної кирилиці поза HTML-коментарями. Коментарі — нотатки для
    # розробника, вони однакові в обох файлах і читачеві не видні.
    check = re.sub(r'<!--[\s\S]*?-->', '', s)
    left = sorted({l.strip() for l in check.split('\n') if re.search(r'[А-Яа-яІіЇїЄєҐґ]', l)})
    if left:
        print('НЕПЕРЕКЛАДЕНЕ у %s (%d рядків):' % (name, len(left)))
        for l in left:
            print('   ', l[:160])
        sys.exit(1)


def build():
    s = io.open(SRC, encoding='utf-8').read()

    for old, new in HEAD + PATHS:
        if s.count(old) < 1:
            sys.exit('немає в index.html: ' + old[:80])
        s = s.replace(old, new)

    if s.count(SWITCH_UA) != 1:
        sys.exit('перемикач мови в меню не знайдено')
    s = s.replace(SWITCH_UA, SWITCH_EN)

    # блок рядків цілком
    m = re.search(r'<!-- Рядки, які скрипт виводить сам\.[\s\S]*?<script src="\.\./assets/site\.js"></script>', s)
    if not m:
        sys.exit('блок SILENT_I18N не знайдено')
    s = s[:m.start()] + I18N_EN + s[m.end():]

    s = translate(s)

    # hreflang не чіпаємо: обидві сторінки мусять називати ту саму пару, тож
    # трійка посилань з index.html переїжджає сюди дослівно. Змінюється лише
    # canonical — він у кожної сторінки свій.

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    io.open(DST, 'w', encoding='utf-8').write(s)
    assert_translated(s, 'en/index.html')
    print('en/index.html зібрано:', len(s.split('\n')), 'рядків, неперекладеного немає')


def build_404():
    """en/404.html з 404.html — тим самим способом і тим самим словником.

    Окрема функція, а не ще один прохід у build(): у сторінки помилки своя
    голова (noindex, свій title) і свій перемикач мови — з неіснуючої адреси
    він веде на головну іншої мови, а не на її таку саму помилку.
    """
    s = io.open(SRC404, encoding='utf-8').read()

    for old, new in HEAD404:
        if s.count(old) < 1:
            sys.exit('немає в 404.html: ' + old[:80])
        s = s.replace(old, new)

    if s.count(SWITCH_UA_404) != 1:
        sys.exit('перемикач мови в 404.html не знайдено')
    s = s.replace(SWITCH_UA_404, SWITCH_EN_404)

    s = translate(s)

    os.makedirs(os.path.dirname(DST404), exist_ok=True)
    io.open(DST404, 'w', encoding='utf-8').write(s)
    assert_translated(s, 'en/404.html')
    print('en/404.html зібрано:', len(s.split('\n')), 'рядків, неперекладеного немає')


if __name__ == '__main__':
    build()
    build_404()
