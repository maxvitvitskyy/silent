/**
 * SILENT dashboard — Apps Script Web App, який сам віддає сторінку й дані.
 *
 * ЧОМУ ТАК. Раніше dashboard був публічною сторінкою на GitHub Pages, що
 * ходила в окремий публічний JSON-endpoint (розгортання «Anyone», без токена):
 * будь-хто, хто знав адресу — а вона лежить у відкритому репозиторії, — читав
 * заявки. GitHub Pages — статичний хостинг, захистити там нічого не можна, а
 * секрет у JS видно у DevTools. Тому дані й інтерфейс тепер живуть ТУТ:
 *
 *   • doGet() віддає сторінку (Index.html) лише власнику скрипта;
 *   • дані читає серверна функція dashboardData() через google.script.run;
 *   • публічного JSON-endpoint більше немає, токена чи пароля в коді немає —
 *     авторизацію робить сам Google (вхід в акаунт власника).
 *
 * ── Як розгорнути ────────────────────────────────────────────────────────
 * 1. script.google.com → проєкт «SILENT dashboard API» (або новий) → вставити
 *    цей файл як Code.gs, а Index.html — як HTML-файл з іменем «Index».
 *    У SHEET_ID нижче — ID таблиці заявок.
 * 2. Deploy → NEW deployment (не редагувати старе!) → type: Web app
 *      Execute as:      Me
 *      Who has access:  Only myself      ← саме так, НЕ «Anyone»
 * 3. Скопіювати нову адресу …/exec і відкривати її в браузері під своїм Google-
 *    акаунтом. Анонімний відвідувач побачить вхід Google, а не дані.
 * 4. Перевірити, що все працює, і лише тоді ЗАКРИТИ СТАРЕ розгортання (Deploy →
 *    Manage deployments → старе → Archive). Його адреса — у відкритому git, тож
 *    вважається скомпрометованою.
 *
 * Захист у два шари: (1) розгортання «Only myself» — Google не пускає нікого, крім
 * власника; (2) isOwner_() у коді — навіть якщо розгортання помилково зробити
 * «Anyone», анонімний виклик отримає порожню відповідь. Телефон / Instagram
 * (колонка E) не віддається ніколи.
 */

// ID таблиці — та частина URL, що між /d/ і /edit:
// https://docs.google.com/spreadsheets/d/⟨ОСЬ ЦЕ⟩/edit
var SHEET_ID = 'ВСТАВТЕ_ID_ТАБЛИЦІ';

// Скільки днів історії віддавати. Дашборд показує 30, але «Бажана дата»
// дивиться в майбутнє, тож беремо із запасом.
var WINDOW_DAYS = 180;

/** Сторінка. Не власнику — лише «Доступ закрито», жодних даних. */
function doGet() {
  if (!isOwner_()) {
    return HtmlService
      .createHtmlOutput('<!doctype html><meta charset="utf-8"><title>SILENT</title>' +
                        '<p style="font:16px sans-serif">Доступ закрито.</p>')
      .setTitle('SILENT');
  }
  return HtmlService
    .createHtmlOutputFromFile('Index')
    .setTitle('SILENT — Dashboard')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0');
}

/**
 * Дані для сторінки. Викликається з Index.html через google.script.run — це
 * єдиний шлях до заявок. Ім'я без підкреслення, бо google.script.run бачить
 * лише такі функції; isOwner_ нижче — приватна.
 */
function dashboardData() {
  if (!isOwner_()) throw new Error('forbidden');

  var sheet = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
  var values = sheet.getDataRange().getValues();
  var tz = Session.getScriptTimeZone();

  var cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - WINDOW_DAYS);
  var cutoffKey = fmtDate(cutoff, tz);

  var rows = [];
  for (var i = 1; i < values.length; i++) {
    var r = values[i];
    if (!r[0] && !r[3]) continue;              // порожній рядок

    var date = fmtDate(r[1], tz);
    if (date && date < cutoffKey) continue;    // старіше за вікно — не віддаємо

    rows.push({
      id:          str(r[0]),
      date:        date,
      time:        fmtTime(r[2], tz),
      name:        str(r[3]),
      // r[4] — телефон / Instagram. Навмисно не віддається.
      eventType:   str(r[5]),
      guests:      str(r[6]),
      eventDate:   fmtDate(r[7], tz),
      discovery:   str(r[8]),
      comment:     str(r[9]),
      utmSource:   str(r[10]),
      utmMedium:   str(r[11]),
      utmCampaign: str(r[12]),
      device:      str(r[15]),
      os:          str(r[16]),
      browser:     str(r[17]),
      status:      str(r[18])
    });
  }
  return { ok: true, rows: rows, generatedAt: new Date().toISOString() };
}

/**
 * Власник = користувач, що відкрив сторінку, збігається з тим, від чийого імені
 * виконується скрипт. Анонімний відвідувач (розгортання «Anyone») має порожній
 * email — відмова. Якщо розгортання помилково зробити «Execute as: user accessing»,
 * скрипт піде під акаунтом відвідувача і не відкриє таблицю без доступу до неї.
 */
function isOwner_() {
  var active = Session.getActiveUser().getEmail();
  var owner = Session.getEffectiveUser().getEmail();
  return !!active && !!owner && active === owner;
}

function str(v) {
  return v === null || v === undefined ? '' : String(v).trim();
}

// Сітківський «день нуль» для серійних дат: 30 грудня 1899. Якщо клітинка
// прийде як голе число (не Date і не рядок), це і є той серійний формат.
var SHEETS_EPOCH_MS = Date.UTC(1899, 11, 30);

/** Дати з таблиці приходять по-різному: об'єктом Date, рядком або (рідше)
 *  голим числом-серійником. Зводимо все до YYYY-MM-DD, щоб фронт міг
 *  порівнювати їх як звичайні рядки, без вгадування часових поясів. */
function fmtDate(v, tz) {
  if (v === null || v === undefined || v === '') return '';
  if (v instanceof Date) {
    if (isNaN(v.getTime())) return '';                 // «зіпсована» дата
    return Utilities.formatDate(v, tz, 'yyyy-MM-dd');
  }
  if (typeof v === 'number') {
    var d = new Date(SHEETS_EPOCH_MS + Math.round(v) * 86400000);
    return Utilities.formatDate(d, tz, 'yyyy-MM-dd');
  }
  var s = String(v).trim();
  if (!s) return '';
  var m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);                          // 2026-09-01(...)
  if (m) return m[1] + '-' + m[2] + '-' + m[3];
  m = s.match(/^(\d{1,2})[.\/](\d{1,2})[.\/](\d{4})/);                  // 01.09.2026 або 01/09/2026
  if (m) return m[3] + '-' + pad(m[2]) + '-' + pad(m[1]);
  // Останній шанс — віддати це на розсуд самого JS/Apps Script: формати
  // штибу «Tue Sep 01 2026 …» чи локалізовані рядки Date.toString() інакше
  // не зловити регуляркою.
  var parsed = new Date(s);
  if (!isNaN(parsed.getTime())) return Utilities.formatDate(parsed, tz, 'yyyy-MM-dd');
  return '';
}

function fmtTime(v, tz) {
  if (v === null || v === undefined || v === '') return '';
  if (v instanceof Date) {
    if (isNaN(v.getTime())) return '';
    return Utilities.formatDate(v, tz, 'HH:mm');
  }
  if (typeof v === 'number') {
    // Час-без-дати Sheets теж зберігає як частку доби від тієї самої епохи.
    var d = new Date(SHEETS_EPOCH_MS + Math.round(v * 86400000));
    return Utilities.formatDate(d, tz, 'HH:mm');
  }
  var m = String(v).trim().match(/^(\d{1,2}):(\d{2})/);
  return m ? pad(m[1]) + ':' + m[2] : '';
}

function pad(n) {
  return String(n).length < 2 ? '0' + n : String(n);
}
