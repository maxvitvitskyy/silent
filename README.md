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

| Канал | Файл | Трек | Виконавець | Жанр |
|---|---|---|---|---|
| RED — Deep & Dance | `audio/red.mp3` | We Came to Party | Basixx | pop / dance |
| GREEN — Pop & Throwback | `audio/green.mp3` | Don't Stop | I'MIN | contemporary r&b / k-pop |
| BLUE — Chill & Soul | `audio/blue.mp3` | Try Again | mr. | soul / contemporary r&b |

Джерело — **Epidemic Sound** (за підпискою власника сайту). Ліцензія діє в межах
умов підписки; для комерційного сайту потрібен відповідний тариф. Оригінальні
повні треки не зберігаються в репозиторії — лише 60-секундні фрагменти.

Кожен фрагмент: 60 с, 128 kbps, гучність вирівняна між каналами (≈ −18.4 dB mean),
щоб перемикання не давало стрибка. Файли завантажуються лише після того, як
відвідувач увімкне звук (`preload="none"`).

Щоб замінити трек — поклади інший файл під тим самим ім'ям у `audio/`.

## Локальний перегляд
```bash
python3 -m http.server 8000
# відкрити http://localhost:8000
```

## Публікація на GitHub Pages
Залийте вміст теки в репозиторій, у Settings → Pages оберіть гілку `main` / корінь.
Головна сторінка — `index.html`.
