"""Вирівнювання колонок у старих статтях блогу (17.11.2026, правило власника: кінці колонок у межах рядка-двох).
- nosplit знято там, де він заважав балансу (абзацу дозволено перейти в іншу колонку, як в інших статтях);
- три абзаци й одна група чекліста скорочені без втрати змісту;
- у CSS кроки .art-steps можуть переходити між колонками (site.css, «.art-flow .art-steps li»).
Зберігає форматування JSON файлів. Запуск: python3 tools/balance_columns_2026_11.py && python3 tools/build_en.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def edit(slug, fn):
    p = os.path.join(ROOT, 'blog_src', slug + '.json'); raw = open(p, encoding='utf-8').read()
    m = re.search(r'\n( +)"', raw); ind = len(m.group(1)) if m else 1
    j = json.loads(raw); fn(j)
    open(p, 'w', encoding='utf-8').write(json.dumps(j, ensure_ascii=False, indent=ind) + ('\n' if raw.endswith('\n') else ''))

def blk(j, prefix): return next(b for b in j['blocks'] if b.get('title', '').startswith(prefix))

def unsplit(*prefixes):
    def f(j):
        for pr in prefixes: blk(j, pr).pop('nosplit', None)
    return f

edit('yak-sklasty-pleylist-dlya-vechirky', unsplit('6. Чому'))
edit('ihry-dlya-vechirky-vdoma', unsplit('10 ігор', 'Що робити, якщо'))
edit('yak-organizuvaty-zvuk-na-zakhodi-prosto-neba', unsplit('3. Які є'))

def divych(j):
    c = blk(j, '7. Продумайте')['cols'][0]
    for x in c:
        if x.get('p', '').startswith('Збирайте побажання'):
            x['p'] = ('Збирайте побажання заздалегідь: нехай кожна подруга надішле одну пісню для танців і одну, пов’язану зі спільним спогадом. '
                      'Окремо запитайте наречену, що вона точно хоче чути, а чого б уникнула. Про послідовність треків читайте в статті '
                      '[[/blog/yak-sklasty-pleylist-dlya-vechirky/|Плейлист для вечірки]].')
        if x.get('p', '').startswith('Якщо обрано Silent Disco'):
            x['p'] = 'Якщо обрано Silent Disco, підготуйте кілька музичних настроїв для різних каналів.'
    b = blk(j, '8. Чекліст'); c = b['cols'][0]
    c[:] = [x for x in c if not x.get('p', '').startswith('Скопіюйте список')]
    for x in c:
        if 'checks' in x and 'Уточнити умови послуги' in x['checks']:
            x['checks'] = ['Уточнити умови й тривалість замовлення', 'Узгодити кількість навушників', 'Перевірити доступність на дату',
                           'Узгодити місце й час доставки', 'Визначити відповідальну людину на локації']
edit('yak-organizuvaty-divych-vechir', divych)

def park(j):
    for x in blk(j, '5. Як організувати звук')['cols'][0]:
        if x.get('p', '').startswith('Якщо плануєте використання бездротових'):
            x['p'] = ('Якщо плануєте бездротові навушники, закладіть час на перевірку сигналу й коротке пояснення учасникам. Докладніше: '
                      '[[/blog/yak-organizuvaty-zvuk-na-zakhodi-prosto-neba/|як організувати звук на заході просто неба]].')
edit('yak-organizuvaty-zakhid-u-parku', park)
print('ok')

# Друга хвиля (перевірка на 1000px): ще два nosplit, абзац Silent Yoga стисло (і без тире), список з одного слова → речення.
edit('divych-vechir-u-navushnykakh', unsplit('Як підготувати музику'))
edit('yoga-v-navushnykakh', unsplit('Як проходить заняття'))

def yoga(j):
    c = blk(j, '5. Звук на природі')['cols'][0]
    for x in c:
        if x.get('h3') == 'Йога в навушниках — Silent Yoga': x['h3'] = 'Йога в навушниках: Silent Yoga'
        if x.get('p', '').startswith('Це формат, у якому учасники слухають'):
            x['p'] = ('Учасники слухають голос інструктора й музику в бездротових навушниках, тож спільну практику можна провести там, де звук із колонок недоречний. '
                      'Докладніше: [[/blog/yoga-v-navushnykakh/|що таке Silent Yoga і як проходить практика]].')
        if x.get('p', '').startswith('Проте навушники'):
            x['p'] = ('Проте навушники не обов’язкові для йоги на природі: вибір залежить від локації, кількості учасників і сценарію заняття. '
                      'Про аудіоформати просто неба читайте в статті [[/blog/yak-organizuvaty-zvuk-na-zakhodi-prosto-neba/|Як організувати звук на заході просто неба]].')
edit('yoga-na-pryrodi', yoga)

def kino(j):
    c = blk(j, '1. Визначте')['cols'][0]
    i = next(i for i, x in enumerate(c) if x.get('p', '').startswith('Приватний кіновечір'))
    c[i]['p'] = 'Приватний кіновечір, показ для мешканців ЖК, корпоративна зустріч і культурна подія мають різні вимоги. Від формату залежать посадка, тривалість, вступне слово, реєстрація й аудіосистема.'
    if i + 1 < len(c) and 'ul' in c[i + 1]: del c[i + 1]
edit('yak-orhanizuvaty-kinopokaz-prosto-neba', kino)
print('ok 2')
