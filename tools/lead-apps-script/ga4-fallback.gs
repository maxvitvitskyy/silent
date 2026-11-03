/**
 * Запасна відправка generate_lead у GA4 через Measurement Protocol.
 *
 * Навіщо. Браузерну подію generate_lead (assets/site.js, sendLeadToGa) може заблокувати розширення чи режим
 * приватності: gtag() тоді нічого не шле, а сайт про це не дізнається. Заявка при цьому в таблиці є. Тому сайт чекає
 * підтвердження від gtag.js (event_callback), і якщо за 3 секунди його немає, шле GET-маячок на цей скрипт із
 * ?ga_fallback=1&lead_id=…&cid=…; тут ми повторюємо подію вже з сервера.
 *
 * Як підключити (скрипт заявок живе в Apps Script, не в цьому репозиторії):
 *  1. Скопіювати функції нижче в проєкт Apps Script, який приймає заявки (де doPost).
 *  2. У doGet(e) першим рядком: if (e && e.parameter && e.parameter.ga_fallback) return handleGaFallback_(e);
 *     (якщо doGet у скрипті заявок нема, створити його лише з цим рядком і запасним ContentService-відповіддю).
 *  3. Project Settings → Script properties: GA4_MEASUREMENT_ID = G-L60PG6EF3E, GA4_API_SECRET = секрет із GA4
 *     (Admin → Data streams → потік → Measurement Protocol API secrets → Create). СЕКРЕТ НЕ КОМІТИТИ й не
 *     вставляти в код: лише в Script properties.
 *  4. Deploy → Manage deployments → нова версія того самого розгортання (URL не міняється).
 *
 * Захист від дубля: на кожен lead_id подія з сервера йде не більше одного разу (CacheService, 6 год).
 * Сервер не бачить, чи справжня подія з браузера дійшла пізніше за 3 с; це рідкісний випадок, і він дасть
 * максимум один зайвий lead на таку заявку.
 */
function handleGaFallback_(e) {
  var p = e.parameter || {};
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('GA4_MEASUREMENT_ID');
  var secret = props.getProperty('GA4_API_SECRET');
  var leadId = String(p.lead_id || '');
  if (!id || !secret || !/^lead_\d+_[a-z0-9]+$/i.test(leadId) || !/^\d+\.\d+$/.test(String(p.cid || ''))) {
    return ContentService.createTextOutput('skip');
  }
  var cache = CacheService.getScriptCache();
  if (cache.get('ga_' + leadId)) return ContentService.createTextOutput('dup');
  cache.put('ga_' + leadId, '1', 21600);

  var payload = {
    client_id: String(p.cid),
    events: [{
      name: 'generate_lead',
      params: {
        lead_id: leadId,
        form_type: String(p.form_type || '').slice(0, 40),
        format: String(p.format || '').slice(0, 20),
        page_language: String(p.lang || '').slice(0, 5),
        utm_source: String(p.utm_source || '').slice(0, 100),
        utm_medium: String(p.utm_medium || '').slice(0, 100),
        utm_campaign: String(p.utm_campaign || '').slice(0, 100),
        delivery: 'server_fallback',
        engagement_time_msec: 1
      }
    }]
  };
  UrlFetchApp.fetch('https://www.google-analytics.com/mp/collect?measurement_id=' + encodeURIComponent(id) +
    '&api_secret=' + encodeURIComponent(secret), {
    method: 'post', contentType: 'application/json', payload: JSON.stringify(payload), muteHttpExceptions: true
  });
  return ContentService.createTextOutput('ok');
}
