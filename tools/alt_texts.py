# -*- coding: utf-8 -*-
"""Alt-тексти зображень сайту (аудит 08.10.2026). Правило: опис того, що на фото, + одне природне
слово-запит там, де воно справді підходить («Silent Disco», «тиха дискотека/вечірка», «навушники»,
«корпоратив», «домашня вечірка»). Без переліку ключових слів. Див. розділ «Alt-тексти» в CLAUDE.md.

Кожен запис: файл -> (українська, англійська). tools/apply_alts.py один раз підставляє українські
значення в розмітку, а ALT_T (українська -> англійська) підхоплює build_en.py для EN-версії."""

# Мозаїка «Атмосфера» на головній (images/gal/*)
GALLERY = {
 '01_wide': ('Дівчина танцює серед вогнів у навушниках Silent Disco на вечірці', 'A girl dances among the lights in Silent Disco headphones at a party'),
 '02_sq': ('Руки вгору на танцполі: вечірка в навушниках Silent Disco', 'Hands in the air on the dance floor: a party in Silent Disco headphones'),
 '03_wide': ('Компанія танцює разом у навушниках Silent Disco', 'A group dances together in Silent Disco headphones'),
 '04_wide': ('Дах із панорамою нічного міста: вечірка в навушниках Silent Disco', 'A rooftop with a night-city panorama: a party in Silent Disco headphones'),
 '05_wide': ('Ряди бездротових навушників Silent Disco, підготовлених перед вечіркою', 'Rows of wireless Silent Disco headphones prepared before the party'),
 '06_tall': ('Танці серед колон на тихій дискотеці: гості слухають музику в навушниках', 'Dancing among columns at a silent disco: guests listen to music in headphones'),
 '07_tall': ('Йога-сет на світанку біля моря в навушниках Silent Disco', 'A sunrise yoga set by the sea in Silent Disco headphones'),
 '08_tall': ('Кінопоказ просто неба зі звуком у навушниках Silent Disco', 'An open-air movie screening with sound in Silent Disco headphones'),
 '09_tall': ('Гості в залі музею в навушниках Silent Disco', 'Guests in a museum hall wearing Silent Disco headphones'),
 '10_sq': ('Навушник Silent Disco із підсвіткою каналу зблизька', 'A Silent Disco headphone with channel lighting up close'),
 '11_tall': ('Навушник Silent Disco із підсвіткою на столі', 'A Silent Disco headphone with lighting on a table'),
 '12_tall': ('Перший танець молодят у навушниках Silent Disco на весіллі', 'The newlyweds\' first dance in Silent Disco headphones at a wedding'),
 '13_sq': ('Повний двір гостей на тихій вечірці в навушниках Silent Disco', 'A courtyard full of guests at a quiet party in Silent Disco headphones'),
 '14_sq': ('Сервірований святковий стіл із навушниками Silent Disco', 'A set festive table with Silent Disco headphones'),
 '15_tall': ('Пара обіймається серед гостей у навушниках Silent Disco', 'A couple embraces among guests in Silent Disco headphones'),
 '16_tall': ('Дві подруги сміються в навушниках Silent Disco на вечірці', 'Two friends laugh in Silent Disco headphones at a party'),
 '17_tall': ('Діджей-сет на заході сонця для гостей у навушниках Silent Disco', 'A DJ set at sunset for guests in Silent Disco headphones'),
 '18_wide': ('Розмова в синьому світлі: гості у навушниках Silent Disco', 'A conversation in blue light: guests in Silent Disco headphones'),
 '19_wide': ('Вечірка на даху над містом у навушниках Silent Disco', 'A rooftop party above the city in Silent Disco headphones'),
 '20_tall': ('Навушники Silent Disco для гостей на вході на вечірку', 'Silent Disco headphones for guests at the party entrance'),
 '21_sq': ('Ранкове тренування на вулиці під музику в навушниках Silent Disco', 'A morning outdoor workout to music in Silent Disco headphones'),
 '22_sq': ('Гостя вибирає свій канал на навушниках Silent Disco', 'A guest picks her channel on Silent Disco headphones'),
 '23_sq': ('Натовп гостей співає в навушниках Silent Disco перед сценою', 'A crowd of guests sings along in Silent Disco headphones in front of the stage'),
 '24_sq': ('Вечірка за склом: тиха дискотека в навушниках, а ззовні тихо', 'A party behind glass: a silent disco in headphones while it stays quiet outside'),
 '25_sq': ('Танці у дворі надвечір: тиха вечірка в навушниках', 'Dancing in a courtyard at dusk: a quiet party in headphones'),
 '26_wide': ('Захід сонця над пляжним танцполом: тиха дискотека в навушниках', 'Sunset over a beach dance floor: a silent disco in headphones'),
 '27_sq': ('Святковий стіл у рожевому світлі на вечірці в навушниках', 'A festive table in pink light at a party in headphones'),
 '28_wide': ('Лазери над залою, гості танцюють у навушниках Silent Disco', 'Lasers over the hall as guests dance in Silent Disco headphones'),
 '29_wide': ('Дискокуля над залою, де гості танцюють у навушниках Silent Disco', 'A disco ball over a hall where guests dance in Silent Disco headphones'),
 '30_wide': ('Щільний танцпол у фіолетовому світлі, гості в навушниках Silent Disco', 'A packed dance floor in purple light, guests in Silent Disco headphones'),
 '31_tall': ('Гостя озирається на танцполі в навушниках Silent Disco', 'A guest looks around the dance floor in Silent Disco headphones'),
 '32_sq': ('Гості співають разом у синьому світлі в навушниках Silent Disco', 'Guests sing together in blue light in Silent Disco headphones'),
 '33_sq': ('Гостя з коктейлем на танцполі в навушниках Silent Disco', 'A guest with a cocktail on the dance floor in Silent Disco headphones'),
 '34_sq': ('Біля бару, кожен у своїх навушниках: вечірка в навушниках без колонок', 'At the bar, everyone in their own headphones: a party in headphones with no speakers'),
 '35_sq': ('Подруги відпочивають на дивані в навушниках після танців на тихій вечірці', 'Friends rest on a sofa in headphones after dancing at a quiet party'),
 '36_wide': None,
 '101_tall': ('Гості танцюють у червоному світлі в навушниках на тихій дискотеці', 'Guests dance in red light in headphones at a silent disco'),
 '102_tall': ('Танцпол просто неба: тиха дискотека в навушниках Silent Disco', 'An open-air dance floor: a silent disco in Silent Disco headphones'),
 '103_tall': ('Повний двір гостей у навушниках на тихій вечірці під відкритим небом', 'A courtyard full of guests in headphones at a quiet open-air party'),
 '104_tall': ('Синє світло над танцполом: тиха дискотека для гостей у навушниках', 'Blue light over the dance floor: a silent disco for guests in headphones'),
 '105_tall': ('Лазери й екран у залі, гості в навушниках Silent Disco', 'Lasers and a screen in the hall, guests in Silent Disco headphones'),
 '106_tall': ('Гості співають разом на тихій дискотеці в навушниках', 'Guests sing together at a silent disco in headphones'),
}
GALLERY = {k: v for k, v in GALLERY.items() if v}

# Картки форматів (images/uc/*): головна, каталог і сторінки досвідів (їх синхронізує build_en.py з index.html)
CARDS = {
 'birthday': ('День народження в навушниках Silent Disco: тиха вечірка з друзями', 'A birthday in Silent Disco headphones: a quiet party with friends'),
 'school': ('Шкільне свято з тихою дискотекою в навушниках Silent Disco', 'A school party with a silent disco in Silent Disco headphones'),
 'corporate': ('Корпоратив у навушниках Silent Disco: цікавий формат для команди', 'A corporate event in Silent Disco headphones: an interesting format for a team'),
 'kids': ('Дитяче свято в навушниках: тиха дискотека для дітей', 'A children\'s party in headphones: a silent disco for kids'),
 'church': ('Церковна подія з музикою в навушниках Silent Disco', 'A church event with music in Silent Disco headphones'),
 'camp': ('Табір і молодіжні збори: тиха дискотека в навушниках', 'A camp and youth gathering: a silent disco in headphones'),
 'yoga': ('Йога й ecstatic dance у навушниках Silent Disco', 'Yoga and ecstatic dance in Silent Disco headphones'),
 'houseparty': ('Домашня вечірка в навушниках: тиха вечірка без скарг сусідів', 'A house party in headphones: a quiet party with no neighbour complaints'),
 'cinema': ('Кіно просто неба: звук у навушниках Silent Disco', 'Open-air cinema: sound in Silent Disco headphones'),
 'tour': ('Екскурсія зі звуком у навушниках Silent Disco', 'A guided tour with sound in Silent Disco headphones'),
 'markets': ('Ярмарок чи маркет із тихою музикою в навушниках Silent Disco', 'A fair or market with quiet music in Silent Disco headphones'),
 'training': ('Тренінг і навчання: звук у навушниках Silent Disco', 'Training and learning: sound in Silent Disco headphones'),
 'museum': ('Музей і галерея: тиха музична програма в навушниках Silent Disco', 'A museum and gallery: a quiet music programme in Silent Disco headphones'),
 'meditation': ('Медитація просто неба в навушниках Silent Disco', 'Open-air meditation in Silent Disco headphones'),
 'workshop': ('Майстерклас під музику в навушниках Silent Disco', 'A workshop with music in Silent Disco headphones'),
 'inclusive': ('Інклюзивна подія в навушниках Silent Disco з особистою гучністю', 'An inclusive event in Silent Disco headphones with personal volume'),
 'seniors': ('Подія для літніх людей у навушниках Silent Disco', 'An event for older guests in Silent Disco headphones'),
 'quest': ('Квест із підказками в навушниках Silent Disco', 'A quest with clues in Silent Disco headphones'),
 'dancebattle': ('Танцювальні змагання в навушниках Silent Disco', 'A dance battle in Silent Disco headphones'),
 'expo': ('Виставка й експо з музикою в навушниках Silent Disco', 'An exhibition and expo with music in Silent Disco headphones'),
 'fashion': ('Модний показ під музику в навушниках Silent Disco', 'A fashion show with music in Silent Disco headphones'),
 'musiccollege': ('Музичний коледж: заняття й виступи в навушниках Silent Disco', 'A music college: lessons and performances in Silent Disco headphones'),
 'silentdisco': ('Silent Disco: тиха дискотека в бездротових навушниках', 'Silent Disco: a silent disco in wireless headphones'),
 'wedding': ('Весілля в навушниках Silent Disco: танці для гостей усіх поколінь', 'A wedding in Silent Disco headphones: dancing for guests of every generation'),
 'students': ('Студентська вечірка в навушниках Silent Disco', 'A student party in Silent Disco headphones'),
 'festival': ('Фестиваль із тихою сценою в навушниках Silent Disco', 'A festival with a silent stage in Silent Disco headphones'),
 'churchcamp': ('Церковний і молодіжний табір із музикою в навушниках Silent Disco', 'A church and youth camp with music in Silent Disco headphones'),
 'conference': ('Конференція з тихим нетворкінгом у навушниках Silent Disco', 'A conference with quiet networking in Silent Disco headphones'),
 'community': ('Громадське зібрання з музикою в навушниках Silent Disco', 'A community gathering with music in Silent Disco headphones'),
 'hen': ('Дівич-вечір у навушниках Silent Disco', 'A hen party in Silent Disco headphones'),
 'gala': ('Благодійне гала з тихою дискотекою в навушниках Silent Disco', 'A charity gala with a silent disco in Silent Disco headphones'),
 'dj': ('Діджей-сет наживо для гостей у навушниках Silent Disco', 'A live DJ set for guests in Silent Disco headphones'),
 'sport': ('Спортивна подія з музикою в навушниках Silent Disco', 'A sports event with music in Silent Disco headphones'),
 'run': ('Забіг і прогулянка під музику в навушниках Silent Disco', 'A run and a walk to music in Silent Disco headphones'),
 'showcase': ('Камерний концерт у навушниках Silent Disco', 'An intimate concert in Silent Disco headphones'),
 'brand': ('Бренд-активація в навушниках Silent Disco', 'A brand activation in Silent Disco headphones'),
 'translation': ('Синхронний переклад у навушниках на заході', 'Simultaneous interpreting through headphones at an event'),
 'standup': ('Стендап і комедія з тихим форматом у навушниках Silent Disco', 'Stand-up and comedy in a quiet format with Silent Disco headphones'),
 'bartour': ('Бар-тур у навушниках Silent Disco', 'A bar tour in Silent Disco headphones'),
 'impostor': ('Гра «Імпостер» у навушниках Silent Disco', 'The Impostor game in Silent Disco headphones'),
 'hotel': ('Готель і ресорт: тиха вечірка в навушниках Silent Disco', 'A hotel and resort: a quiet party in Silent Disco headphones'),
 'listening': ('Презентація релізу: прослуховування в навушниках Silent Disco', 'A release presentation: a listening session in Silent Disco headphones'),
 'theatre': ('Іммерсивний театр у навушниках Silent Disco', 'Immersive theatre in Silent Disco headphones'),
 'drivein': ('Драйв-ін кіно: звук у навушниках Silent Disco', 'Drive-in cinema: sound in Silent Disco headphones'),
}

# Інші окремі зображення головної
HOME_SHIFT_NEW = ('Компанія друзів сміється у світних зелених навушниках Silent Disco: вечірка без колонок',
                  'A group of friends laughs in glowing green Silent Disco headphones: a party with no speakers')

# Колаж у геро сторінок досвідів (aria-hidden, перша поява кожного файла)
CORP_HERO = {
 'corp-1': ('Гості корпоративу танцюють на терасі в навушниках Silent Disco', 'Corporate guests dance on a terrace in Silent Disco headphones'),
 'para-na-yaskraviy-vechirtsi-silent-disco': ('Пара усміхається в навушниках Silent Disco на яскравому корпоративі', 'A couple smiles in Silent Disco headphones at a bright corporate party'),
 'corp-3': ('Дівчина танцює з піднятою рукою в навушниках Silent Disco на нічному заході', 'A girl dances with a raised hand in Silent Disco headphones at a night event'),
 'corp-4': ('Чоловік із навушниками Silent Disco на шиї на нічній терасі корпоративу', 'A man with Silent Disco headphones around his neck on a night terrace'),
 'corp-5': ('Нічна тераса з видом на місто: гості корпоративу в навушниках Silent Disco', 'A night terrace with a city view: corporate guests in Silent Disco headphones'),
 'yaskrave-selfi-na-vechirtsi-v-navushnykakh': ('Колеги усміхаються на корпоративі в навушниках Silent Disco', 'Colleagues smile at a corporate party in Silent Disco headphones'),
 'corp-7': ('Дівчина танцює на терасі під гірляндами в навушниках Silent Disco', 'A girl dances on a terrace under string lights in Silent Disco headphones'),
 'tantsi-pid-syayvom-silent-disco': ('Пара танцює на корпоративі в навушниках Silent Disco під кольоровим світлом', 'A couple dances at a corporate event in Silent Disco headphones under coloured light'),
}
WEDDING_HERO = {
 'couple-dancing-blue-red': ('Наречені танцюють у навушниках Silent Disco із синьою й червоною підсвіткою', 'Newlyweds dance in Silent Disco headphones with blue and red lights'),
 'woman-dancing-garden': ('Гостя весілля танцює в саду під гірляндами в навушниках Silent Disco', 'A wedding guest dances in a garden under string lights in Silent Disco headphones'),
 'headphone-candles-closeup': ('Навушник Silent Disco із зеленою підсвіткою серед свічок на весільному столі', 'A Silent Disco headphone with green lighting among candles on a wedding table'),
 'crowd-overhead-dance': ('Гості весілля на танцполі просто неба в навушниках Silent Disco, вид згори', 'Wedding guests on an open-air dance floor in Silent Disco headphones, seen from above'),
 'couple-embrace-crowd': ('Наречені обіймаються серед гостей у навушниках Silent Disco', 'Newlyweds embrace among guests in Silent Disco headphones'),
 'smiling-man-table': ('Усміхнений гість за весільним столом у навушниках Silent Disco з червоною підсвіткою', 'A smiling guest at a wedding table in Silent Disco headphones with red lighting'),
 'headphones-table-couple-bg': ('Навушники Silent Disco на сервірованому весільному столі, на тлі наречені', 'Silent Disco headphones on a set wedding table with the newlyweds in the background'),
 'champagne-couple-closeup': ('Пара з келихом шампанського на весіллі, поруч навушник Silent Disco із зеленою підсвіткою', 'A couple with a champagne glass at a wedding, a green-lit Silent Disco headphone nearby'),
}

# Картки статей у блозі (blog_src/posts.json): slug -> (alt)
BLOG = {
 'vechirka-bez-shumu-sysidy': 'Домашня вечірка в навушниках Silent Disco: гості танцюють, а сусіди не чують музики',
 'vesillya-voyennyi-stan': 'Весілля в навушниках Silent Disco: тиха дискотека для гостей під час воєнного стану',
 'zamist-konkursiv-korporativ': 'Корпоратив у навушниках Silent Disco: цікавий формат замість конкурсів',
 'rozvahy-vesillya-riznyi-vik': 'Гості різного віку на весіллі танцюють у навушниках Silent Disco',
 'skilky-koshtuye-tyha-dyskoteka': 'Навушники Silent Disco на танцполі: з чого складається ціна тихої дискотеки',
 'tri-kanaly-tysha-zzovni': 'Гості слухають свій канал у навушниках Silent Disco, а ззовні тихо',
}


def _all():
    pairs = {}
    for d in (GALLERY, CARDS, CORP_HERO, WEDDING_HERO):
        for ua, en in d.values():
            pairs[ua] = en
    pairs[HOME_SHIFT_NEW[0]] = HOME_SHIFT_NEW[1]
    return pairs


ALT_T = _all()
