# SILENT — Silent Disco Landing

Односторінковий лендинг (Київ). Всі зображення винесені з HTML у теку `images/`
і підключені відносними шляхами, тож сайт коректно відкривається локально
та на GitHub Pages.

## Структура
```
.
├── index.html          # головна сторінка
├── audio/              # треки каналів (див. «Музика»)
└── images/
    ├── hero.jpg
    ├── benefits-bg.jpg
    ├── gallery-chill.jpg
    ├── gallery-dance.jpg
    └── gallery-guests.jpg
```

Шрифти підвантажуються з Google Fonts (потрібен інтернет).

## Музика

Кожен канал у hero-секції має власний трек, що зациклюється:

| Канал | Файл | Трек | Автор |
|---|---|---|---|
| RED — Deep & Dance | `audio/red.mp3` | Deep House | Arulo |
| GREEN — Pop & Throwback | `audio/green.mp3` | Disco Ain't Old School | Michael Ramir C. |
| BLUE — Chill & Soul | `audio/blue.mp3` | Cotton Candy R&B Beat | Michael Ramir C. |

Джерело — [Mixkit](https://mixkit.co/free-stock-music/), **Mixkit Stock Music Free
License**: дозволяє комерційне використання, атрибуція не вимагається. Заборонено
перепродаж/поширення самих аудіофайлів як окремого продукту, а також використання
в CD/DVD, відеоіграх та теле-/радіоефірі. Для сайту як фонова музика — дозволено.

Кожен трек — 60-секундний фрагмент, 128 kbps, гучність вирівняна між каналами
(≈ −18 dB mean), щоб перемикання не давало стрибка. Файли завантажуються лише
після того, як відвідувач увімкне звук (`preload="none"`).

Щоб замінити трек — просто поклади інший файл під тим самим ім'ям у `audio/`.

## Локальний перегляд
```bash
python3 -m http.server 8000
# відкрити http://localhost:8000
```

## Публікація на GitHub Pages
Залийте вміст теки в репозиторій, у Settings → Pages оберіть гілку `main` / корінь.
Головна сторінка — `index.html`.
