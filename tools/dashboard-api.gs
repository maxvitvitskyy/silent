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
        status:      str(r[18])
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

/** Дати з таблиці приходять то об'єктом Date, то рядком — зводимо до YYYY-MM-DD,
 *  щоб фронт міг порівнювати їх як звичайні рядки, без вгадування часових поясів. */
function fmtDate(v, tz) {
  if (!v) return '';
  if (v instanceof Date) return Utilities.formatDate(v, tz, 'yyyy-MM-dd');
  var s = String(v).trim();
  var m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) return m[1] + '-' + m[2] + '-' + m[3];
  m = s.match(/^(\d{1,2})[.\/](\d{1,2})[.\/](\d{4})/);   // 01.09.2026 або 01/09/2026
  if (m) return m[3] + '-' + pad(m[2]) + '-' + pad(m[1]);
  return '';
}

function fmtTime(v, tz) {
  if (!v) return '';
  if (v instanceof Date) return Utilities.formatDate(v, tz, 'HH:mm');
  var m = String(v).trim().match(/^(\d{1,2}):(\d{2})/);
  return m ? pad(m[1]) + ':' + m[2] : '';
}

function pad(n) {
  return String(n).length < 2 ? '0' + n : String(n);
}
