# SILENT — Silent Disco Landing

Односторінковий лендинг (Київ). Всі зображення винесені з HTML у теку `images/`
і підключені відносними шляхами, тож сайт коректно відкривається локально
та на GitHub Pages.

## Структура
```
.
├── index.html          # головна сторінка
└── images/
    ├── hero.jpg
    ├── benefits-bg.jpg
    ├── gallery-chill.jpg
    ├── gallery-dance.jpg
    └── gallery-guests.jpg
```

Шрифти підвантажуються з Google Fonts (потрібен інтернет).

## Локальний перегляд
```bash
python3 -m http.server 8000
# відкрити http://localhost:8000
```

## Публікація на GitHub Pages
Залийте вміст теки в репозиторій, у Settings → Pages оберіть гілку `main` / корінь.
Головна сторінка — `index.html`.
