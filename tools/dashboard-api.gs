/**
 * SILENT dashboard — endpoint ТІЛЬКИ на читання.
 *
 * Це ОКРЕМИЙ Apps Script проєкт, не той, що приймає заявки з форми. Так
 * зроблено навмисно: щоб додати читання, не треба передеплоювати скрипт
 * форми, а отже немає ризику, що /exec для POST зміниться і заявки почнуть
 * губитися.
 *
 * Колонка E (телефон / Instagram) сюди НЕ потрапляє взагалі. Дашборд її не
 * показує, а сторінка поки без авторизації — тож найнадійніше не віддавати
 * контакт із сервера, а не ховати його на фронті.
 *
 * ── Як розгорнути ────────────────────────────────────────────────────────
 * 1. script.google.com → New project, назвати «SILENT dashboard API».
 * 2. Вставити цей код, замінити SHEET_ID нижче.
 * 3. Deploy → New deployment → type: Web app.
 *      Execute as:  Me
 *      Who has access:  Anyone
 * 4. Скопіювати URL виду https://script.google.com/macros/s/…/exec
 *    і вставити його в dashboard/index.html у READ_ENDPOINT.
 */

// ID таблиці — та частина URL, що між /d/ і /edit:
// https://docs.google.com/spreadsheets/d/⟨ОСЬ ЦЕ⟩/edit
var SHEET_ID = 'ВСТАВТЕ_ID_ТАБЛИЦІ';

// Скільки днів історії віддавати. Дашборд показує 30, але «Бажана дата»
// дивиться в майбутнє, тож беремо із запасом.
var WINDOW_DAYS = 180;

function doGet() {
  try {
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
        status:      str(r[18]),
        // ТИМЧАСОВЕ поле для діагностики: сире значення й тип клітинок B/C/H,
        // як їх бачить сам Apps Script. dashboard/index.html його ігнорує —
        // він читає лише відомі йому ключі, тож це поле безпечне і нічого
        // не зламає. Прибрати після того, як стане зрозуміло, чому fmtDate/
        // fmtTime не розпізнають формат.
        _dbg: {
          rawB: String(r[1]), typeB: typeof r[1], isDateB: r[1] instanceof Date,
          rawC: String(r[2]), typeC: typeof r[2], isDateC: r[2] instanceof Date,
          rawH: String(r[7]), typeH: typeof r[7], isDateH: r[7] instanceof Date
        }
      });
    }
    return json({ ok: true, rows: rows, generatedAt: new Date().toISOString() });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
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
