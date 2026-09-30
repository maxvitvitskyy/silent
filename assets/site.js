/* SILENT — спільний скрипт української та англомовної версій.
   Вийнятий з двох <script> в index.html, логіка не змінена. Увесь текст, який
   скрипт виводить сам (рядки hero, підписи калькулятора, календар, лайтбокс),
   винесений у window.SILENT_I18N: його оголошує сама сторінка перед цим
   файлом. Так поведінка лишається однією на дві мови, а різниться тільки
   набір рядків. */
const I18N = window.SILENT_I18N;

// ---- Замовлення досвіду з картки (.uc-order) — спільне для всіх сторінок ----
// Сторінки з власною формою (головна, /experiences/corporate/) заповнюють
// #comment і скролять до #book на місці. Сторінка-каталог (/experiences/)
// власної форми не має: та сама дія веде на головну через query-параметр
// (?uc=<назва>#book) — а блок унизу файлу, що перевіряє цей параметр після
// завантаження, викликає ту саму функцію другою гілкою (форма вже є) і
// довершує префіл так, ніби це був клік на місці.
function orderExperience(name){
  const form = document.getElementById('book');
  if (!form){
    location.href = '/?uc=' + encodeURIComponent(name) + '#book';
    return;
  }
  const line = I18N.uc.line(name);
  const field = document.getElementById('comment');
  if (field && !field.value.includes(line)){
    field.value = field.value ? field.value + '\n' + line : line;
  }
  const note = document.getElementById('calcSummaryNote');
  if (note){
    note.style.display = 'block';
    note.innerHTML = I18N.uc.note(name);
  }
  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  setTimeout(() => { if (field) field.focus({ preventScroll: true }); }, 600);
}

  // ---- Магнітні кнопки (десктоп) ----
  // Головні кнопки тягнуться до курсора, поки він у межах ~110px, не більше ніж
  // на PULL пікселів — ледь відчутна «тяга», без стрибків. Зсув іде через
  // CSS-змінні --mx/--my на властивість translate (правило .magnet), тож не
  // заважає ні підйому на наведенні (transform), ні натисканню (scale).
  // З GSAP кнопка не просто повертається на місце, а «допружинює» (elastic) —
  // саме цього CSS-transition не вміє. Без GSAP — той самий зсув без пружини.
  (function(){
    const btns = [].slice.call(document.querySelectorAll(
      '.hero-actions .btn-primary, .band-cta-btn, .f-cta, .f-soc'));
    if (!btns.length || !window.matchMedia('(hover: hover) and (pointer: fine)').matches ||
        window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const G = window.gsap;
    const RANGE = 110;
    const items = btns.map(function(btn){
      const it = { btn: btn, pull: btn.classList.contains('f-soc') ? 6 : 8, o: { x: 0, y: 0 } };
      btn.classList.add('magnet');
      const paint = function(){
        btn.style.setProperty('--mx', it.o.x.toFixed(2) + 'px');
        btn.style.setProperty('--my', it.o.y.toFixed(2) + 'px');
      };
      if (G){
        const cfg = { duration: 0.9, ease: 'elastic.out(1, 0.42)', onUpdate: paint };
        it.qx = G.quickTo(it.o, 'x', cfg);
        it.qy = G.quickTo(it.o, 'y', cfg);
      } else {
        it.set = function(x, y){ it.o.x = x; it.o.y = y; paint(); };
      }
      return it;
    });
    let raf = 0, px = 0, py = 0;
    function apply(){
      raf = 0;
      items.forEach(function(it){
        const r = it.btn.getBoundingClientRect();
        // Кнопки поза екраном не рахуємо: getBoundingClientRect дешевий, але
        // цикл іде на кожен рух миші.
        if (r.bottom < -RANGE || r.top > innerHeight + RANGE) return;
        const dx = px - (r.left + r.width / 2), dy = py - (r.top + r.height / 2);
        const d = Math.hypot(dx, dy), reach = RANGE + r.width / 2;
        let x = 0, y = 0;
        if (d <= reach){
          const f = (1 - d / reach) * it.pull / (d || 1);
          x = dx * f; y = dy * f;
        }
        if (it.qx){ it.qx(x); it.qy(y); } else it.set(x, y);
      });
    }
    window.addEventListener('pointermove', function(e){
      px = e.clientX; py = e.clientY;
      if (!raf) raf = requestAnimationFrame(apply);
    }, { passive: true });
  })();

  // ---- Рухоме підсвічення розділів у mega-меню (десктоп) ----
  // Один елемент .nav-mega-glow на сітку: під курсором (або фокусом) він
  // стає рівно по колонці розділу й переїжджає до сусіднього, а не блимає.
  // Колір, лінію під заголовком і сам заголовок підсвічує CSS (:hover колонки);
  // тут лише геометрія, бо чистим CSS між довільними клітинками сітки не
  // переїхати. Фото-колонка (без .nav-mega-card) підсвічення не дістає.
  (function(){
    document.querySelectorAll('.nav-mega-grid').forEach(function(grid){
      const glow = document.createElement('div');
      glow.className = 'nav-mega-glow';
      glow.setAttribute('aria-hidden', 'true');
      // Не всередині сітки: розкладка колонок тримається на :nth-child і
      // :last-child, а ще один дочірній елемент їх зсунув би. Панель —
      // абсолютний контейнер, тож координати рахуємо від неї.
      const panel = grid.parentNode;
      panel.insertBefore(glow, grid);
      let live = false;
      function show(col){
        const g = panel.getBoundingClientRect(), c = col.getBoundingClientRect();
        // Перше з'явлення — без переїзду з минулого місця: спершу ставимо на
        // колонку без transition, і лише потім вмикаємо рух для наступних.
        glow.style.width = c.width + 'px';
        glow.style.height = c.height + 'px';
        glow.style.transform = 'translate(' + (c.left - g.left) + 'px,' + (c.top - g.top) + 'px)';
        glow.classList.add('is-on');
        if (!live){ requestAnimationFrame(function(){ glow.classList.add('is-live'); }); live = true; }
      }
      function hide(){
        glow.classList.remove('is-on', 'is-live');
        live = false;
      }
      grid.addEventListener('mouseover', function(e){
        const col = e.target.closest('.nav-mega-col');
        if (!col || !grid.contains(col)) return;
        if (col.querySelector('.nav-mega-card')) show(col); else hide();
      });
      grid.addEventListener('focusin', function(e){
        const col = e.target.closest('.nav-mega-col');
        if (col && col.querySelector('.nav-mega-card')) show(col);
      });
      grid.addEventListener('mouseleave', hide);
      grid.addEventListener('focusout', function(e){
        if (!grid.contains(e.relatedTarget)) hide();
      });
    });
  })();

  // ---- Parallax on the hero background photos ----
  // Each layer drifts vertically at a fraction of scroll speed. Layers are
  // oversized in CSS so the translate never exposes an edge. Skipped entirely
  // when the user prefers reduced motion.
  // Плями в секціях сюди НЕ входять: у них власний нескінченний дрейф у CSS,
  // а скролл-паралакс зверху ще й зсував би їхню маску відносно секції — край
  // згасання виїжджав би за обріз, і замість плавного виходу з'являлася б
  // різка межа саме там, де вона найпомітніша.
  (function(){
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) return;
    const layers = [
      { el: document.querySelector('.hero'), section: document.querySelector('.hero'), speed: 0.18, photos: true },
      // Танцівниця їде помітніше за зал позаду, але стеля ходу в неї власна й
      // рахується на льоту (autoMax). У фонових шарів є запас за краями секції,
      // а її коробка — рівно кадр, і вона стоїть лише за кілька десятків
      // пікселів від низу .hero. На спільних 150px вона виїжджала за цей край, і
      // overflow:hidden різав її різкою межею просто під панеллю. Фіксоване
      // число натомість зупиняло її посеред прокрутки — швидкість підібрана так,
      // щоб вона не впиралась у стелю, поки hero у кадрі.
      { el: document.getElementById('heroDancer'), section: document.querySelector('.hero'), speed: 0.11, autoMax: true }
    ].filter(l => l.el && l.section);
    // Фонові знімки hero їдуть разом: активний видно, решта прозорі.
    const heroPhotoEls = [].slice.call(document.querySelectorAll('.hero-photo'));
    let ticking = false;
    // innerHeight на телефоні стрибає щоразу, коли ховається адресний рядок, а
    // він входить у формулу зсуву — фігура через це смикалась на кожен дотик.
    // Тому висота кешується й оновлюється лише разом із шириною.
    let vhCache = window.innerHeight, wCache = window.innerWidth;
    function update(){
      if (window.innerWidth !== wCache){
        wCache = window.innerWidth; vhCache = window.innerHeight;
      }
      const vh = vhCache;
      for (const l of layers){
        const r = l.section.getBoundingClientRect();
        // delta = швидкість × scrollY, а не «відстань від центру секції до
        // центру вікна» (як було): та версія давала нульовий зсув лише коли
        // висота секції рівно дорівнює висоті вікна. .hero має
        // min-height: min(100svh, 1040px) — на вікнах вищих за 1040px секція
        // коротша за viewport, і навіть при scrollY=0 (сторінка щойно
        // завантажилась, ще ніхто не скролив) формула видавала ненульовий
        // зсув — фотографія/відео стартували вже зсунутими вниз, і згори
        // з'являлась чорна смуга під шапкою (рамка .hero-video-frame
        // розрахована на зсув=0 у стані спокою). Обидві формули лінійні за
        // scrollY з однаковим нахилом (швидкість), відрізняються лише
        // константою зсуву — тож ця версія дає ту саму швидкість дрейфу під
        // час скролу, просто без хибного стартового зміщення.
        let delta = l.speed * window.scrollY;
        // never travel further than the overhang, or the layer's edge appears
        let MAX = 150;
        if (l.autoMax){
          // Скільки лишилось до низу секції (без урахування вже накладеного
          // зсуву) плюс прозорий хвіст маски, який однаково нічого не показує.
          const rect = l.el.getBoundingClientRect();
          const room = r.bottom - (rect.bottom - (l._d || 0));
          MAX = Math.max(30, room + rect.height * 0.06);
        }
        delta = Math.max(-MAX, Math.min(MAX, delta));
        l._d = delta;
        const t = 'translate3d(0,' + delta.toFixed(1) + 'px,0)';
        if (l.photos) heroPhotoEls.forEach(function(p){ p.style.transform = t; });
        else l.el.style.transform = t;
      }
      ticking = false;
    }
    function onScroll(){
      if (!ticking){ requestAnimationFrame(update); ticking = true; }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  })();

  const channels = [
    { color:'#ff4757', soft:'rgba(var(--red-rgb), 0.14)',  glow:'rgba(var(--red-rgb), 0.45)'  },
    { color:'#2ed573', soft:'rgba(var(--green-rgb), 0.14)', glow:'rgba(var(--green-rgb), 0.45)' },
    { color:'#3da8ff', soft:'rgba(var(--blue-rgb), 0.14)', glow:'rgba(var(--blue-rgb), 0.45)' }
  ];
  const btns = Array.from(document.querySelectorAll('.ch-toggle'));
  const heroDancerEl = document.getElementById('heroDancer');
  // Background position is controlled by CSS (focal point on the dancer, with a
  // mobile media-query variant) — do not override it here.

  // Hero copy per channel — the toggles double as a content slider. Each slide
  // has three headline lines (one word optionally accented lime via
  // {lime:'word'}) and a sub; the fact line above the headline is static and
  // doesn't change per channel, unlike the old per-channel eyebrow it replaced.
  // RED is slide 0 / default.
  // lines — десктопні рядки (три, кожен в один ряд). mLines — мобільний набір:
  // на телефоні композиція журнальна, і розподіл слів по рядках у кожного каналу
  // свій, з власними зсувами. Другий елемент пари — клас зсуву (s1/s2/s3/sr).
  // Підзаголовки навмисно вирівняні за довжиною (~130–140 знаків): у вузькій
  // правій колонці різна довжина одразу ламала б висоту композиції.
  const heroContent = I18N.hero;
  const heroLines = document.getElementById('heroLines');
  const heroSub = document.getElementById('heroSub');

  // Render a headline line, converting {word} into a lime accent span.
  function renderLine(text){
    return text.replace(/\{([^}]+)\}/g, '<span class="accent-lime">$1</span>');
  }

  // 600, а не 760: той самий запит, що й у мобільному блоці hero в CSS. Вище
  // цієї ширини йде планшетна композиція з десктопними рядками, бо журнальний
  // набір зі зсувами розрахований на колонку завширшки з вертикальний телефон і
  // між 600 і 760 розсипався — рядок зі зсувом відлітав до правого краю.
  const heroNarrow = window.matchMedia('(max-width: 600px)');
  // Той самий запит, що й у CSS-блоці горизонтальної орієнтації нижче: обидва
  // мусять вмикатись і вимикатись разом, інакше розкладка й набір рядків
  // розійдуться.
  const heroLandscape = window.matchMedia('(max-width: 900px) and (max-height: 480px) and (orientation: landscape)');
  // Планшет бере короткий підзаголовок, але НЕ мобільні рядки заголовка: mLines —
  // це журнальна розкладка під вузьку колонку, і на 900px вона розсипалась би.
  const heroShortSub = window.matchMedia('(max-width: 1100px)');
  // На телефоні підзаголовок — одне коротке речення: довгий текст у вузькій
  // колонці поруч із фігурою розвалював композицію.
  function heroSubText(data){
    return (heroShortSub.matches && data.mSub) ? data.mSub : data.sub;
  }
  // Пари [текст, клас] для поточної ширини: на телефоні — мобільний набір,
  // інакше десктопні рядки без зсувів.
  // mLines — журнальна розкладка під колонку завширшки з вертикальний екран:
  // чотири-п'ять коротких рядків зі зсувами. У горизонталі телефона екран удвічі
  // ширший і втричі нижчий, і там ця розкладка давала вузький стовпчик тексту
  // при порожній половині кадру, а зсунутий рядок відлітав до правого краю.
  // Тому в горизонталі беруться десктопні три рядки.
  // Умова саме така, а не «вузько і високо»: у вузькому ВЕРТИКАЛЬНОМУ вікні
  // нижче 481px колонка все одно лишається вузькою, і довгі десктопні рядки з
  // white-space: nowrap вилізли б за екран.
  function heroLineSet(data){
    return (heroNarrow.matches && !heroLandscape.matches && data.mLines)
      ? data.mLines
      : data.lines.map(t => [t, '']);
  }
  // Кількість рядків між наборами різна, тож спани щоразу будуються наново, а не
  // переписуються на місці.
  function paintHeadline(data){
    heroLines.innerHTML = heroLineSet(data).map(([text, cls]) =>
      '<span' + (cls ? ' class="' + cls + '"' : '') + '>' + renderLine(text) + '</span>'
    ).join('');
    return [...heroLines.querySelectorAll(':scope > span')];
  }

  let heroIndex = 0;

  // Reserve the headline and sub heights for the tallest of the three slides at
  // the current width, so the hero doesn't shift on each switch. Measured
  // synchronously (no paint between swaps) and re-run on resize / after fonts load.
  function reserveHeroSubHeight(){
    if (!heroSub || !heroLines) return;
    heroSub.style.minHeight = '0px';
    heroLines.style.minHeight = '0px';
    let maxSub = 0, maxLines = 0;
    for (const c of heroContent){
      heroSub.textContent = heroSubText(c);
      if (heroSub.offsetHeight > maxSub) maxSub = heroSub.offsetHeight;
      paintHeadline(c);
      if (heroLines.offsetHeight > maxLines) maxLines = heroLines.offsetHeight;
    }
    // Відновлюємо з даних, а не з того, що було в DOM: при першому виклику там
    // лежить довгий серверний текст, і на телефоні він так і лишався б замість
    // короткого варіанта.
    heroSub.textContent = heroSubText(heroContent[heroIndex]);
    paintHeadline(heroContent[heroIndex]);
    heroSub.style.minHeight = maxSub + 'px';
    heroLines.style.minHeight = maxLines + 'px';
  }
  reserveHeroSubHeight();
  if (document.fonts && document.fonts.ready){ document.fonts.ready.then(reserveHeroSubHeight); }
  let heroSubResizeTimer = null;
  // Тільки на зміну ШИРИНИ. На телефоні поява й ховання адресного рядка під час
  // звичайної прокрутки теж кидає resize, а перерахунок будує спани наново — і
  // заголовок програвав анімацію появи щоразу, коли палець ледь торкався екрана.
  let heroLastW = window.innerWidth;
  window.addEventListener('resize', () => {
    if (window.innerWidth === heroLastW) return;
    heroLastW = window.innerWidth;
    clearTimeout(heroSubResizeTimer);
    heroSubResizeTimer = setTimeout(reserveHeroSubHeight, 150);
  });
  // Перехід через 760px міняє сам набір рядків, а через 1100px — довжину
  // підзаголовка; обидва змінюють вміст, а не лише його ширину.
  // Горизонтальна орієнтація телефона (heroLandscape, оголошений вище) міняє і
  // набір рядків, і кегль, а отже і висоту заголовка. Поворот пристрою міняє й
  // ширину, тож resize вище спрацював би й сам, але вікно можна стиснути і по
  // одній висоті — тоді резерв лишався б від попереднього набору.
  const onHeroBreakpoint = () => reserveHeroSubHeight();
  [heroNarrow, heroShortSub, heroLandscape].forEach(mq => {
    if (mq.addEventListener) mq.addEventListener('change', onHeroBreakpoint);
    else mq.addListener(onHeroBreakpoint);
  });

  let heroInited = false;
  let heroSwapTimer = null;
  // Усі три SEO-фрази вже в DOM (розмітка вище) — тут лише перемикається,
  // яка видима. На відміну від заголовка нижче, це не залежить від heroInited:
  // клас коректний уже в статичному HTML (data-ch="0" — активна), тож на
  // першому виклику це просто no-op, а не пропуск анімації.
  function updateHeroFacts(i){
    document.querySelectorAll('.hf-phrase').forEach(el => {
      el.classList.toggle('active', Number(el.dataset.ch) === i);
    });
  }

  function updateHeroText(i){
    const data = heroContent[i];
    updateHeroFacts(i);
    if (!data || !heroLines || !heroSub) return;
    heroIndex = i;
    // On the very first call, content already matches slide 0 (server-rendered)
    // and the initial CSS rise animation is playing — don't replay it.
    if (!heroInited){ heroInited = true; return; }

    const oldSpans = [...heroLines.querySelectorAll(':scope > span')];
    const out = [heroSub, ...oldSpans];
    // paintHeadline будує спани наново (у слайдів різна кількість рядків), тож
    // новий набір повертається звідси й анімується вже він, а не старий.
    const applyNew = () => {
      heroSub.textContent = heroSubText(data);
      return [heroSub, ...paintHeadline(data)];
    };

    // Reduced-motion / no-anim: swap instantly, no transition.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      out.forEach(el => el.classList.remove('swap-out', 'swap-in'));
      applyNew().forEach(el => el.classList.remove('swap-out', 'swap-in'));
      return;
    }

    // Phase 1: ease the current copy up and out.
    out.forEach(el => { el.classList.remove('swap-in'); el.classList.add('swap-out'); });

    // Phase 2 (after the fade-out): swap the text, then rise the new copy in.
    clearTimeout(heroSwapTimer);
    heroSwapTimer = setTimeout(() => {
      const fresh = applyNew();
      fresh.forEach(el => el.classList.remove('swap-out'));
      void heroLines.offsetWidth; // reflow so swap-in restarts cleanly
      fresh.forEach(el => el.classList.add('swap-in'));
    }, 300);
  }

  // deferGlow: тільки для початкового виклику на завантаженні. litStrip()
  // читає getBoundingClientRect() і тим форсує синхронний layout усього
  // документа — на старті сторінки це заважає першому paint. Клас
  // heroDancer.active має лишитись синхронним: якщо додати його пізніше,
  // ПІСЛЯ того як браузер уже намалював кадр без нього,
  // CSS-transition на opacity вперше реально запуститься з 0 замість
  // миттєвого фінального стану — і рендер спотвориться (перевірено:
  // саме так і сталось, коли відкладався весь setChannel()).
  function setChannel(i, deferGlow){
    const c = channels[i];
    // Не в root: інакше колір каналу розтікався б по всьому сайту — по eyebrow,
    // цифрах, іконках, підсвітках. Панель перевизначає змінні лише для себе.
    const panel = document.getElementById('channels');
    if (panel){
      panel.style.setProperty('--ch', c.color);
      panel.style.setProperty('--ch-soft', c.soft);
      panel.style.setProperty('--ch-glow', c.glow);
    }
    btns.forEach((b, idx) => {
      const isActive = idx === i;
      b.classList.toggle('active', isActive);
      const sw = b.querySelector('.ch-switch');
      if (sw) sw.setAttribute('aria-pressed', String(isActive));
      if (isActive){
        b.style.setProperty('--active-color', c.color);
        b.style.setProperty('--active-soft', c.soft);
        b.style.setProperty('--active-glow', c.glow);
      }
    });
    // Фон більше не залежить від каналу (одне зациклене відео замість трьох
    // знімків), тож тут лишається тільки фігура.
    if (heroDancerEl) heroDancerEl.classList.add('active');
    updateHeroText(i);
    if (deferGlow) requestAnimationFrame(() => litStrip(c.color, i));
    else litStrip(c.color, i);
    playChannel(i);
  }
  const stripEl = document.getElementById('channels');
  // Ставить блоб центром у (cx, cy) і розміром (w, h) через один transform.
  // База в CSS: 300×100% у лівому верхньому куті, тож центр бази — (150, H/2).
  const BLOB_BASE_W = 300;
  function placeBlob(cx, cy, w, h, stripH){
    const sx = w / BLOB_BASE_W;
    const sy = stripH ? h / stripH : 1;
    const tx = cx - BLOB_BASE_W / 2;
    const ty = cy - stripH / 2;
    glowBlob.style.transform =
      'translate3d(' + tx.toFixed(1) + 'px,' + ty.toFixed(1) + 'px,0) scale(' +
      sx.toFixed(3) + ',' + sy.toFixed(3) + ')';
  }
  function litStrip(color, idx){
    if (!stripEl || !glowBlob) return;
    stripEl.style.setProperty('--glow-color', color);
    glowBlob.classList.add('on');

    const target = btns[idx];
    if (!target) return;
    const stripRect = stripEl.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();

    // Detect vertical stacking (mobile: toggles are stacked, so widths ~ full strip width)
    const firstRect = btns[0].getBoundingClientRect();
    const secondRect = btns[1] ? btns[1].getBoundingClientRect() : firstRect;
    const isStacked = Math.abs(secondRect.top - firstRect.top) > firstRect.height * 0.5;

    if (isStacked){
      // Vertical mode: glow hugs the active toggle's row vertically, full width
      const centerY = targetRect.top - stripRect.top + targetRect.height / 2;
      const blobHeight = Math.max(targetRect.height * 1.4, 120);
      // Коробка блоба — 300×H у лівому верхньому куті смуги; сюди рахуємо зсув і
      // масштаб її центру до потрібного місця. Трансформація не чіпає розкладку.
      placeBlob(0.5 * stripRect.width, centerY, stripRect.width, blobHeight, stripRect.height);

      if (outlineEq){
        outlineEq.style.left = '0';
        outlineEq.style.width = '100%';
        // Sit in the middle of the gap below the active toggle rather than flush
        // with its bottom edge, so the bars read as centred between the rows.
        const row = target.parentElement;
        const rowGap = parseFloat(getComputedStyle(row).rowGap) || 12;
        const eqH = outlineEq.offsetHeight || 18;
        const centreY = targetRect.bottom + rowGap / 2;
        outlineEq.style.bottom = (stripRect.bottom - (centreY + eqH / 2)) + 'px';
        outlineEq.style.setProperty('--glow-color', color);
        outlineEq.classList.add('on');
      }
    } else {
      // Horizontal mode (desktop): glow hugs the active toggle's column
      const centerX = targetRect.left - stripRect.left + targetRect.width / 2;
      const blobWidth = Math.max(targetRect.width * 1.5, 240);
      // По вертикалі — те саме, що давали bottom:-40% і height:200%:
      // центр на 0.4 висоти смуги, висота вдвічі більша за неї.
      placeBlob(centerX, 0.4 * stripRect.height, blobWidth, 2 * stripRect.height, stripRect.height);

      if (outlineEq){
        outlineEq.style.left = (targetRect.left - stripRect.left) + 'px';
        outlineEq.style.width = targetRect.width + 'px';
        outlineEq.style.bottom = '2px';
        outlineEq.style.setProperty('--glow-color', color);
        outlineEq.classList.add('on');
      }
    }
  }
  const glowBlob = document.getElementById('chGlowBlob');
  const outlineEq = document.getElementById('chOutlineEq');
  window.addEventListener('resize', () => {
    const activeIdx = btns.findIndex(b => b.classList.contains('active'));
    if (activeIdx !== -1) litStrip(channels[activeIdx].color, activeIdx);
  });
  const muteBtn = document.getElementById('chMute');
  const muteLabel = muteBtn?.querySelector('.ch-mute-label');
  let lastChannel = 0;
  let isMuted = false;
  function syncMuteBtn(){
    // .is-silent лише після свідомого вимкнення: на завантаженні звуку теж немає
    // (браузер не дає його без жесту), але панель там має світитись, а не
    // виглядати вимкненою.
    if (stripEl) stripEl.classList.toggle('is-silent', isMuted);
    if (muteBtn) muteBtn.setAttribute('aria-pressed', String(!soundOn));
    if (muteLabel) muteLabel.textContent = soundOn ? I18N.sound.on : I18N.sound.off;
    if (muteBtn) muteBtn.title = soundOn ? I18N.sound.mute : I18N.sound.off;
  }

  // ---- Геро: текст «відпускає» разом із прокруткою (десктоп, ScrollTrigger) ----
  // Танцівниця й фон уже їдуть паралаксом вище; текст стояв на місці й
  // залишав геро пласким: усе рухалось, крім головного. Тепер заголовок і
  // блок кнопок повільно підпливають угору й тьмяніють, поки геро йде з кадру,
  // — із різною швидкістю, тож між ними й фігурою виникає глибина.
  // Рухаємо обгортки .hero-top/.hero-bottom, а не самі рядки заголовка: у тих
  // власна CSS-анімація появи й перемикання каналів на transform.
  // scrub: 0.6 — рух наздоганяє прокрутку з невеликою інерцією, без ривків.
  // gsap.matchMedia сам повертає елементам початковий стан, коли умова
  // перестає діяти (вікно звузили до планшета, увімкнули reduce-motion).
  (function(){
    const G = window.gsap, ST = window.ScrollTrigger;
    const hero = document.querySelector('.hero');
    if (!G || !ST || !hero) return;
    G.registerPlugin(ST);
    G.matchMedia().add('(min-width: 1000px) and (prefers-reduced-motion: no-preference)', function(){
      const top = hero.querySelector('.hero-top'), bottom = hero.querySelector('.hero-bottom');
      if (!top || !bottom) return;
      const tl = G.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom 35%', scrub: 0.6 }
      });
      tl.to(top,    { y: -70, opacity: 0.15 }, 0)
        .to(bottom, { y: -36, opacity: 0.25 }, 0);
      // Страховка від «залипання»: scrub із згладжуванням наздоганяє прокрутку з
      // запізненням, і при різкому поверненні нагору (клавіша Home, якір «нагору»,
      // швидкий жест) слід міг зупинитись, не дійшовши до нуля — текст лишався
      // напівпрозорим. Коли прокрутка стоїть біля верху, доводимо в нуль сами.
      let idle = 0;
      const settleTop = () => {
        if (window.scrollY > 4) return;
        tl.progress(0);
        G.set([top, bottom], { opacity: 1, y: 0 });
      };
      const onScroll = () => { clearTimeout(idle); idle = setTimeout(settleTop, 160); };
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('pageshow', settleTop);
      document.addEventListener('visibilitychange', () => { if (!document.hidden) settleTop(); });
      return () => { window.removeEventListener('scroll', onScroll); window.removeEventListener('pageshow', settleTop); clearTimeout(idle); };
    });
  })();

  // ---- Channel audio ----
  // Each channel owns a looping track. Files are fetched only on demand
  // (preload="none"), so a visitor who never turns sound on downloads nothing.
  // Browsers block autoplay, so playback can only begin from a real gesture:
  // clicking a channel toggle or the sound button.
  // Bump AUDIO_VER whenever a track file is replaced. Without it browsers keep
  // serving the previously cached mp3 and returning visitors hear the old track.
  const AUDIO_VER = '2';
  // I18N.base — єдиний шлях у скрипті, який не приходить із розмітки: решту
  // адрес він читає з атрибутів, а ті вже написані відносно своєї сторінки.
  // Українська сторінка лежить у корені, англійська на рівень глибше.
  const AUDIO_SRC = ['audio/red.mp3', 'audio/green.mp3', 'audio/blue.mp3']
    .map(src => I18N.base + src + '?v=' + AUDIO_VER);
  const AUDIO_VOL = 0.55;
  const FADE_MS = 700;
  const players = [];
  let soundOn = false;
  const activeIdx = () => { const i = btns.findIndex(b => b.classList.contains('active')); return i === -1 ? 0 : i; };

  function player(i){
    if (!players[i]){
      const a = document.createElement('audio');
      a.preload = 'none';
      a.loop = true;
      a.src = AUDIO_SRC[i];
      a.volume = 0;
      a.hidden = true;
      a.setAttribute('data-channel', String(i));
      document.body.appendChild(a);
      players[i] = a;
    }
    return players[i];
  }
  // Ramp volume so channel switches crossfade instead of cutting.
  function fade(a, to, ms){
    if (a._fade) cancelAnimationFrame(a._fade);
    const from = a.volume, t0 = performance.now();
    return new Promise(res => {
      (function step(now){
        const p = ms <= 0 ? 1 : Math.min(1, (now - t0) / ms);
        a.volume = Math.max(0, Math.min(1, from + (to - from) * p));
        if (p < 1) a._fade = requestAnimationFrame(step);
        else { a._fade = null; res(); }
      })(t0);
    });
  }
  function playChannel(i){
    if (!soundOn) return;
    players.forEach((pl, idx) => {
      if (pl && idx !== i && !pl.paused) fade(pl, 0, FADE_MS).then(() => pl.pause());
    });
    const a = player(i);
    a.volume = 0;
    const started = a.play();
    if (started && started.catch) started.catch(() => {});
    fade(a, AUDIO_VOL, FADE_MS);
  }
  function stopAudio(){
    players.forEach(pl => { if (pl && !pl.paused) fade(pl, 0, 350).then(() => pl.pause()); });
  }
  // Don't leave music running in a tab the visitor has switched away from.
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopAudio();
    else if (soundOn) playChannel(activeIdx());
  });

  btns.forEach((b, idx) => b.addEventListener('click', () => {
    // Повторний клік по вже активному каналі глушить його: сам перемикач і є
    // вимикачем, а не лише селектором. setChannel тут не викликаємо — канал
    // лишається обраним, і заголовок не програє підміну заново.
    if (b.classList.contains('active') && soundOn){
      soundOn = false;
      isMuted = true;
      stopAudio();
      syncMuteBtn();
      return;
    }
    // Picking a channel is a deliberate gesture on a control labelled
    // "Оберіть канал" — so it both selects and starts that channel's sound.
    isMuted = false;
    soundOn = true;
    setChannel(idx);
    syncMuteBtn();
  }));
  // deferGlow=true: лише геометрія підсвітки перемикача (litStrip) чекає
  // кадр, класи .active йдуть синхронно, як і завжди — деталі в коментарі
  // над setChannel().
  setChannel(0, true);
  syncMuteBtn();

  // ---- Master sound toggle ----
  // On load the panel is lit but silent (no gesture yet), and the button reads
  // "Увімкнути звук" to invite the first click. Muting still dims the glow and
  // eq bars, so the panel visibly goes quiet along with the audio.
  function setMuted(muted){
    isMuted = muted;
    if (muted){
      soundOn = false;
      stopAudio();
      lastChannel = activeIdx();
      btns.forEach(b => b.classList.remove('active'));
      if (glowBlob) glowBlob.classList.remove('on');
      if (outlineEq) outlineEq.classList.remove('on');
    } else {
      soundOn = true;
      setChannel(lastChannel);
    }
    syncMuteBtn();
  }
  if (muteBtn) muteBtn.addEventListener('click', () => setMuted(soundOn));

  // ---- Auto-advance hero slider ----
  // The channel toggles double as a content slider, so when nobody is
  // interacting we cycle RED → GREEN → BLUE on a timer. 6.5s per slide gives
  // time to read the ~2-sentence sub without feeling sluggish; the ~1s swap
  // animation runs on top of that idle time. Any manual click resets the timer;
  // it pauses while the panel is hovered, while music is playing (a track
  // shouldn't flip every 6.5s), while muted, or when the tab is hidden.
  (function(){
    const AUTO_MS = 6500;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let autoTimer = null;
    const current = () => btns.findIndex(b => b.classList.contains('active'));
    function stop(){ clearTimeout(autoTimer); autoTimer = null; }
    function start(){
      if (reduceMotion || isMuted || soundOn || document.hidden) return;
      stop();
      autoTimer = setTimeout(() => {
        setChannel((current() + 1) % channels.length);
        start();
      }, AUTO_MS);
    }
    btns.forEach(b => b.addEventListener('click', () => { stop(); start(); }));
    if (muteBtn) muteBtn.addEventListener('click', () => { stop(); start(); });
    if (stripEl){
      stripEl.addEventListener('mouseenter', stop);
      stripEl.addEventListener('mouseleave', start);
    }
    document.addEventListener('visibilitychange', () => { document.hidden ? stop() : start(); });
    start();
  })();

  // ---- Price calculator ----
  const fmt = new Intl.NumberFormat(I18N.locale);
  const headphoneRange = document.getElementById('headphoneRange');
  const calcHeadphones = document.getElementById('calcHeadphones');
  const calcTotal = document.getElementById('calcTotal');
  const baseLine = document.getElementById('baseLine');
  const extraLine = document.getElementById('extraLine');
  const hoursLine = document.getElementById('hoursLine');
  const optionsLine = document.getElementById('optionsLine');
  const perHeadLine = document.getElementById('perHeadLine');
  const outsideKyiv = document.getElementById('outsideKyiv');
  const contentReel = document.getElementById('contentReel');
  const smokeLight = document.getElementById('smokeLight');
  const guestsSelect = document.getElementById('guests');
  const hoursValueEl = document.getElementById('hoursValue');
  const hourMinus = document.getElementById('hourMinus');
  const hourPlus = document.getElementById('hourPlus');
  let hours = 4;
  const MIN_HOURS = 4, MAX_HOURS = 8;

  // База: 40 навушників / 4 год = 9 800 грн. Кожен навушник понад 40 — 244 грн
  // (ставка лишилась тією, що була, коли стеля була 90: 12 200 / 50). Стеля
  // слайдера — 100 навушників (максимум на першому етапі), там показуємо «100+».
  // Ціни до 90 навушників не змінились; на 100 — 24 440 грн за 4 години.
  const MAX_QTY = 100;
  const EXTRA_PER_HEADPHONE = 244;
  function calcPrice(qty){
    const base = 9800;
    const extraQty = Math.max(0, qty - 40);
    const extra = extraQty * EXTRA_PER_HEADPHONE;
    // Година рахується від самого пакета, а не фіксованою ставкою: базові
    // 4 години коштують base + extra, тож одна година — рівно чверть від цього.
    const hourPrice = Math.round((base + extra) / MIN_HOURS);
    const extraHours = Math.max(0, hours - MIN_HOURS);
    const hoursCost = extraHours * hourPrice;
    const options =
      (outsideKyiv.checked ? 4000 : 0) +
      (contentReel.checked ? 2000 : 0) +
      (smokeLight.checked ? 4000 : 0);
    return { base, extra, hoursCost, options, total: Math.max(6900, base + extra + hoursCost + options) };
  }

  function syncGuestSelect(qty){
    if (!guestsSelect) return;
    if (qty <= 60) guestsSelect.value = '40–60';
    else if (qty <= 80) guestsSelect.value = '60–80';
    else guestsSelect.value = '80–100';
  }

  function updateCalculator(){
    if (!headphoneRange) return;
    const qty = Number(headphoneRange.value);
    const price = calcPrice(qty);
    // At the ceiling show "100+": the slider stops there, but larger events are
    // still possible — it reads as "90 or more", not a hard limit.
    calcHeadphones.textContent = qty >= MAX_QTY ? `${MAX_QTY}+` : qty;
    calcTotal.textContent = fmt.format(price.total);
    baseLine.textContent = `${fmt.format(price.base)} ${I18N.currency}`;
    extraLine.textContent = `${fmt.format(price.extra)} ${I18N.currency}`;
    hoursLine.textContent = `${fmt.format(price.hoursCost)} ${I18N.currency}`;
    optionsLine.textContent = `${fmt.format(price.options)} ${I18N.currency}`;
    perHeadLine.textContent = `${fmt.format(Math.round(price.total / qty))} ${I18N.currency}`;
    syncGuestSelect(qty);
    hourMinus.disabled = hours <= MIN_HOURS;
    hourPlus.disabled = hours >= MAX_HOURS;
  }
  [headphoneRange, outsideKyiv, contentReel, smokeLight].forEach((el) => {
    if (el) el.addEventListener('input', updateCalculator);
    if (el) el.addEventListener('change', updateCalculator);
  });
  // На сторінках без калькулятора цих кнопок немає. Раніше звертання до них
  // напряму валило весь site.js, а з ним і все, що нижче за текстом файла:
  // поява блоків, стрічка, плаваючий контакт і прапорець __siteJs. Решта
  // елементів калькулятора вже перевіряється через `if (el)` вище — ці дві
  // лишались єдиним незахищеним місцем.
  if (hourMinus && hourPlus && hoursValueEl) {
    hourMinus.addEventListener('click', () => {
      if (hours > MIN_HOURS){ hours--; hoursValueEl.textContent = hours; updateCalculator(); }
    });
    hourPlus.addEventListener('click', () => {
      if (hours < MAX_HOURS){ hours++; hoursValueEl.textContent = hours; updateCalculator(); }
    });
    updateCalculator();
  }

  // ---- Передаємо параметри калькулятора у форму заявки ----
  const calcSubmit = document.getElementById('calcSubmit');
  const commentField = document.getElementById('comment');
  const calcSummaryNote = document.getElementById('calcSummaryNote');
  if (calcSubmit) {
    calcSubmit.addEventListener('click', (e) => {
      const qty = Number(headphoneRange.value);
      const price = calcPrice(qty);
      const opts = [];
      if (outsideKyiv.checked) opts.push(I18N.calc.outside);
      if (contentReel.checked) opts.push(I18N.calc.reel);
      if (smokeLight.checked) opts.push(I18N.calc.smoke);
      const optsText = opts.length ? I18N.calc.opts(opts) : '';
      const qtyLabel = qty >= MAX_QTY ? `${MAX_QTY}+` : qty;
      const summary = I18N.calc.summary(qtyLabel, hours, optsText, fmt.format(price.total));

      if (commentField) {
        commentField.value = commentField.value
          ? commentField.value + '\n\n' + summary
          : summary;
      }
      syncGuestSelect(qty);

      if (calcSummaryNote) {
        calcSummaryNote.style.display = 'block';
        calcSummaryNote.innerHTML = I18N.calc.note(qtyLabel, hours, fmt.format(price.total));
      }
    });
  }

  // ---- Стрічки: кеш наперед і вікно живих картинок ----
  //
  // Нескінченні стрічки тримають у DOM кілька копій набору: 130 карток сценаріїв
  // і 72 плитки атмосфери. Якщо в кожної стоїть src, браузер тримає в пам'яті
  // декодовані бітмапи всіх — це близько 223 МБ, і мобільний Safari просто вбиває
  // вкладку («сталася повторна проблема», чорний екран).
  //
  // Тому картинка живе тільки поки вона поруч із видимою частиною стрічки. Адреса
  // зберігається в data-src, а src ставиться й знімається на льоту. Під зображенням
  // лишається його ж крихітний відбиток (--lqip), тож порожніх плям не видно.
  // Файли при цьому вже лежать у HTTP-кеші — їх прогріває fetch, який нічого не
  // декодує й не займає пам'яті під бітмапи.

  function warmStripCache(section, list, done){
    if (!section) return;
    const run = () => {
      // Список можна передати явно: у віртуалізованій стрічці більшості картинок
      // у DOM просто немає, тож зібрати їх звідти не вийде.
      const urls = list || [...new Set([...section.querySelectorAll('img')]
        .map(i => i.dataset.src || i.getAttribute('src'))
        .filter(u => u && u.slice(0, 5) !== 'data:'))];
      if (!urls.length) { done && done(); return; }
      let left = urls.length;
      const tick = () => { if (--left === 0 && done) done(); };
      urls.forEach(u => fetch(u, { cache: 'force-cache', priority: 'low' })
        .then(tick, tick));
    };
    if (!('IntersectionObserver' in window)) { run(); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some(e => e.isIntersecting)) { io.disconnect(); run(); }
    }, { rootMargin: '2200px 0px' });   // почати задовго до того, як блок доїде
    io.observe(section);
  }

  // Обидві стрічки віртуалізовані по горизонталі, але про вертикаль не знали
  // нічого: їхня ініціалізація підставляла src у картки одразу на старті, хоча
  // самі секції лежать за сім-вісім екранів униз. Через це 57 файлів (~1.5 МБ)
  // тягнулись у першу ж секунду й відбирали смугу в hero. Тепер запуск чекає
  // на наближення секції — тим самим спостерігачем, що вже прогріває кеш вище.
  // Сама логіка вікна й віртуалізації не змінюється, зсувається лише момент.
  function whenNear(section, fn, margin){
    if (!section || !('IntersectionObserver' in window)) { fn(); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some(e => e.isIntersecting)) { io.disconnect(); fn(); }
    }, { rootMargin: margin || '2200px 0px' });
    io.observe(section);
  }

  // Прозорий піксель замість зняття src: <img> без адреси малює іконку
  // «зображення не завантажилось» і текст alt, а з цим — нічого. Усі копії
  // ділять один і той самий декодований піксель, тож пам'яті це не коштує.
  const BLANK = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';

  function makeImageWindow(strip){
    const imgs = [...strip.querySelectorAll('img')];
    imgs.forEach(img => {
      const src = img.getAttribute('src');
      if (src && src !== BLANK) { img.dataset.src = src; img.setAttribute('src', BLANK); }
      img.loading = 'eager';
    });

    // Позиції міряємо один раз: під час прокрутки порівнюємо лише числа, інакше
    // 200 викликів getBoundingClientRect на кожен кадр з'їдять увесь бюджет.
    let pos = [];
    const measure = () => {
      // Координати рахуємо від початку вмісту стрічки, а не від краю екрана:
      // до різниці з рамкою контейнера треба додати поточний scrollLeft, інакше
      // scrollLeft скорочується і позиції виходять відносні — вікно порівнює
      // їх не з тим і не вмикає жодної картинки.
      const edge = strip.getBoundingClientRect().left;
      const sl = strip.scrollLeft;
      pos = imgs.map(img => {
        const r = img.getBoundingClientRect();
        return [r.left - edge + sl, r.right - edge + sl];
      });
    };

    let queued = false;
    const apply = () => {
      queued = false;
      if (!pos.length) return;
      // Два екрани запасу в кожен бік: одного мало — при швидкому свайпі картка
      // встигала в'їхати в кадр раніше, ніж її зображення декодувалось, і мигала
      // розмитим відбитком. Живих картинок при цьому все одно двадцятки, а не
      // дві сотні, тож пам'ять лишається в межах десятків мегабайтів.
      // Стеля потрібна для широких моніторів: без неї запас росте разом із
      // шириною стрічки, і на full-bleed десктопі живих картинок стає під сотню.
      const reach = Math.min(strip.clientWidth * 3, 3200);
      const from = strip.scrollLeft - reach;
      const to = strip.scrollLeft + strip.clientWidth + reach;
      for (let i = 0; i < imgs.length; i++) {
        const img = imgs[i], p = pos[i];
        const near = p[1] > from && p[0] < to;
        const live = img.getAttribute('src') !== BLANK;
        if (near) { if (!live) img.setAttribute('src', img.dataset.src); }
        else if (live) img.setAttribute('src', BLANK);
      }
    };
    const sync = () => { if (!queued) { queued = true; requestAnimationFrame(apply); } };

    strip.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', () => { measure(); sync(); }, { passive: true });
    return { measure, sync };
  }

  // ---- Нескінченні стрічки: перенос лише на спокої ----
  // Раніше перенос усередину циклу робився на кожній події прокрутки. На дотику
  // це й давало «стіну»: запис у scrollLeft посеред інерційного розгону скасовує
  // саму інерцію, стрічка різко спиняється, і докрутити її можна лише наступним
  // свайпом. Тому перенос тепер чекає, поки прокрутка вгамується, а щоб довгий
  // кидок не встиг долетіти до справжнього краю, копій стало більше — скільки
  // саме, рахує TARGET_SLACK нижче. Інерцію рахує сам браузер — вона рідна для
  // платформи й гальмує саме так, як очікує палець.
  // Запас, який має лишатись у кожен бік: приблизно стільки долітає найсильніший
  // кидок пальцем у вузькій стрічці на телефоні.
  const TARGET_SLACK = 6500;
  // Зона біля справжнього краю, у якій перенос робиться негайно. Раніше вона
  // дорівнювала пів копії — у фотогалереї з її короткою копією це з'їдало більшу
  // частину запасу, і сильний свайп щоразу впирався в неї посеред інерції.
  const EDGE_GUARD = 420;
  function idleNormaliser(el, copyWidth, copies, isBusy){
    let t = 0;
    const guard = () => {
      const w = copyWidth();
      if (!w) return;
      const max = el.scrollWidth - el.clientWidth;
      if (el.scrollLeft < EDGE_GUARD) el.scrollLeft += w * 2;
      else if (el.scrollLeft > max - EDGE_GUARD) el.scrollLeft -= w * 2;
    };
    const settle = () => {
      if (isBusy && isBusy()) return;
      const w = copyWidth();
      if (!w) return;
      const mid = Math.floor(copies() / 2) * w;
      const drift = Math.round((el.scrollLeft - mid) / w);
      if (drift) el.scrollLeft -= drift * w;
    };
    return () => { guard(); clearTimeout(t); t = setTimeout(settle, 140); };
  }

  // ---- Atmosphere strip: endless loop + arrows ----
  // Та сама механіка, що й у стрічці сценаріїв: три копії набору, а scrollLeft
  // тримається всередині середньої. Кінця не існує, тож немає і жорсткого краю,
  // об який раніше різко обривалася стрічка.
  (function(){
    const grid = document.getElementById('galGrid');
    if (!grid) return;
    const prev = document.querySelector('.gal-prev');
    const next = document.querySelector('.gal-next');

    const originals = [...grid.children];
    const addCopy = () => originals.forEach(el => grid.appendChild(el.cloneNode(true)));

    // Ширину однієї копії міряємо по факту: у grid із dense-упаковкою рахувати
    // її з розмірів карток ненадійно, а різниця позицій — точна.
    const copyWidth = () => {
      const n = originals.length;
      const first = grid.children[0], second = grid.children[n];
      if (!first || !second) return 0;
      return second.getBoundingClientRect().left - first.getBoundingClientRect().left;
    };

    // Копія тут коротка (мозаїка з восьми кадрів), тож фіксованих п'яти копій
    // не вистачало: сильний свайп долітав до краю. Рахуємо потрібну кількість
    // від фактичної ширини копії — стільки, щоб запас у кожен бік був не менший
    // за TARGET_SLACK. Число копій непарне, щоб старт був рівно посередині.
    // Клонування відкладене до наближення секції: копії створюються через
    // cloneNode, а програмно вставлений <img> не проходить ту саму ліниву
    // перевірку, що й розпарсений з розмітки — усі 31 кадр стрічки летіли по
    // мережі в першу ж секунду, хоча сама галерея за сім екранів униз.
    // Кількість копій читається лениво (через колбеки), тож до клонування
    // стрічка просто лишається однією статичною копією.
    let copies = 1;
    const cloneStrip = () => {
      addCopy();
      copies = 2;
      const w0 = copyWidth() || 1;
      const want = Math.min(15, Math.max(5, 2 * Math.ceil(TARGET_SLACK / w0) + 1));
      while (copies < want) { addCopy(); copies++; }
    };

    let held = 0;                       // палець на стрічці — переносити не можна
    const normalise = idleNormaliser(grid, copyWidth, () => copies, () => held);
    function start(){
      const w = copyWidth();
      if (w) grid.scrollLeft = w * Math.floor(copies / 2);
    }

    const step = () => Math.max(grid.clientWidth * 0.7, 260);
    function nudge(dir){ grid.scrollBy({ left: dir * step(), behavior: 'smooth' }); }
    if (prev) prev.addEventListener('click', () => nudge(-1));
    if (next) next.addEventListener('click', () => nudge(1));

    grid.addEventListener('pointerdown', () => { held = 1; }, { passive: true });
    ['pointerup','pointercancel','touchend','touchcancel'].forEach(ev =>
      window.addEventListener(ev, () => { held = 0; }, { passive: true }));
    grid.addEventListener('scroll', normalise, { passive: true });
    // Тільки на зміну ШИРИНИ. На телефоні вертикальна прокрутка ховає й показує
    // адресний рядок, і кожен такий рух кидає resize — а start() ставить
    // scrollLeft на середину, тобто стрічка стрибала на перший кадр щоразу,
    // щойно користувач гортав сторінку вниз.
    let lastW = window.innerWidth;
    window.addEventListener('resize', () => {
      if (window.innerWidth === lastW) return;
      lastW = window.innerWidth;
      start();
    }, { passive: true });

    // Позицію переставляємо лише поки користувач стрічки не торкався: інакше
    // відкладений start() смикає її просто під пальцем.
    let touched = false;
    ['pointerdown','touchstart','wheel','keydown'].forEach(ev =>
      grid.addEventListener(ev, () => { touched = true; }, { passive: true }));
    const safeStart = () => { if (!touched) start(); };

    // win створюється лише коли секція наблизилась, тож зовнішні обробники
    // мусять переживати стан «ще не створено» — до того моменту стрічка просто
    // стоїть статичною розміткою з рідним loading="lazy".
    let win = null;
    const section = document.getElementById('atmosphere');
    whenNear(section, () => {
      cloneStrip();
      win = makeImageWindow(grid);
      start();
      win.measure(); win.sync();
      grid.addEventListener('scroll', win.sync, { passive: true });
    });
    warmStripCache(section, null, () => { safeStart(); if (win) win.sync(); });
    window.addEventListener('load', () => { safeStart(); if (win) { win.measure(); win.sync(); } });
  })();

  // ---- Сценарії: віртуалізована нескінченна стрічка ----
  //
  // Нескінченність раніше давалось дублюванням: 26 сценаріїв × 5 копій = 130
  // карток у DOM. У кожної картки два шари backdrop-filter — сама картка й хвіст
  // розмиття під фото, — тобто 260 окремих поверхонь, які компонувальник мусить
  // знімати й розмивати щокадру. Мобільний Safari цього не витримує і вбиває
  // вкладку («сталася повторна проблема»), причому ще до того, як діло доходить
  // до ваги зображень.
  //
  // Тепер у DOM живе рівно стільки карток, скільки вміщається на екрані плюс
  // невеликий запас. Картки переставні: під час прокрутки їм міняють позицію й
  // вміст. Нескінченність дає не дублювання, а арифметика — номер слота за
  // модулем кількості сценаріїв. Прокрутка лишається рідною, з інерцією
  // платформи: ширину стрічці задає одна порожня розпірка.
  (function(){
    const view = document.getElementById('ucGrid');
    if (!view) return;
    const rowEls = [...view.querySelectorAll('.uc-row')];
    if (!rowEls.length) return;
    const prev = document.querySelector('.uc-prev');
    const next = document.querySelector('.uc-next');

    const PERIODS = 21;                 // скільки повних наборів має розпірка
    const MID = Math.floor(PERIODS / 2);

    // Вміст знімаємо з розмітки: вона лишається джерелом правди й показує всі
    // сценарії навіть якщо скрипт не виконався.
    const rows = rowEls.map((el, ri) => ({
      el, ri,
      // Розбираємо картку на поля, а не зберігаємо розмітку рядком: перестановка
      // тоді оновлює три текстові вузли й одну адресу замість того, щоб щоразу
      // будувати піддерево наново.
      items: [...el.querySelectorAll('.uc-card')].map(c => {
        const img = c.querySelector('img');
        const h3 = c.querySelector('h3');
        const par = c.querySelector('.uc-body p');
        return {
          name: c.dataset.uc || '',
          title: h3 ? h3.textContent : '',
          text: par ? par.textContent : '',
          src: img ? img.getAttribute('src') : null,
          lqip: img ? img.style.getPropertyValue('--lqip') : '',
          alt: img ? img.getAttribute('alt') : '',
          cats: c.dataset.cats || ''
        };
      }),
      offset: ri === 1 ? 0.5 : 0,       // нижній ряд зсунутий на пів картки
      pool: [], slot: []
    })).filter(r => r.items.length);
    if (!rows.length) return;

    const urls = [...new Set(rows.flatMap(r => r.items.map(i => i.src)).filter(Boolean))];
    let step = 0, period = 0, poolSize = 0, BUFFER = 12;

    function metrics(){
      const cs = getComputedStyle(view.closest('.uc-gallery') || view);
      return [parseFloat(cs.getPropertyValue('--uc-col')) || 272,
              parseFloat(cs.getPropertyValue('--uc-gap')) || 14];
    }

    // У потоці картки вирівнював flex-stretch по найвищій. В абсолютній розкладці
    // висоту треба знати наперед, тож міряємо найвищий варіант тексту один раз.
    const SKELETON =
      '<div class="uc-media"><img width="544" height="306" decoding="async" alt=""></div>' +
      '<div class="uc-body"><h3></h3><p></p>' +
      '<button type="button" class="uc-order">' + I18N.uc.order + '</button></div>';

    function makeCard(col, h){
      const c = document.createElement('article');
      c.className = 'uc-card';
      c.style.cssText = 'position:absolute;top:0;width:' + col + 'px' + (h ? ';height:' + h + 'px' : '');
      c.innerHTML = SKELETON;
      c._img = c.querySelector('img');
      c._h3 = c.querySelector('h3');
      c._p = c.querySelector('.uc-body p');
      c._media = c.querySelector('.uc-media');
      return c;
    }

    function tallest(r, col){
      const probe = makeCard(col, 0);
      probe.style.cssText += ';visibility:hidden;pointer-events:none;left:0';
      r.el.appendChild(probe);
      let h = 0;
      r.items.forEach(it => {
        probe._h3.textContent = it.title;
        probe._p.textContent = it.text;
        h = Math.max(h, probe.offsetHeight);
      });
      probe.remove();
      return h;
    }

    function build(){
      const [col, gap] = metrics();
      step = col + gap;
      period = rows[0].items.length * step;
      // Запас по 12 карток у кожен бік (≈2900px на телефоні) — більше, ніж
      // проходить один сильний кидок пальцем. Тепер це по кишені: без
      // backdrop-filter картка коштує звичайного малювання, а не знімка фону.
      BUFFER = 12;
      poolSize = Math.ceil(view.clientWidth / step) + BUFFER * 2;
      rows.forEach(r => {
        r.el.textContent = '';
        r.el.style.position = 'relative';
        r.el.style.paddingLeft = '0';
        const h = tallest(r, col);
        r.el.style.height = h + 'px';

        const track = document.createElement('div');
        track.style.cssText = 'height:1px;pointer-events:none;width:' + (r.items.length * PERIODS * step) + 'px';
        r.el.appendChild(track);

        r.pool = []; r.slot = [];
        for (let i = 0; i < poolSize; i++){
          const c = makeCard(col, h);
          r.el.appendChild(c);
          r.pool.push(c); r.slot.push(NaN);
        }
      });
    }

    // Запит на перемальовування летить через requestAnimationFrame, тож
    // клік на тему може прийти між плануванням і виконанням: у момент
    // виклику пул уже спорожнений buildSimple(), а fill() усе ще тягне його
    // за старою адресою. Прапорець ловить саме цей проміжок.
    let virtualized = true;
    function fill(){
      if (!virtualized) return;
      const from = Math.floor(view.scrollLeft / step) - BUFFER;
      for (const r of rows){
        const n = r.items.length;
        for (let s = from; s < from + poolSize; s++){
          // слот завжди лягає в ту саму картку пулу, тож при зсуві на крок
          // перемальовується одна картка, а не весь ряд
          const i = ((s % poolSize) + poolSize) % poolSize;
          if (r.slot[i] === s) continue;
          r.slot[i] = s;
          const it = r.items[((s % n) + n) % n];
          const c = r.pool[i];
          if (c.dataset.uc !== it.name){
            // Пул переставний: той самий вузол DOM за мить показує зовсім
            // інший сценарій. Тап-підсвітка тримається на класі, а не на
            // ідентичності картки, тож без цього скидання вона «перестрибувала»
            // на нову картку, яка щойно посіла місце підсвіченої.
            c.classList.remove('is-lit');
            c.dataset.uc = it.name;
            c._h3.textContent = it.title;
            c._p.textContent = it.text;
            // --lqip ставимо на .uc-media: звідти його бачить і сам <img>, і хвіст
            // розмиття в ::after
            if (it.lqip) c._media.style.setProperty('--lqip', it.lqip);
            if (it.src && c._img.getAttribute('src') !== it.src){
              c._img.setAttribute('src', it.src);
              c._img.setAttribute('alt', it.alt || it.name);
              c._img.loading = 'eager';
              c._img.fetchPriority = 'high';
            }
          }
          c.style.left = ((s + r.offset) * step) + 'px';
        }
      }
    }

    let queued = false;
    const sync = () => { if (!queued){ queued = true; requestAnimationFrame(() => { queued = false; fill(); }); } };

    let held = 0;
    const normalise = idleNormaliser(view, () => period, () => PERIODS, () => held);
    // virtualized: у режимі теми (фільтр нижче) петлі немає, і scrollLeft
    // посеред неіснуючої доріжки закинув би короткий ряд у самий кінець.
    const start = () => { if (period && virtualized) { view.scrollLeft = MID * period; fill(); } };

    view.addEventListener('pointerdown', () => { held = 1; }, { passive: true });
    ['pointerup','pointercancel','touchend','touchcancel'].forEach(ev =>
      window.addEventListener(ev, () => { held = 0; }, { passive: true }));
    // normalise() підтримує ілюзію нескінченної петлі: коли scrollLeft
    // підходить до краю, він перестрибує на period — величину, пораховану
    // під усі 43 картки. У простому режимі теми (buildSimple) така петля не
    // існує: рядок короткий, period лишається старим і набагато більшим за
    // реальну прокрутку. Перший же скрол після перемикання теми читався як
    // «біля краю» (scrollLeft стартує з 0, поріг EDGE_GUARD — 420px) і
    // guard() додавав старий period — стрічку жбурляло в сам кінець.
    view.addEventListener('scroll', () => { if (virtualized) normalise(); sync(); }, { passive: true });

    let touched = false;
    ['pointerdown','touchstart','wheel','keydown'].forEach(ev =>
      view.addEventListener(ev, () => { touched = true; }, { passive: true }));

    // step рахує build(), а build() тепер лінивий (whenNear чекає наближення
    // секції) — клік по стрілці чи темі до того, як користувач доскролив,
    // заставав step на початковому 0, і стрілка мовчки нікуди не гортала.
    // metrics() важить копійки, тож рахуємо крок напряму, коли build() ще
    // не встиг.
    function nudge(dir){ view.scrollBy({ left: dir * (step || metrics().reduce((a,b)=>a+b)) * 2, behavior: 'smooth' }); }
    if (prev) prev.addEventListener('click', () => nudge(-1));
    if (next) next.addEventListener('click', () => nudge(1));

    // картки переставні, тож кнопки замовлення ловимо делегуванням
    view.addEventListener('click', (e) => {
      const btn = e.target.closest('.uc-order');
      if (!btn) return;
      const card = btn.closest('.uc-card');
      const name = card && card.dataset.uc;
      if (name) orderExperience(name);
    });

    // ---- Паралакс між рядами ----
    // Ряди пливуть у різні боки, поки секція йде через екран. Суто візуально:
    // трансформи не чіпають scrollLeft, тож на арифметику слотів не впливають.
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce && rows.length > 1){
      const DRIFT = 46;
      let ticking = false;
      function drift(){
        // Обрано тему — ряди короткі й мусять стояти рівно від початку, на
        // одній вертикалі з текстом над ними; зсув паралаксу її б ламав.
        if (!virtualized){
          rows.forEach(r => { r.el.style.transform = ''; });
          ticking = false; return;
        }
        const r = view.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight){ ticking = false; return; }
        const p = 1 - (r.top + r.height / 2) / (innerHeight / 2 + r.height / 2);
        const clamped = Math.max(-1, Math.min(1, p));
        rows[0].el.style.transform = `translate3d(${(-clamped * DRIFT).toFixed(1)}px,0,0)`;
        rows[1].el.style.transform = `translate3d(${(clamped * DRIFT).toFixed(1)}px,0,0)`;
        ticking = false;
      }
      const onScroll = () => { if (!ticking){ ticking = true; requestAnimationFrame(drift); } };
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      drift();
    }

    // Перебудовуємось лише коли змінилась ширина. На телефоні поява й ховання
    // адресного рядка під час звичайної прокрутки сторінки міняє висоту і теж
    // кидає `resize` — а перебудова скидає scrollLeft на середину, і стрічка
    // на очах перескакувала на початок. Саме це й ловилось як «прокручую сайт
    // далі, а слайдер стрибає назад».
    let rt = 0, lastW = 0, lastCol = 0;
    const remember = () => { lastW = view.clientWidth; lastCol = metrics()[0]; };
    // Один вхід у побудову на всі виклики: до наближення секції lastW/lastCol
    // ще нульові, тож будь-який resize (на телефоні його кидає навіть поява
    // адресного рядка) пройшов би повз перевірку ширини й побудував стрічку
    // достроково — а потім спостерігач побудував би її вдруге.
    let booted = false;
    // Якщо тему обрали раніше, ніж секція підійшла до екрана, пул не
    // будуємо: він стер би картки теми. Повернення на «Усі» збудує його саме.
    const boot = () => { if (booted) return; booted = true; if (!virtualized) return; build(); start(); remember(); };
    window.addEventListener('resize', () => {
      if (!booted) return;                 // ще нема чого перебудовувати
      if (!virtualized) return;            // ряди теми — звичайний потік, перебудова не потрібна
      if (view.clientWidth === lastW && metrics()[0] === lastCol) return;
      clearTimeout(rt);
      rt = setTimeout(() => { build(); start(); remember(); }, 200);
    }, { passive: true });

    // Секція, а не жорстке id="cases": на головній стрічка живе в #cases, на
    // сторінці досвіду — в #more. Раніше guard шукав саме #cases, і на іншій
    // сторінці whenNear(null, ...) вважав це «елемента нема, запускай одразу»
    // — стрічка з сорока з гаком картками будувалась і тягла зображення eager
    // просто при завантаженні, хоч сама секція стоїть нижче середини сторінки.
    const stripSection = view.closest('section');
    whenNear(stripSection, boot);
    // start() усередині захищений `if (period)`, тож до побудови він тихо
    // нічого не робить — колбек прогріву кешу лишається безпечним.
    warmStripCache(stripSection, urls, () => { if (!touched) start(); });

    // ---- Фільтр тем над стрічкою (лише де є панель) ----
    // На «Усі» стрічка лишається тим самим нескінченним пулом, що й досі:
    // build()/fill() вище цього не знають і не мають знати. Обраної теми
    // пул не витримує чесно — там лишається 3-5 карток, і подвоєння такої
    // жмені на всю ширину «нескінченної» доріжки миттю видало б повтор.
    // Тому для теми ряд перемальовується один раз звичайними картками у
    // потоці, без пулу й без петлі: рівно стільки елементів, скільки в темі
    // є, прокрутка лишається рідною.
    (function(){
      const filterBar = stripSection && stripSection.querySelector('.exp-filter');
      if (!filterBar) return;
      const chips = [...filterBar.querySelectorAll('.exp-chip')];
      const countEl = stripSection.querySelector('.exp-count');
      const galleryEl = view.closest('.uc-gallery');
      if (!chips.length) return;

      // Той самий відмінок, що на сторінці-списку — форма слова від числа.
      function word(n){
        const t = n % 100, o = n % 10;
        if (t > 10 && t < 20) return 'форматів';
        if (o === 1) return 'формат';
        if (o >= 2 && o <= 4) return 'формати';
        return 'форматів';
      }

      // Англійська головна має власний рядок у I18N; українські сторінки —
      // відмінювання вище.
      const countText = n => (I18N.uc && I18N.uc.count)
        ? I18N.uc.count(n) : n + ' ' + word(n) + ' у цій темі';

      let simple = false; // чи ряди зараз у звичайному, нефільтрованому режимі
      // Рядів може бути кілька: на корпоративах один, на головній два. Спільний
      // список — у порядку популярності. На головній ряди чергуються (зверху
      // 1, 3, 5…, знизу 2, 4, 6…), тож склеюємо їх назад через одну; для
      // одного ряду це просто його порядок.
      const master = [];
      const longest = Math.max(...rows.map(r => r.items.length));
      for (let k = 0; k < longest; k++) rows.forEach(r => { if (r.items[k]) master.push(r.items[k]); });
      // Картки будуються один раз persistant-набором (а не пересотворюються
      // на кожен клік, як раніше) — інакше FLIP нема чим ловити: браузер не
      // може плавно перевіршувати елемент, якого щойно не існувало. Той
      // самий підхід, що на сторінці-каталозі «Тихі враження».
      let simpleCards = null;
      const leaveTimers = new Map();

      function clearLeaveStyles(c){
        c.style.position = ''; c.style.left = ''; c.style.top = ''; c.style.width = '';
      }

      function ensureSimpleCards(){
        if (simpleCards) return;
        // paddingLeft = '' повертає CSS-зсув нижнього ряду на пів картки
        // (у пулі його замінював r.offset) — «шахівниця» лишається і в темі.
        rows.forEach(r => {
          r.el.textContent = '';
          r.el.style.position = 'relative';
          r.el.style.paddingLeft = '';
          r.el.style.height = '';
          r.el.style.transform = '';
          r.pool = []; r.slot = [];
        });
        simpleCards = master.map(it => {
          const c = document.createElement('article');
          c.className = 'uc-card';
          c.dataset.uc = it.name;
          c.dataset.cats = it.cats;
          c.hidden = true;
          c.innerHTML = SKELETON;
          c.querySelector('h3').textContent = it.title;
          c.querySelector('.uc-body p').textContent = it.text;
          const media = c.querySelector('.uc-media');
          if (it.lqip) media.style.setProperty('--lqip', it.lqip);
          const img = c.querySelector('img');
          if (it.src){
            img.setAttribute('src', it.src);
            img.setAttribute('alt', it.alt || it.name);
            img.loading = 'lazy';
          }
          rows[0].el.appendChild(c);
          return c;
        });
      }

      // FLIP — той самий прийом, що на сторінці-каталозі: картка, що
      // лишається видимою, не стрибає на нове місце, а плавно туди їде.
      function flip(before){
        simpleCards.forEach(c => {
          if (c.hidden || c.classList.contains('is-leaving')) return;
          const first = before.get(c);
          if (!first) return;
          const last = c.getBoundingClientRect();
          const dx = first.left - last.left, dy = first.top - last.top;
          if (Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5) return;
          c.style.transition = 'none';
          c.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
          void c.offsetWidth;
          c.style.transition = 'transform .34s var(--ease-arrive)';
          c.style.transform = '';
          clearTimeout(c._flipCleanup);
          c._flipCleanup = setTimeout(() => { c.style.transition = ''; }, 380);
        });
      }

      function applyCat(cat){
        ensureSimpleCards();
        const before = new Map();
        simpleCards.forEach(c => { if (!c.hidden) before.set(c, c.getBoundingClientRect()); });
        // Картку, що йде, тримаємо на місці відносно ТОГО ряду, де вона стоїть.
        const rowBefore = new Map(rows.map(r => [r.el, r.el.getBoundingClientRect()]));

        let shown = 0, i = 0;
        simpleCards.forEach(c => {
          const on = (c.dataset.cats || '').split(' ').indexOf(cat) !== -1;
          if (on){
            // Розкладка по рядах через одну, у порядку популярності. appendChild
            // переносить наявний вузол, тож картка, що лишається, може
            // перейти в інший ряд — FLIP нижче доведе її туди плавно.
            rows[shown % rows.length].el.appendChild(c);
            shown++;
          }

          const pending = leaveTimers.get(c);
          if (pending){ clearTimeout(pending); leaveTimers.delete(c); }

          if (on){
            const wasHidden = c.hidden;
            c.hidden = false;
            c.classList.remove('is-leaving');
            clearLeaveStyles(c);
            if (wasHidden){
              c.style.setProperty('--stagger', i++);
              c.classList.add('is-entering');
              clearTimeout(c._enterCleanup);
              c._enterCleanup = setTimeout(() => c.classList.remove('is-entering'), 400);
            }
          } else if (!c.hidden){
            const r = before.get(c);
            const gridBefore = rowBefore.get(c.parentNode);
            c.style.position = 'absolute';
            c.style.left = (r.left - gridBefore.left) + 'px';
            c.style.top = (r.top - gridBefore.top) + 'px';
            c.style.width = r.width + 'px';
            c.classList.add('is-leaving');
            // Тап-підсвітка не мусить пережити тему, у якій її поставили:
            // інакше картка, що ховається зараз, наступного разу вигулькне
            // під іншою темою вже «активною» без жодного тапу по ній.
            c.classList.remove('is-lit');
            const t = setTimeout(() => {
              c.hidden = true;
              c.classList.remove('is-leaving');
              clearLeaveStyles(c);
              leaveTimers.delete(c);
            }, 180);
            leaveTimers.set(c, t);
          }
        });
        flip(before);
        // Нова тема завжди починається з початку ряду — саме там він рівний
        // з текстом над стрічкою, і саме це мало бути видно одразу.
        view.scrollLeft = 0;
        return shown;
      }

      // Перший перехід із нескінченного пулу в простий режим одноразово чистить
      // rows[0].el (сотні px фіксованої висоти зникають) — і саме на цьому кадрі
      // Chrome/Safari іноді самі підкручують scrollY, «компенсуючи» зниклий
      // вузол, який вважали якорем прокрутки. overflow-anchor: none на самих
      // контейнерах це не завжди ловить (вузол-якір міг бути карткою всередині,
      // яку ми щойно видалили), тож тут просто силоміць повертаємо позицію, яку
      // мав документ до кліку — після кадру, яким браузер встиг її підкрутити.
      function holdScroll(fn){
        const y = window.scrollY;
        fn();
        // behavior:'instant' обов'язково: на <html> стоїть scroll-behavior:
        // smooth, і scrollTo(0, y) не повертав позицію, а плавно їхав до неї —
        // сторінку помітно відкидало після кліку по темі.
        requestAnimationFrame(() => {
          if (window.scrollY !== y) window.scrollTo({ top: y, left: 0, behavior: 'instant' });
        });
      }

      function apply(cat){
        chips.forEach(ch => {
          const on = ch.dataset.cat === cat;
          ch.classList.toggle('is-on', on);
          ch.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        if (cat === 'all'){
          if (simple){
            holdScroll(() => {
              simple = false;
              simpleCards = null;
              leaveTimers.forEach(t => clearTimeout(t));
              leaveTimers.clear();
              virtualized = true; build(); start();
            });
          }
          if (countEl) countEl.textContent = '';
          if (galleryEl) galleryEl.classList.remove('is-simple');
          return;
        }
        simple = true;
        virtualized = false;
        if (galleryEl) galleryEl.classList.add('is-simple');
        let shown = 0;
        holdScroll(() => { shown = applyCat(cat); });
        if (countEl) countEl.textContent = countText(shown);
      }

      filterBar.addEventListener('click', (e) => {
        const chip = e.target.closest('.exp-chip');
        if (chip){ apply(chip.dataset.cat); centerChip(filterBar, chip); }
      });
    })();
  })();

  // На телефоні фільтр тем — одна стрічка з прогортанням (site.css, пошук за
  // «одна стрічка»). Обрана кнопка може стояти за краєм, тож після кліку
  // прокручуємо саму стрічку так, щоб кнопка стала в центр. Не scrollIntoView:
  // той заодно рухав би й сторінку по вертикалі. Там, де стрічка не
  // прокручується (кнопки переносяться в рядки), нічого не робимо.
  function centerChip(bar, chip){
    if (!bar || !chip || bar.scrollWidth <= bar.clientWidth) return;
    const br = bar.getBoundingClientRect(), cr = chip.getBoundingClientRect();
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    bar.scrollTo({
      left: bar.scrollLeft + (cr.left - br.left) - (br.width - cr.width) / 2,
      behavior: reduce ? 'instant' : 'smooth'
    });
  }

  // ---- Плашки «Що входить»: підсвітка за прокруткою ----
  // Підсвітка, що йде за прокруткою: активним стає той елемент групи, який
  // найближчий до середини екрана; проходить — гасне, засвічується наступний.
  // Курсор має пріоритет: доки миша в блоці, світиться лише те, на чому вона
  // стоїть, інакше світилися б два елементи одночасно.
  function litOnScroll(box, sel, opts){
    if (!box) return null;
    const items = [...box.querySelectorAll(sel)];
    if (!items.length) return null;
    const o = opts || {};
    let ticking = false, lit = null, hovering = false, manual = false;

    const clear = () => { if (lit){ lit.classList.remove('is-lit'); lit = null; } };

    // Дві моделі, бо геометрія різна.
    // 'nearest' — для вертикальної стопки: світиться те, що найближче до
    // середини екрана; елементи проходять її по черзі самі.
    // 'progress' — для ряду або сітки: там усі елементи перетинають середину
    // ОДНОЧАСНО, і «найближчий» світив би завжди один і той самий. Тому чергу
    // задає прогрес самого блока крізь екран.
    function nearest(){
      const mid = innerHeight * 0.45;
      let best = null, bestD = Infinity;
      for (const el of items){
        const r = el.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight) continue;
        const d = Math.abs(r.top + r.height / 2 - mid);
        if (d < bestD){ bestD = d; best = el; }
      }
      return best;
    }
    function byProgress(){
      const r = box.getBoundingClientRect();
      const from = innerHeight * 0.88;              // блок щойно виходить знизу
      const to = innerHeight * 0.28 - r.height;     // блок майже пішов угору
      if (from === to) return null;
      const p = (from - r.top) / (from - to);
      if (p < 0 || p > 1) return null;
      return items[Math.min(items.length - 1, Math.floor(p * items.length))];
    }

    function pick(){
      ticking = false;
      if (hovering || manual) return;
      // Бенто «Як це працює» попросили лишити тільки на дотик: на десктопі
      // підсвітка мигтіла по черзі просто від прокрутки коліщатком, без
      // жодної дії користувача, і це заважало, а не підказувало.
      if (o.touchOnly && !window.matchMedia('(hover: none)').matches){ clear(); return; }
      const best = o.mode === 'progress' ? byProgress() : nearest();
      if (best === lit) return;
      if (lit) lit.classList.remove('is-lit');
      if (best) best.classList.add('is-lit');
      lit = best;
    }
    const onScroll = () => { if (!ticking){ ticking = true; requestAnimationFrame(pick); } };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });

    // тільки миша: дотик не має вимикати прокруткову підсвітку
    box.addEventListener('pointerenter', (e) => {
      if (e.pointerType !== 'mouse') return;
      hovering = true; clear();
    });
    box.addEventListener('pointerleave', (e) => {
      if (e.pointerType !== 'mouse') return;
      hovering = false; pick();
    });

    // Дотик: тап фіксує саме цей елемент, автоматична підсвітка гасне. Потрібно
    // лише там, де з елемента щось розкривається (стопка плашок) — решті груп
    // фіксація ні до чого, там підсвітка суто декоративна.
    if (o.pinOnTap){
      box.addEventListener('click', (e) => {
        if (!window.matchMedia('(hover: none)').matches) return;
        const el = e.target.closest(sel);
        if (!el) return;
        manual = true;
        if (lit && lit !== el) lit.classList.remove('is-lit');
        el.classList.add('is-lit');
        lit = el;
      });
      document.addEventListener('click', (e) => {
        if (!manual || box.contains(e.target)) return;
        manual = false;
        clear();
        pick();
      });
    }

    pick();
    return { pick, clear };
  }

  // ---- Стопка плашок «Що входить»: безперервний фокус замість перемикача ----
  // Плашки лежать внахлист, і та, що найближча до середини екрана, підіймається,
  // а решта звільняє їй місце. Раніше це було перемикання класу: у момент, коли
  // «найближчою» ставала інша плашка, одна опускалась, інша піднімалась, а всі
  // наступні зсувались на 22px — п'ять карток стрибали одночасно, і CSS-перехід
  // лише розтягував цей стрибок. Відчувалось як ривок.
  //
  // Тепер це стан, що тече. Для кожної плашки рахується ЦІЛЬ фокусу t (0…1) —
  // гладка функція відстані її центра до лінії фокуса: 1 у центрі, 0 на відстані
  // кроку стопки, між ними smoothstep. Дві сусідні плашки на півдорозі дають
  // 0.5 + 0.5, тож «фокус» перетікає з однієї на іншу, а не стрибає. Видиме
  // значення f наздоганяє ціль за експонентою, залежною від ЧАСУ (не від кадрів):
  // на 60 і на 120 Гц інерція однакова, і навіть різке гортання не дає ривка —
  // картка встигає лише м'яко розганятись. --f веде підйом, світіння, рамку,
  // цифру й бейдж; --p (сума --f плашок над цією, не більше 1) — відступ сусідів
  // вниз: наступні звільняють місце рівно настільки, наскільки піднялась активна.
  // Уся візуальна логіка — у CSS (.slab, змінні --f/--p), тут лише числа.
  //
  // Джерела цілі: (1) прокрутка; (2) мишка — плашка під курсором стає ціллю
  // (курсор має пріоритет, доки він у стопці); (3) тап на дотиці фіксує плашку.
  // Позиції беремо з розкладки (offsetTop), а не з getBoundingClientRect самих
  // плашок: у них transform, і ціль від власного зсуву давала б зворотний зв'язок.
  (function(){
    const box = document.querySelector('.slabs');
    if (!box) return;
    const items = [].slice.call(box.querySelectorAll('.slab'));
    const n = items.length;
    if (n < 2) return;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const RATE = 5.5;                       // 1/с; ~180мс постійна часу — повільно, «дорого»
    const f = new Array(n).fill(0);         // те, що зараз на екрані
    const t = new Array(n).fill(0);         // до чого ведемо
    let ptrY = null, pin = -1, raf = 0, last = 0;
    let rel = [], mid = [], pitch = 1;

    function measure(){
      // Центри плашок відносно верху стопки за розкладкою (без transform).
      const top0 = items[0].offsetTop;
      rel = items.map(function(el){ return el.offsetTop - top0 + el.offsetHeight / 2; });
      pitch = Math.max(1, (rel[n - 1] - rel[0]) / (n - 1));
    }
    const smooth = function(x){ x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };

    function retarget(){
      if (pin >= 0){
        for (let i = 0; i < n; i++) t[i] = i === pin ? 1 : 0;
        return;
      }
      const r = box.getBoundingClientRect();
      const H = window.innerHeight;
      // Стопка поза екраном — жодна плашка не світиться.
      if (r.top > H * 0.98 || r.bottom < H * 0.02){ t.fill(0); return; }
      // Лінія фокуса: за замовчуванням трохи вище середини екрана, а поки курсор
      // у стопці — сам курсор. Та сама гладка функція, тож фокус їздить за
      // мишкою так само плавно, як за прокруткою, і перетікає між плашками.
      const focusY = ptrY !== null ? ptrY : H * 0.47;
      for (let i = 0; i < n; i++){
        const d = Math.abs(r.top + rel[i] - focusY);
        t[i] = smooth(1 - d / pitch);
      }
    }
    function paint(){
      let above = 0, top = -1, topV = 0.5;
      for (let i = 0; i < n; i++){
        const el = items[i];
        el.style.setProperty('--f', f[i].toFixed(4));
        el.style.setProperty('--p', Math.min(1, above).toFixed(4));
        above += f[i];
        if (f[i] > topV){ topV = f[i]; top = i; }
      }
      for (let i = 0; i < n; i++) items[i].classList.toggle('is-top', i === top);
    }
    function tick(now){
      raf = 0;
      const dt = Math.min(0.05, (now - last) / 1000) || 0.016;
      last = now;
      const a = reduce ? 1 : 1 - Math.exp(-RATE * dt);
      let moving = false;
      for (let i = 0; i < n; i++){
        const d = t[i] - f[i];
        if (Math.abs(d) < 0.0004){ f[i] = t[i]; continue; }
        f[i] += d * a; moving = true;
      }
      paint();
      if (moving) raf = requestAnimationFrame(tick);
    }
    function wake(){
      retarget();
      if (!raf){ last = performance.now(); raf = requestAnimationFrame(tick); }
    }

    measure();
    window.addEventListener('scroll', wake, { passive: true });
    window.addEventListener('resize', function(){ measure(); wake(); }, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ measure(); wake(); });
    window.addEventListener('load', function(){ measure(); wake(); });

    // Мишка: поки курсор у стопці, лінія фокуса — це він. Позицію курсора міряємо
    // по розкладці (rel/offsetTop), а не по тому, яка плашка зараз під ним: вони
    // рухаються, і «що під курсором» давало б зворотний зв'язок — плашка піднялась,
    // і під курсором уже сусідня. Так фокус не смикається, коли стопка їде під
    // нерухомим курсором (гортання коліщатком). Вийшов зі стопки — веде прокрутка.
    box.addEventListener('pointermove', function(e){
      if (e.pointerType !== 'mouse') return;
      ptrY = e.clientY; wake();
    });
    box.addEventListener('pointerleave', function(e){
      if (e.pointerType !== 'mouse') return;
      ptrY = null; wake();
    });

    // Дотик: тап фіксує плашку (з неї розкривається стопка), тап деінде знімає.
    box.addEventListener('click', function(e){
      if (!window.matchMedia('(hover: none)').matches) return;
      const el = e.target.closest('.slab');
      if (!el) return;
      pin = items.indexOf(el); wake();
    });
    document.addEventListener('click', function(e){
      if (pin < 0 || box.contains(e.target)) return;
      pin = -1; wake();
    });

    wake();
  })();
  litOnScroll(document.querySelector('.flow'), '.flow-step', { mode: 'progress' });
  litOnScroll(document.querySelector('.benefits-grid'), '.benefit-card', { mode: 'progress' });
  // «Як це працює»: той самий прийом, що в переваг — на дотик картки бенто
  // раніше не відповідали взагалі нічим, доки палець саме на них.
  litOnScroll(document.querySelector('.process-bento'), '.pb-card:not(.pb-card-accent)', { mode: 'progress', touchOnly: true });

  // ---- Стрічка сценаріїв: тап перемикає підсвітку картки ----
  // Спершу підсвітку прив'язали до прокрутки (яка картка по центру), але
  // власник це приміряв і захотів простішого: тап по картці фіксує обводку,
  // повторний тап по тій самій — знімає. Прокрутка сама по собі більше
  // нічого не підсвічує й не гасить. Delegation на .uc-grid: у
  // нескінченному пулі й у простому ряді обраної теми самі елементи-картки
  // час від часу підмінюються, слухач на контейнері переживає будь-яку з
  // цих підмін.
  document.querySelectorAll('.uc-grid').forEach((grid) => {
    grid.addEventListener('click', (e) => {
      if (!window.matchMedia('(hover: none)').matches) return;
      const card = e.target.closest('.uc-card');
      if (!card || !grid.contains(card)) return;
      const was = card.classList.contains('is-lit');
      const prev = grid.querySelector('.uc-card.is-lit');
      if (prev) prev.classList.remove('is-lit');
      if (!was) card.classList.add('is-lit');
    });
  });

  // ---- Стрічка відгуків: стрілки й активна картка ----
  (function(){
    const strip = document.getElementById('tstStrip');
    if (!strip) return;
    const prev = document.querySelector('.tst-prev');
    const next = document.querySelector('.tst-next');
    const cards = [...strip.querySelectorAll('.tst-card')];

    const step = () => Math.max(strip.clientWidth * 0.6, 280);
    if (prev) prev.addEventListener('click', () => strip.scrollBy({ left: -step(), behavior: 'smooth' }));
    if (next) next.addEventListener('click', () => strip.scrollBy({ left:  step(), behavior: 'smooth' }));

    function syncArrows(){
      const max = strip.scrollWidth - strip.clientWidth - 2;
      const atStart = strip.scrollLeft <= 2, atEnd = strip.scrollLeft >= max;
      if (prev){ prev.style.opacity = atStart ? '0' : '1'; prev.style.pointerEvents = atStart ? 'none' : 'auto'; }
      if (next){ next.style.opacity = atEnd ? '0' : '1'; next.style.pointerEvents = atEnd ? 'none' : 'auto'; }
    }

    // На дотику курсора немає, тож активною стає картка, найближча до середини
    // екрана: гортаєш — і вона сама виходить наперед.
    // Перевіряємо щоразу, а не один раз при завантаженні: інакше після зміни
    // розміру вікна прапорець лишається застарілим і клас .is-active висить на
    // десктопі, конфліктуючи з :hover.
    const mqTouch = window.matchMedia('(hover: none)');
    let cur = null, ticking = false;
    const drop = () => { if (cur){ cur.classList.remove('is-active'); cur = null; } };
    function pickCentre(){
      ticking = false;
      if (!mqTouch.matches){ drop(); return; }
      const mid = innerWidth / 2;
      let best = null, bestD = Infinity;
      for (const c of cards){
        const r = c.getBoundingClientRect();
        if (r.right < 0 || r.left > innerWidth) continue;
        const d = Math.abs(r.left + r.width / 2 - mid);
        if (d < bestD){ bestD = d; best = c; }
      }
      if (best === cur) return;
      if (cur) cur.classList.remove('is-active');
      if (best) best.classList.add('is-active');
      cur = best;
    }
    const queue = () => { if (!ticking){ ticking = true; requestAnimationFrame(pickCentre); } };

    // Щойно в стрічку заходить миша, активність передаємо :hover: інакше
    // підсвіченими були б одразу дві картки — центральна й та, під курсором.
    strip.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') drop(); });
    strip.addEventListener('pointermove', (e) => { if (e.pointerType === 'mouse') drop(); }, { passive: true });

    strip.addEventListener('scroll', () => { syncArrows(); queue(); }, { passive: true });
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', () => { syncArrows(); queue(); }, { passive: true });
    syncArrows(); pickCentre();
  })();

  // ---- Scroll reveal ----
  // Коли поява відіграла, з елемента знімається і затримка, і саме правило
  // появи (клас rv-done). Доти правило появи перебиває власний transition
  // елемента: у плашок «Що входить» наведення миттєво клацало рамкою й тінню
  // замість своїх 0.55s, а затримка черги (до 0.28s) тягнулася і на підйом
  // картки, через що він майже не встигав відіграти, поки курсор переходив
  // між плашками. Поява — разова річ і не має лишатися на елементі назавжди.
  const REVEAL_MS = 700;
  function settleReveal(el){
    const delay = (parseFloat(el.style.transitionDelay) || 0) * 1000;
    setTimeout(() => {
      el.style.transitionDelay = '';
      el.classList.add('rv-done');
    }, delay + REVEAL_MS + 60);
  }
  // GSAP-режим появи. Тригер лишається за IntersectionObserver, а не за
  // ScrollTrigger: якірний перехід із меню за один стрибок пролітає повз
  // кілька блоків, і IO спрацьовує на кожному, що потрапив у кадр, тоді як
  // тригер за позицією міг би так і не спрацювати для тих, що лишились вище
  // точки приземлення. GSAP лише малює сам рух, і робить те, чого CSS-перехід
  // не вміє: черга по групі одним потоком (картки, що прийшли в кадр разом,
  // ідуть по черзі), різний характер входу для заголовків і карток, розмиття
  // «наведення на різкість» для заголовків, як у героя.
  // Плашки «Що входить» (.slab) лишаються на старій появі: їхній рух
  // тримається на власному transform і підсвітці за прокруткою.
  // Без GSAP (не завантажився) і при prefers-reduced-motion працює стара поява.
  const gsapOn = !!(window.gsap && window.ScrollTrigger) &&
    !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gsQueue = [];
  let gsTimer = 0;
  function gsKind(el){
    if (el.matches('h2, .h2, .exp-head-title')) return 'head';
    if (el.matches('.eyebrow, .section-lead, .how-lead, .slabs-foot')) return 'text';
    if (el.matches('.benefit-card, .pb-card')) return 'benefit';
    if (el.matches('.pb-shot, .exp-story-shots')) return 'shots';
    if (el.matches('.faq-cats .faq-item')) return 'faq';
    if (el.matches('.faq-cats .faq-cat-head')) return 'cathead';
    return 'card';
  }
  // Картки «Досвіду гостя»: не просто виїзд, а невеличка вистава. Картка
  // піднімається знизу з легким нахилом «від глядача» (rotationX із
  // перспективою), розпрямляється й лягає; слідом іконка вистрибує з
  // прокруткою, а заголовок і опис проявляються нашаруванням — око встигає
  // прочитати картку по частинах. Хвиля йде за порядком у сітці, тож ряд
  // приходить зліва направо, а другий — услід за першим.
  function gsBenefit(el, i, narrow){
    const G = window.gsap;
    const icon = el.querySelector('.b-icon, .pb-num');
    const h3 = el.querySelector('h3'), p = el.querySelector('p');
    const cta = el.querySelector('.pb-cta');
    const at = i * 0.11;
    G.fromTo(el,
      narrow ? { opacity: 0, y: 46, scale: 0.96 }
             : { opacity: 0, y: 70, scale: 0.93, rotationX: -14, transformPerspective: 900, transformOrigin: '50% 100%' },
      { opacity: 1, y: 0, scale: 1, rotationX: 0, duration: 1.05, ease: 'expo.out', delay: at, overwrite: 'auto',
        onComplete: () => {
          el.classList.add('in', 'rv-done');
          G.set(el, { clearProps: 'opacity,transform,translate,scale,rotation,transformOrigin,willChange' });
        } });
    if (h3) G.fromTo(h3, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', delay: at + 0.22, clearProps: 'opacity,transform' });
    if (p)  G.fromTo(p,  { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.65, ease: 'power3.out', delay: at + 0.32, clearProps: 'opacity,transform' });
    if (cta) G.fromTo(cta, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.55, ease: 'power3.out', delay: at + 0.45, clearProps: 'opacity,transform' });
    if (icon) G.fromTo(icon, { opacity: 0, scale: 0.3, rotation: -25 },
      { opacity: 1, scale: 1, rotation: 0, duration: 0.8, ease: 'back.out(2.2)', delay: at + 0.38, clearProps: 'opacity,transform' });
  }
  // Знімки: «завіса» знизу вгору, як у «Атмосфері». Колаж у розповіді (.exp-story-shots)
  // збирається з трьох кадрів, що заходять із різних боків — головний знизу, два
  // менші збоку, кнопка відео проявляється наприкінці. Одинокий кадр (.pb-shot)
  // просто піднімається завісою з легким наближенням.
  function gsShots(el, i, narrow){
    const G = window.gsap;
    const at = i * 0.08;
    const done = (t) => { G.set(t, { clearProps: 'opacity,transform,clipPath' }); };
    if (el.matches('.pb-shot')){
      const img = el.querySelector('img');
      G.fromTo(el, { opacity: 0, y: 50, clipPath: 'inset(100% 0% 0% 0%)' },
        { opacity: 1, y: 0, clipPath: 'inset(0% 0% 0% 0%)', duration: 1.2, ease: 'expo.out', delay: at, overwrite: 'auto',
          onComplete: () => { el.classList.add('in', 'rv-done'); done(el); } });
      if (img) G.fromTo(img, { scale: 1.3 }, { scale: 1, duration: 1.8, ease: 'expo.out', delay: at, clearProps: 'transform' });
      return;
    }
    const main = el.querySelector('.s-main'), a = el.querySelector('.s-a'), b = el.querySelector('.s-b');
    const play = el.querySelectorAll('.gal-play, .gal-ring');
    G.set(el, { opacity: 1 });
    const tl = G.timeline({ delay: at, onComplete: () => {
      el.classList.add('in', 'rv-done');
      G.set([el, main, a, b], { clearProps: 'opacity,transform,clipPath' });
      [main, a, b].forEach(f => { const im = f && f.querySelector('img'); if (im) G.set(im, { clearProps: 'transform' }); });
      if (play.length) G.set(play, { clearProps: 'opacity' });
    } });
    if (play.length) G.set(play, { opacity: 0 });
    const frame = (f, from, at2) => {
      if (!f) return;
      tl.fromTo(f, Object.assign({ opacity: 0 }, from, { clipPath: 'inset(100% 0% 0% 0%)' }),
                   { opacity: 1, x: 0, y: 0, clipPath: 'inset(0% 0% 0% 0%)', duration: 1.15, ease: 'expo.out' }, at2);
      const im = f.tagName === 'IMG' ? f : f.querySelector('img');
      if (im) tl.fromTo(im, { scale: 1.3 }, { scale: 1, duration: 1.7, ease: 'expo.out' }, at2);
    };
    frame(main, { y: 60 }, 0);
    frame(a, narrow ? { y: 40 } : { x: 60 }, 0.18);
    frame(b, narrow ? { y: 40 } : { x: -60 }, 0.34);
    if (play.length) tl.to(play, { opacity: 1, duration: 0.6, ease: 'power2.out' }, 0.8);
  }
  // Списки всередині блоків тексту (кроки в «Розповіді» корпоративів): слідом за
  // самим блоком пункти проявляються по одному.
  function gsChildren(el, i){
    const items = el.querySelectorAll('.gear-steps li');
    if (!items.length) return;
    window.gsap.fromTo(items, { opacity: 0, y: 18 },
      { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.14, delay: i * 0.09 + 0.35, clearProps: 'opacity,transform' });
  }
  // Питання на /faq/: картка виїжджає знизу, у момент приходу її рамка
  // спалахує лаймовим і згасає (як «завантажилась»), заголовок питання
  // з'їжджає зліва, а плюс докочується з поворотом. Спалах — лише кольором
  // рамки (без тіні): тінь у картки своя, і повернення до неї стрибало б.
  function gsFaq(el, i){
    const G = window.gsap;
    const ic = el.querySelector('.faq-icon'), h3 = el.querySelector('.faq-q h3');
    const base = getComputedStyle(el).borderTopColor;
    const at = i * 0.07;
    el.classList.add('gs-busy');
    const tl = G.timeline({ delay: 0, onComplete: () => {
      el.classList.remove('gs-busy');
      el.classList.add('in', 'rv-done');
      G.set(el, { clearProps: 'opacity,transform,scale,borderColor' });
      if (h3) G.set(h3, { clearProps: 'opacity,transform' });
      if (ic) G.set(ic, { clearProps: 'transform' });
    } });
    tl.fromTo(el, { opacity: 0, y: 38, scale: 0.98 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'expo.out' }, at)
      .fromTo(el, { borderColor: 'rgba(198,255,0,0.85)' }, { borderColor: base, duration: 0.9, ease: 'power2.out', immediateRender: false }, at + 0.1);
    if (h3) tl.fromTo(h3, { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power3.out' }, at + 0.15);
    if (ic) tl.fromTo(ic, { scale: 0.2, rotation: -120 }, { scale: 1, rotation: 0, duration: 0.7, ease: 'back.out(2)' }, at + 0.25);
  }
  // Заголовок розділу /faq/: іконка вистрибує, назва підпливає з наведенням на
  // різкість, а під ними лаймова лінія проводиться зліва направо й гасне.
  function gsCatHead(el, i){
    const G = window.gsap;
    const ic = el.querySelector('.faq-cat-icon'), h = el.querySelector('.h2');
    const line = document.createElement('span');
    line.className = 'faq-cat-line'; line.setAttribute('aria-hidden', 'true');
    el.appendChild(line);
    const tl = G.timeline({ delay: i * 0.05, onComplete: () => {
      line.remove();
      el.classList.add('in', 'rv-done');
      G.set(el, { clearProps: 'opacity,transform' });
      if (h) G.set(h, { clearProps: 'opacity,transform,filter' });
      if (ic) G.set(ic, { clearProps: 'transform,opacity' });
    } });
    tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.3 }, 0);
    if (ic) tl.fromTo(ic, { opacity: 0, scale: 0.2, rotation: -50 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.8, ease: 'back.out(2.2)' }, 0);
    if (h)  tl.fromTo(h, { opacity: 0, y: 22, filter: 'blur(8px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.9, ease: 'expo.out' }, 0.08);
    tl.fromTo(line, { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: 0.9, ease: 'power2.inOut' }, 0.05)
      .to(line, { opacity: 0, duration: 0.5 }, 0.85);
  }
  function gsFlush(){
    gsTimer = 0;
    const els = gsQueue.splice(0).sort((a, b) => {
      // Питання лежать у двох колонках: за порядком у DOM пішла б уся ліва
      // колонка, а потім уся права. Для них порядок — за візуальним рядом.
      if (a.matches('.faq-item') && b.matches('.faq-item')){
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return (Math.round(ra.top / 30) - Math.round(rb.top / 30)) || (ra.left - rb.left);
      }
      return (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1;
    });
    if (!els.length) return;
    const ease = 'power3.out';
    const step = Math.min(0.09, 0.45 / els.length);
    // Вузька смуга — одноколонкова стрічка з нашаруванням і нахилами карток:
    // 3D-нахил там зайвий, а нашарування з нахилом читається й без нього.
    const narrow = window.matchMedia('(max-width: 560px)').matches;
    els.forEach((el, i) => {
      const kind = gsKind(el);
      if (kind === 'benefit'){ gsBenefit(el, i, narrow); return; }
      if (kind === 'shots'){ gsShots(el, i, narrow); return; }
      if (kind === 'faq'){ gsFaq(el, i); return; }
      if (kind === 'cathead'){ gsCatHead(el, i); return; }
      if (el.querySelector('.gear-steps li')){
        // Прибираємо їх із поля зору одразу, щоб не було миготіння до їхньої черги.
        window.gsap.set(el.querySelectorAll('.gear-steps li'), { opacity: 0 });
        gsChildren(el, i);
      }
      const from = kind === 'head' ? { opacity: 0, y: 30, filter: 'blur(9px)' }
                 : kind === 'text' ? { opacity: 0, y: 14 }
                 :                   { opacity: 0, y: 42, scale: 0.975 };
      window.gsap.fromTo(el, from, {
        opacity: 1, y: 0, scale: 1, filter: 'blur(0px)',
        duration: kind === 'head' ? 1 : kind === 'text' ? 0.65 : 0.9,
        ease: ease, delay: i * step, overwrite: 'auto',
        // rv-done ставимо ДО очищення інлайнових стилів, в одному такті: CSS
        // вже перестав ховати елемент, а GSAP ще нічого не зняв — миготіння
        // нема. clearProps точковий, а не 'all': 'all' зніс би й чужі інлайнові
        // стилі елемента.
        onComplete: () => {
          el.classList.add('in', 'rv-done');
          window.gsap.set(el, { clearProps: 'opacity,transform,translate,scale,filter,willChange' });
        }
      });
      // Картки каталогу: фото всередині повільно «доїжджає» з легкого
      // збільшення — картка з'являється не пласким прямокутником, а кадром.
      const img = el.matches('.uc-card') && el.querySelector('.uc-media img');
      if (img) window.gsap.fromTo(img, { scale: 1.14 },
        { scale: 1, duration: 1.3, ease: 'power3.out', delay: i * step, clearProps: 'transform' });
    });
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      if (e.target._gs){
        gsQueue.push(e.target);
        if (!gsTimer) gsTimer = setTimeout(gsFlush, 70);
        return;
      }
      e.target.classList.add('in');
      settleReveal(e.target);
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => {
    // Усередині нескінченних стрічок поодинокі появи заборонені: там сотні
    // клонованих карток, і кожна проявлялась би окремо — при вертикальній
    // прокрутці порядно, при горизонтальній по одній, збиваючи паралакс.
    // Стрічка проявляється цілком, одним контейнером.
    // Ці нічого не програють, тож і чекати їм нема чого.
    if (el.closest('.uc-grid, .gallery-grid')) { el.classList.add('in', 'rv-done'); return; }
    // Черга рахується серед сусідів у своїй групі, а не за номером елемента на
    // всій сторінці. Раніше було i % 4 від глобального індексу: сусідні
    // картки однієї сітки отримували затримки 0.18 і 0, тобто черга була
    // випадковою, і сітка приходила рвано. Тепер шість карток одного блоку
    // приходять групою, одна за одною, а стеля 0.28s не дає останній у
    // великій сітці приїхати помітно пізніше за першу.
    const group = el.parentElement
      ? Array.prototype.filter.call(el.parentElement.children, n => n.classList.contains('reveal'))
      : [];
    // Таймлайн «Як це працює» проявляється власною хореографією (нижче), тож
    // загальна поява його не чіпає.
    if (gsapOn && el.matches('.flow, .gallery-strip, .uc-gallery')) return;
    if (gsapOn && !el.matches('.slab')){
      // Свій transition CSS-появи вимкнено (клас gs-rv), рух веде GSAP.
      el._gs = true;
      el.classList.add('gs-rv');
      io.observe(el);
      return;
    }
    const k = Math.max(0, group.indexOf(el));
    el.style.transitionDelay = (Math.min(k, 4) * 0.07).toFixed(2) + 's';
    io.observe(el);
  });

  // ---- /faq/: питання й заголовки розділів (поява через загальний механізм) ----
  // До появи їх ховає CSS (html.js .faq-cats … :not(.rv-done)); без GSAP скрипт
  // одразу позначає їх готовими, інакше сторінка лишилась би порожньою.
  (function(){
    const els = [].slice.call(document.querySelectorAll('.faq-cats .faq-cat-head, .faq-cats .faq-item'));
    if (!els.length) return;
    if (!gsapOn){ els.forEach(e => e.classList.add('rv-done')); return; }
    els.forEach(e => { e._gs = true; e.classList.add('gs-rv'); io.observe(e); });
  })();

  // ---- /faq/: вступ геро (GSAP) ----
  // «Крихти», заголовок (із наведенням на різкість), вступ і картка-барабан з
  // питаннями, що виїжджає завісою знизу вгору. До готовності CSS ховає ці
  // елементи (html.js:not(.gs-cover-done)); без GSAP клас ставимо одразу.
  (function(){
    const head = document.querySelector('.faq-head');
    const root = document.documentElement;
    if (!head) return;
    if (!gsapOn){ root.classList.add('gs-cover-done'); return; }
    const G = window.gsap;
    const one = (sel) => head.querySelector(sel);
    const crumb = one('.exp-crumb'), title = one('.exp-head-title'), lead = one('.exp-head-lead'),
          reel = one('.exp-head-reel--q'), win = one('.exp-reel-window');
    const all = [crumb, title, lead, reel].filter(Boolean);
    let started = false;
    function go(){
      if (started) return;
      if (root.classList.contains('hold')){ setTimeout(go, 40); return; }
      started = true;
      G.set(all, { opacity: 0 });
      root.classList.add('gs-cover-done');
      const tl = G.timeline({ defaults: { ease: 'expo.out' }, onComplete: () => {
        G.set(all, { clearProps: 'opacity,transform,filter,clipPath' });
        if (win) G.set(win, { clearProps: 'opacity' });
      } });
      if (reel) tl.fromTo(reel, { opacity: 0, y: 46, clipPath: 'inset(100% 0% 0% 0%)' },
                                { opacity: 1, y: 0, clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4 }, 0);
      if (win) tl.fromTo(win, { opacity: 0 }, { opacity: 1, duration: 1, ease: 'power2.out' }, 0.45);
      if (crumb) tl.fromTo(crumb, { opacity: 0, x: -16 }, { opacity: 1, x: 0, duration: 0.8 }, 0.15);
      if (title) tl.fromTo(title, { opacity: 0, y: 46, filter: 'blur(10px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.2 }, 0.25);
      if (lead)  tl.fromTo(lead, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 1 }, 0.5);
    }
    go();
  })();

  // ---- Картки каталогу на /experiences/: поява при прокрутці ----
  // Сорок чотири картки раніше стояли одразу всі. Тепер ряд за рядом
  // проявляються чергою (загальний механізм появи вище: тригер IO, рух GSAP),
  // а фото в кожній додатково «доїжджає» з легкого збільшення.
  // До першого кадру картки ховає CSS (html.js .exp-grid .uc-card:not(.rv-done)),
  // тож без цього коду вони мусять бути показані — інакше каталог лишився б
  // порожнім: без GSAP усі картки одразу позначаємо як готові.
  // Фільтр тем (нижче) перед кожним перемиканням викликає __expFinish: він
  // миттю доводить до кінця всі, що ще не встигли з'явитись, — інакше картка,
  // яку фільтр показав уперше, лишалась би прозорою, а його власна анімація
  // входу й FLIP-зсув лягали б на чужий transform.
  (function(){
    const cards = [].slice.call(document.querySelectorAll('.exp-grid .uc-card'));
    if (!cards.length) return;
    if (!gsapOn){
      cards.forEach(c => c.classList.add('rv-done'));
      return;
    }
    cards.forEach(c => { c._gs = true; c.classList.add('gs-rv'); io.observe(c); });
    window.__expFinish = function(){
      cards.forEach(c => {
        if (c.classList.contains('rv-done')) return;
        io.unobserve(c);
        window.gsap.killTweensOf(c);
        const img = c.querySelector('.uc-media img');
        if (img) window.gsap.killTweensOf(img);
        c.classList.add('in', 'rv-done');
        window.gsap.set(c, { clearProps: 'opacity,transform,translate,scale,filter,willChange' });
        if (img) window.gsap.set(img, { clearProps: 'transform' });
      });
      gsQueue.length = 0;
    };
  })();

  // ---- «Атмосфера» і «Silent-досвіди»: поява кадрів і карток (GSAP) ----
  // Обидві стрічки нескінченні, а «Silent-досвіди» ще й віртуалізована, тож
  // анімуємо лише те, що в момент появи блоку справді потрапило в екран, а
  // решту не чіпаємо: кадри й картки поза екраном не існують для очей, а
  // будь-який transform на них лише плутав би віртуалізацію.
  //  • «Атмосфера»: кожен кадр «підіймається завісою» знизу вгору (clip-path),
  //    фото всередині повільно віддаляється зі збільшення, кнопка відео
  //    проявляється в кінці. Хвиля йде зліва направо.
  //  • «Silent-досвіди»: картки плавно підіймаються й розправляються, фото в
  //    них «доїжджає» з легкого зуму — той самий вхід, що в каталозі
  //    /experiences/ (без ліній і спалахів).
  // До моменту показу контейнер тримає CSS-приховування .reveal, а елементи
  // усередині ховаємо в тому ж такті, коли контейнер відкриваємо, — миготіння
  // нема. Без GSAP загальна поява показує контейнер цілком, як раніше.
  // Перед перемиканням теми в стрічці недограні показ доводиться до кінця
  // (__stripFinish), щоб не змішуватись із FLIP і власним входом фільтра.
  (function(){
    if (!gsapOn) return;
    const G = window.gsap;
    const conts = [].slice.call(document.querySelectorAll('.gallery-strip, .uc-gallery'));
    if (!conts.length) return;
    const running = [];
    function onScreen(el){
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.right > 0 && r.left < innerWidth && r.bottom > 0 && r.top < innerHeight;
    }
    function order(list){
      return list.sort((a, b) => {
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        return (Math.round(ra.left / 40) - Math.round(rb.left / 40)) || (ra.top - rb.top);
      });
    }
    function showGallery(c){
      const items = order([].slice.call(c.querySelectorAll('.gallery-item')).filter(onScreen));
      items.forEach(it => it.classList.add('gs-busy'));
      G.set(items, { opacity: 0 });
      c.classList.add('in', 'rv-done');
      const tl = G.timeline({ onComplete: () => {
        items.forEach(it => {
          it.classList.remove('gs-busy');
          G.set(it, { clearProps: 'opacity,transform,clipPath' });
          const img = it.querySelector('img'); if (img) G.set(img, { clearProps: 'transform' });
          const pl = it.querySelectorAll('.gal-play, .gal-ring'); if (pl.length) G.set(pl, { clearProps: 'opacity' });
        });
      } });
      items.forEach((it, i) => {
        const at = Math.min(i * 0.1, 0.9);
        const img = it.querySelector('img');
        const pl = it.querySelectorAll('.gal-play, .gal-ring');
        if (pl.length) G.set(pl, { opacity: 0 });
        tl.fromTo(it, { opacity: 0, y: 64, clipPath: 'inset(100% 0% 0% 0%)' },
                      { opacity: 1, y: 0, clipPath: 'inset(0% 0% 0% 0%)', duration: 1.15, ease: 'expo.out' }, at);
        if (img) tl.fromTo(img, { scale: 1.35 }, { scale: 1, duration: 1.8, ease: 'expo.out' }, at);
        if (pl.length) tl.to(pl, { opacity: 1, duration: 0.6, ease: 'power2.out' }, at + 0.75);
      });
      running.push(tl);
    }
    // Картки, що на момент показу блоку ще нижче краю екрана (другий ряд, коли
    // блок тільки заїхав у кадр), чекають своєї черги: їх ховаємо й проявляємо
    // тим самим рухом, щойно вони самі потраплять в екран. Раніше грав лише
    // верхній ряд, а нижній просто стояв — його анімація відбувалась би, поки
    // його ще не видно.
    const pendingCards = new Set();
    let pendingQueue = [], pendingTimer = 0;
    function animateCards(cards){
      if (!cards.length) return;
      cards.forEach(el => el.classList.add('gs-busy'));
      G.set(cards, { opacity: 0 });
      const tl = G.timeline({ onComplete: () => {
        cards.forEach(el => {
          el.classList.remove('gs-busy');
          G.set(el, { clearProps: 'opacity,transform,scale' });
          const img = el.querySelector('.uc-media img'); if (img) G.set(img, { clearProps: 'transform' });
        });
      } });
      const step = Math.min(0.09, 0.45 / Math.max(cards.length, 1));
      cards.forEach((el, i) => {
        const at = i * step;
        const img = el.querySelector('.uc-media img');
        tl.fromTo(el, { opacity: 0, y: 42, scale: 0.975 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'power3.out' }, at);
        if (img) tl.fromTo(img, { scale: 1.14 }, { scale: 1, duration: 1.3, ease: 'power3.out' }, at);
      });
      running.push(tl);
    }
    const ioPending = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        ioPending.unobserve(e.target);
        if (!pendingCards.has(e.target)) return;
        pendingCards.delete(e.target);
        pendingQueue.push(e.target);
        if (!pendingTimer) pendingTimer = setTimeout(() => {
          pendingTimer = 0;
          animateCards(order(pendingQueue.splice(0)));
        }, 60);
      });
    }, { threshold: 0.12 });
    function showCards(c){
      // Той самий плавний вхід, що в картках каталогу на /experiences/: картка
      // піднімається знизу й трохи збільшується до свого розміру, фото
      // всередині повільно віддаляється з легкого зуму. Без ліній і спалахів.
      const all = [].slice.call(c.querySelectorAll('.uc-card')).filter(el => {
        if (el.hidden) return false;
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.right > 0 && r.left < innerWidth;   // у межах екрана по горизонталі
      });
      const now = all.filter(onScreen), later = all.filter(el => !onScreen(el));
      later.forEach(el => {
        el.classList.add('gs-busy');
        G.set(el, { opacity: 0 });
        pendingCards.add(el);
        ioPending.observe(el);
      });
      G.set(now, { opacity: 0 });
      c.classList.add('in', 'rv-done');
      animateCards(order(now));
    }
    const io2 = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        io2.unobserve(e.target);
        // Невелика пауза: віртуалізована стрічка розставляє картки за
        // прокруткою вже ПІСЛЯ спрацювання IO, і в момент, коли блок тільки
        // з'явився в кадрі, вони ще стоять за межами екрана (координати
        // -60000px) — фільтр «що в кадрі» вийшов би порожнім, і жодна
        // картка не отримала б анімації. Контейнер тим часом лишається
        // прихованим (.reveal), тож це просто ~0.15с очікування.
        const t = e.target;
        setTimeout(() => {
          if (t.classList.contains('rv-done')) return;
          if (t.matches('.gallery-strip')) showGallery(t); else showCards(t);
        }, 160);
      });
    }, { threshold: 0.15 });
    conts.forEach(c => io2.observe(c));
    window.__stripFinish = function(){
      // Контейнер, до якого ще не дійшли, показуємо одразу: інакше фільтр
      // працював би по невидимому блоку.
      conts.forEach(c => { if (!c.classList.contains('rv-done')){ io2.unobserve(c); c.classList.add('in', 'rv-done'); } });
      running.splice(0).forEach(tl => tl.progress(1));
      // Картки, що чекали своєї черги, показуємо одразу й чисто.
      pendingCards.forEach(el => {
        ioPending.unobserve(el);
        el.classList.remove('gs-busy');
        G.set(el, { clearProps: 'opacity,transform,scale' });
      });
      pendingCards.clear(); pendingQueue = [];
    };
    document.addEventListener('click', (e) => {
      if (e.target.closest && e.target.closest('.exp-chip')) window.__stripFinish();
    }, true);
  })();

  // ---- Фільтри тем і навігація FAQ: «підвантаження» рядка чипів (GSAP) ----
  // Рядок чипів (.exp-filter на головній, /experiences/ і корпоративах; .faq-nav
  // на /faq/) раніше просто стояв. Тепер він завантажується як один суцільний
  // рядок: чипи по черзі виринають зліва направо (пружина, наведення на різкість),
  // у момент появи кожен коротко спалахує лаймовою рамкою — ніби по рядку
  // пробігає світло, — а лічильник у ньому дорахується від нуля до свого числа.
  // До показу чипи ховає CSS (html.js .exp-filter:not(.gs-in) …), тож без GSAP
  // усім барам одразу ставимо gs-in, інакше рядок лишився б порожнім.
  (function(){
    const bars = [].slice.call(document.querySelectorAll('.exp-filter, .faq-nav'));
    if (!bars.length) return;
    if (!gsapOn){ bars.forEach(b => b.classList.add('gs-in')); return; }
    const G = window.gsap;
    function load(bar){
      const chips = [].slice.call(bar.querySelectorAll('.exp-chip'));
      bar.classList.add('gs-busy');
      const counts = chips.map(ch => {
        const n = ch.querySelector('span:not(.faq-nav-icon)');
        const val = n ? parseInt(n.textContent, 10) : NaN;
        return (n && !isNaN(val)) ? { n: n, val: val, o: { v: 0 } } : null;
      });
      counts.forEach(c => { if (c) c.n.textContent = '0'; });
      // Кінцевий колір рамки — власний колір кожного чипа (активний лаймовий,
      // решта сірі), зчитаний ДО зміни: спалах повертається саме до нього.
      const base = chips.map(ch => getComputedStyle(ch).borderTopColor);
      G.set(chips, { opacity: 0, y: 16, scale: 0.86, filter: 'blur(6px)' });
      bar.classList.add('gs-in');
      const tl = G.timeline({ onComplete: () => {
        bar.classList.remove('gs-busy');
        G.set(chips, { clearProps: 'opacity,transform,scale,filter,borderColor,boxShadow' });
        counts.forEach(c => { if (c) c.n.textContent = String(c.val); });
      } });
      chips.forEach((ch, i) => {
        const at = i * 0.055;
        tl.to(ch, { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)', duration: 0.7, ease: 'back.out(1.7)' }, at);
        // Спалах рамки в момент, коли чип «дістався»: світло пробігає рядком.
        tl.fromTo(ch, { borderColor: 'rgba(198,255,0,0.9)', boxShadow: '0 0 20px 0 rgba(198,255,0,0.45)' },
                      { borderColor: base[i], boxShadow: '0 0 0 0 rgba(198,255,0,0)', duration: 0.7, ease: 'power2.out', immediateRender: false }, at + 0.12);
        const ic = ch.querySelector('.faq-nav-icon');
        if (ic) tl.fromTo(ic, { scale: 0.2, rotation: -60 }, { scale: 1, rotation: 0, duration: 0.6, ease: 'back.out(2.4)', clearProps: 'transform' }, at + 0.1);
        const c = counts[i];
        if (c) tl.to(c.o, { v: c.val, duration: 0.9, ease: 'power2.out',
                            onUpdate: () => { c.n.textContent = String(Math.round(c.o.v)); } }, at + 0.1);
      });
    }
    const io3 = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        io3.unobserve(e.target);
        load(e.target);
      });
    }, { threshold: 0.2 });
    bars.forEach(b => io3.observe(b));
  })();

  // ---- Корпоративи: вступна хореографія геро (GSAP) ----
  // Сторінка корпоративів раніше відкривалась готовою картинкою. Тепер геро
  // збирається на очах: «крихти», два рядки заголовка (із наведенням на
  // різкість), вступ, кнопки, чотири факти — кожен зі своєю іконкою, що
  // «вистрибує», — а колонки фото з'їжджаються завісою знизу вгору.
  // До готовності CSS ховає ці елементи (html.js:not(.gs-cover-done)), тож без
  // GSAP клас ставимо одразу, інакше геро було б порожнім. Старт чекає, доки
  // підвантажаться шрифти (.hold), щоб заголовок не перемальовувався під час руху.
  (function(){
    const cover = document.querySelector('.exp-cover-gallery');
    const root = document.documentElement;
    if (!cover) return;
    if (!gsapOn){ root.classList.add('gs-cover-done'); return; }
    const G = window.gsap;
    const q = (sel) => [].slice.call(cover.querySelectorAll(sel));
    const crumb = q('.exp-crumb'), lead = q('.t-lead'), sub = q('.t-sub'), p = q('.exp-lead'),
          btns = q('.exp-actions > *'), facts = q('.exp-facts li'), ico = q('.exp-facts .f-ico'),
          cols = q('.gallery-columns'), col = q('.gallery-col');
    const all = [].concat(crumb, lead, sub, p, btns, facts, cols, col);
    let started = false;
    function go(){
      if (started) return;
      if (root.classList.contains('hold')){ setTimeout(go, 40); return; }
      started = true;
      G.set(all, { opacity: 0 });
      root.classList.add('gs-cover-done');
      const tl = G.timeline({ defaults: { ease: 'expo.out' }, onComplete: () => {
        G.set([].concat(all, ico), { clearProps: 'opacity,transform,filter,clipPath' });
      } });
      tl.fromTo(crumb, { opacity: 0, x: -16 }, { opacity: 1, x: 0, duration: 0.8 }, 0)
        .fromTo(lead,  { opacity: 0, y: 46, filter: 'blur(10px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.2 }, 0.08)
        .fromTo(sub,   { opacity: 0, y: 46, filter: 'blur(10px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.2 }, 0.2)
        .fromTo(p,     { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 1 }, 0.4)
        .fromTo(btns,  { opacity: 0, y: 24, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'back.out(1.6)', stagger: 0.1 }, 0.55)
        .fromTo(facts, { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 0.8, stagger: 0.1 }, 0.75)
        .fromTo(ico,   { scale: 0.3, rotation: -40 }, { scale: 1, rotation: 0, duration: 0.8, ease: 'back.out(2.2)', stagger: 0.1 }, 0.8);
      if (cols.length){
        tl.fromTo(cols, { opacity: 0, clipPath: 'inset(100% 0% 0% 0%)' },
                        { opacity: 1, clipPath: 'inset(0% 0% 0% 0%)', duration: 1.5, ease: 'expo.out' }, 0.15);
        // Самі колонки їдуть CSS-анімацією transform, тож рухаємо тільки їхню прозорість.
        tl.fromTo(col, { opacity: 0 }, { opacity: 1, duration: 0.9, ease: 'power2.out', stagger: 0.25 }, 0.3);
      }
    }
    go();
  })();

  // ---- Mega-меню шапки: поява вмісту при відкритті (GSAP, десктоп) ----
  // Сама панель відкривається CSS (hover/focus-within, без JS); тут лише вміст:
  // фото-картка виїжджає зліва з наближенням, розділи підпливають чергою, їхні
  // іконки «вистрибують», а пункти списків по одному з'являються зліва. Це і є
  // «підвантаження» меню. Спрацьовує при кожному відкритті — панель тим часом
  // з'являється своїм CSS-переходом (затримка 0.08с), тож вміст стартує з нею.
  (function(){
    const G = window.gsap;
    if (!G || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.nav-item-mega').forEach(function(item){
      const panel = item.querySelector('.nav-mega-panel');
      if (!panel) return;
      let hovered = false, focused = false, tl = null;
      function targets(){
        const t = {
          visual: panel.querySelector('.nav-mega-visual'),
          vimg: panel.querySelector('.nav-mega-visual img'),
          vtext: panel.querySelector('.nav-mega-visual-text'),
          cta: panel.querySelector('.nav-mega-cta'),
          cols: [].slice.call(panel.querySelectorAll('.nav-mega-card'))
        };
        return t;
      }
      function reset(){
        if (tl){ tl.kill(); tl = null; }
        const all = panel.querySelectorAll('.nav-mega-visual, .nav-mega-visual img, .nav-mega-visual-text, .nav-mega-cta, .nav-mega-card, .nav-mega-icon, .nav-mega-cat, .nav-mega-q');
        G.set(all, { clearProps: 'opacity,transform,filter' });
      }
      function play(){
        reset();
        const t = targets();
        tl = G.timeline({ delay: 0.06, defaults: { ease: 'power3.out' }, onComplete: reset });
        if (t.visual) tl.fromTo(t.visual, { opacity: 0, x: -18, scale: 0.96 }, { opacity: 1, x: 0, scale: 1, duration: 0.6, ease: 'expo.out' }, 0);
        if (t.vimg)   tl.fromTo(t.vimg, { scale: 1.18 }, { scale: 1, duration: 0.9, ease: 'expo.out' }, 0);
        if (t.vtext)  tl.fromTo(t.vtext, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5 }, 0.2);
        if (t.cta)    tl.fromTo(t.cta, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5 }, 0.32);
        t.cols.forEach(function(c, i){
          const at = 0.06 + i * 0.045;
          tl.fromTo(c, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.55 }, at);
          const ic = c.querySelector('.nav-mega-icon'); if (ic) tl.fromTo(ic, { opacity: 0, scale: 0.3, rotation: -30 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.55, ease: 'back.out(2.2)' }, at + 0.08);
          const cat = c.querySelector('.nav-mega-cat'); if (cat) tl.fromTo(cat, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.45 }, at + 0.1);
          const qs = c.querySelectorAll('.nav-mega-q');
          if (qs.length) tl.fromTo(qs, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.4, stagger: 0.03 }, at + 0.16);
        });
      }
      function sync(){
        const open = hovered || focused;
        if (open && !item._gsOpen){ item._gsOpen = true; play(); }
        else if (!open && item._gsOpen){ item._gsOpen = false; reset(); }
      }
      item.addEventListener('mouseenter', function(){ hovered = true; sync(); });
      item.addEventListener('mouseleave', function(){ hovered = false; sync(); });
      item.addEventListener('focusin', function(){ focused = true; sync(); });
      item.addEventListener('focusout', function(e){ if (!item.contains(e.relatedTarget)){ focused = false; sync(); } });
    });
  })();

  // ---- Футер: поява й «вихід слова» (GSAP + ScrollTrigger) ----
  // Три окремі речі, кожна легка для сторінки (аврору футера не чіпаємо: її
  // розмиття й так найдорожче на сторінці):
  //  1. Гігантське слово SILENT має легкий паралакс за прокруткою (scrub): воно ледь
  //     запізнюється й до кінця сторінки стає на місце, без обрізання знизу. Рух —
  //     через CSS-змінну --fw-y на властивість
  //     translate (site.css, .footer-word): у слова вже є transform:translateX(-50%),
  //     а GSAP переписав би його в пікселі, і на ресайзі слово з'їхало б з центру.
  //  2. Лаймова «комета» пробігає верхньою лінією футера один раз (--lx на
  //     .footer-inner::before), слідом хвилею з'являються бренд, колонки й пункти
  //     списків, іконки соцмереж вистрибують із поворотом (пружина), внизу —
  //     юридичний рядок.
  //  3. Іконки соцмереж тягнуться до курсора — той самий пружний «магніт», що в
  //     кнопок (див. «Магнітні кнопки»).
  // До показу вміст ховає CSS (html.js .site-footer:not(.gs-in)); без GSAP і при
  // reduce-motion клас ставимо одразу, інакше футер лишився б порожнім.
  (function(){
    const foot = document.querySelector('.site-footer');
    if (!foot) return;
    if (!gsapOn){ foot.classList.add('gs-in'); return; }
    const G = window.gsap, ST = window.ScrollTrigger;
    G.registerPlugin(ST);
    const q = (sel) => [].slice.call(foot.querySelectorAll(sel));
    const logo = q('.f-logo'), tag = q('.f-tagline'), cta = q('.f-cta'), heads = q('.f-col h4'),
          items = q('.f-col li'), socs = q('.f-soc'), note = q('.f-note'), legal = q('.footer-legal > *');
    const inner = foot.querySelector('.footer-inner');
    const all = [].concat(logo, tag, cta, heads, items, socs, note, legal);

    // Паралакс слова: воно ледь запізнюється за прокруткою й до кінця сторінки
    // стає на місце (16% висоти → 0). Обгортка не обрізає його по вертикалі
    // (site.css, .footer-word-clip), тож слово нічим не «зрізається» знизу.
    G.fromTo(foot, { '--fw-y': '16%' }, { '--fw-y': '0%', ease: 'none',
      scrollTrigger: { trigger: foot, start: 'top bottom', end: 'bottom bottom', scrub: 0.6 } });

    // Вміст ховаємо й одразу віддаємо клас: далі його показує лише GSAP.
    G.set(all, { opacity: 0 });
    if (inner) G.set(inner, { '--lx': '-20%', '--lo': 1 });
    foot.classList.add('gs-in');
    const tl = G.timeline({ paused: true, defaults: { ease: 'power3.out' }, onComplete: () => {
      G.set(all, { clearProps: 'opacity,transform,filter,scale,rotation' });
      // Комету повертаємо за лівий край: і без overflow-x:clip (старі браузери) вона
      // не лишиться за правим краєм і не розширить сторінку.
      if (inner) G.set(inner, { '--lx': '-20%' });
    } });
    if (inner){
      tl.fromTo(inner, { '--lx': '-20%' }, { '--lx': '100%', duration: 1.4, ease: 'power2.inOut' }, 0)
        .to(inner, { '--lo': 0, duration: 0.35, ease: 'power1.in' }, 1.15);
    }
    tl.fromTo(logo, { opacity: 0, y: 18, filter: 'blur(6px)' }, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.8 }, 0.1)
      .fromTo(tag,  { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.7 }, 0.22)
      .fromTo(cta,  { opacity: 0, y: 14, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'back.out(1.6)' }, 0.36)
      .fromTo(heads, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.1 }, 0.25)
      .fromTo(items, { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.55, stagger: 0.04 }, 0.4)
      .fromTo(socs, { opacity: 0, scale: 0.3, rotation: -40 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.7, ease: 'back.out(2.2)', stagger: 0.07 }, 0.55)
      .fromTo(note, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.6 }, 0.85)
      .fromTo(legal, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.1 }, 0.95);
    // Футер може бути в кадрі одразу (короткі сторінки): тоді onEnter спрацює на старті.
    ST.create({ trigger: foot, start: 'top 78%', once: true, onEnter: () => tl.play() });

    // Саме слово, окрім підйому за прокруткою, має власний вхід: у момент, коли
    // воно з'являється в кадрі, літери сходяться з розлоту (letter-spacing) і
    // різкішають з розмиття. Окремий тригер від самого слова, а не від футера: до
    // цього моменту слово ще під краєм, і вхід відіграв би непомітно. Ширина
    // слова міняється разом із letter-spacing, а центр тримає translateX(-50%).
    const word = foot.querySelector('.footer-word'), clip = foot.querySelector('.footer-word-clip');
    if (word && clip){
      const tw = G.fromTo(word, { letterSpacing: '0.11em', filter: 'blur(14px)' },
        { letterSpacing: '0.012em', filter: 'blur(0px)', duration: 1.7, ease: 'expo.out', paused: true,
          clearProps: 'letterSpacing,filter' });
      ST.create({ trigger: clip, start: 'top 90%', once: true, onEnter: () => tw.play() });
    }
  })();

  // ---- «Як це працює»: таймлайн проявляється по ходу лінії (GSAP) ----
  // Раніше весь блок виїжджав одним шматком. Тепер це одна історія: лінія
  // малюється від першого кроку до останнього, а перед нею біжить світла
  // іскра; щойно фронт лінії доходить до кружечка, той «вистрибує» зі
  // спалахом, його іконка на мить оживає, і слідом проявляється сам крок —
  // номер, заголовок, пункти, а галочки в них домальовуються.
  // Момент кожного кроку рахується з ПОЛОЖЕННЯ його кружечка на лінії й
  // з кривої руху лінії (обернена ease), а не задається на око, тож кружечок
  // з'являється саме тоді, коли лінія до нього дійшла, за будь-якої ширини.
  // Лінією керує CSS-змінна --p (0…1) на .flow: clip-path її ::before читає
  // її (див. site.css, «Лінія таймлайна»). Три розкладки — три сценарії:
  //   ≥1041px  горизонтальна лінія;  621–1040px  сітка 2×2 без спільної лінії,
  //   кроки ідуть по черзі;  ≤620px  вертикальна лінія праворуч.
  // Тригер — ScrollTrigger, одноразовий. Без GSAP і при reduce-motion блок
  // показується як завжди (загальна поява).
  (function(){
    const G = window.gsap, ST = window.ScrollTrigger;
    const flow = document.querySelector('.flow');
    if (!G || !ST || !flow ||
        window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    G.registerPlugin(ST);
    // Сам <ol> робимо видимим одразу: ховається лише вміст, тож між кадрами
    // нема ні миготіння, ні порожнього блоку, якщо скрипт спізниться.
    flow.classList.add('in', 'rv-done');

    const steps = [].slice.call(flow.querySelectorAll('.flow-step'));
    const P = steps.map(function(st){
      return {
        step: st,
        node: st.querySelector('.flow-node'),
        chip: st.querySelector('.flow-chip'),
        h3: st.querySelector('h3'),
        lis: [].slice.call(st.querySelectorAll('.step-list li')),
        ticks: [].slice.call(st.querySelectorAll('.step-list li svg path'))
      };
    });
    let triggered = false, played = false, tl = null;

    // Вміст кроку: номер, заголовок, пункти черзі; галочки домальовуються.
    function content(p, tlx, at){
      tlx.fromTo(p.chip, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power3.out' }, at)
         .fromTo(p.h3,   { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.55, ease: 'power3.out' }, at + 0.08)
         .fromTo(p.lis,  { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out', stagger: 0.12 }, at + 0.22)
         .to(p.ticks,    { strokeDashoffset: 0, duration: 0.4, ease: 'power2.out', stagger: 0.12 }, at + 0.34);
    }
    // Кружечок: пружинний вистріл, спалах свічення й короткий «пульс» іконки.
    function pop(p, tlx, at){
      tlx.fromTo(p.node, { opacity: 0, scale: 0.2 },
                 { opacity: 1, scale: 1, duration: 0.7, ease: 'back.out(2.4)' }, at)
         .fromTo(p.node, { boxShadow: '0 0 0px 0px rgba(198,255,0,0), inset 0 0 0px 0px rgba(198,255,0,0)' },
                 { boxShadow: '0 0 60px 8px rgba(198,255,0,0.8), inset 0 0 26px -4px rgba(198,255,0,0.7)',
                   duration: 0.28, ease: 'power2.out', yoyo: true, repeat: 1 }, at + 0.05)
         .call(function(){ p.step.classList.add('flow-pop'); }, null, at + 0.05)
         .call(function(){ p.step.classList.remove('flow-pop'); }, null, at + 1.5);
    }
    function hideAll(){
      P.forEach(function(p){
        p.ticks.forEach(function(t){
          const len = t.getTotalLength ? Math.ceil(t.getTotalLength()) : 20;
          t.style.strokeDasharray = len; t.style.strokeDashoffset = len;
        });
      });
    }
    function cleanup(){
      P.forEach(function(p){
        G.set([p.node, p.chip, p.h3, p.lis, p.ticks, p.step], { clearProps: 'all' });
      });
      G.set(flow, { clearProps: '--p' });
      const sp = flow.querySelector('.flow-spark'); if (sp) sp.remove();
    }
    function finish(){ played = true; cleanup(); }

    G.matchMedia().add({
      line: '(min-width: 1041px), (max-width: 620px)',
      grid: '(min-width: 621px) and (max-width: 1040px)'
    }, function(ctx){
      if (played) return;
      const vertical = window.matchMedia('(max-width: 620px)').matches;
      hideAll();
      tl = G.timeline({ paused: true, onComplete: finish });

      if (ctx.conditions.line){
        const fr = flow.getBoundingClientRect();
        const total = vertical ? fr.height : fr.width;
        const dur = vertical ? 1.9 : 2.1;
        const ease = G.parseEase('power2.inOut');
        // Момент, коли лінія дійшла до частки frac свого шляху: обернена ease.
        function timeAt(frac){
          let lo = 0, hi = 1;
          for (let i = 0; i < 26; i++){ const m = (lo + hi) / 2; if (ease(m) < frac) lo = m; else hi = m; }
          return ((lo + hi) / 2) * dur;
        }
        // Іскра на фронті лінії: лежить на тій самій осі, що й центри кружечків.
        const c0 = P[0].node.getBoundingClientRect();
        const spark = document.createElement('span');
        spark.className = 'flow-spark'; spark.setAttribute('aria-hidden', 'true');
        spark.style.left = vertical ? (c0.left + c0.width / 2 - fr.left) + 'px' : '0px';
        spark.style.top  = vertical ? '0px' : (c0.top + c0.height / 2 - fr.top) + 'px';
        flow.appendChild(spark);

        G.set(flow, { '--p': 0 });
        G.set(P.map(function(p){ return p.node; }), { opacity: 0, scale: 0.2 });
        G.set(P.map(function(p){ return p.chip; }), { opacity: 0 });
        G.set(P.map(function(p){ return p.h3; }), { opacity: 0 });
        G.set([].concat.apply([], P.map(function(p){ return p.lis; })), { opacity: 0 });

        tl.to(flow, { '--p': 1, duration: dur, ease: 'power2.inOut' }, 0);
        tl.fromTo(spark, vertical ? { y: 0 } : { x: 0 }, vertical ? { y: total, duration: dur, ease: 'power2.inOut' }
                                                                   : { x: total, duration: dur, ease: 'power2.inOut' }, 0);
        tl.fromTo(spark, { opacity: 0 }, { opacity: 1, duration: 0.25 }, 0)
          .to(spark, { opacity: 0, duration: 0.35 }, dur - 0.3);
        P.forEach(function(p, i){
          const r = p.node.getBoundingClientRect();
          const frac = vertical ? (r.top + r.height / 2 - fr.top) / total
                                : (r.left + r.width / 2 - fr.left) / total;
          const t = timeAt(Math.min(Math.max(frac, 0), 1));
          pop(p, tl, Math.max(0, t - 0.12));
          content(p, tl, t + 0.06);
        });
      } else {
        // Планшет: лінії немає (кожна картка з власною обводкою), тож кроки
        // приходять по черзі — картка виїжджає, кружечок вистрибує, вміст
        // проявляється.
        G.set(P.map(function(p){ return p.step; }), { opacity: 0, y: 38 });
        G.set(P.map(function(p){ return p.node; }), { opacity: 0, scale: 0.2 });
        G.set(P.map(function(p){ return p.chip; }), { opacity: 0 });
        G.set(P.map(function(p){ return p.h3; }), { opacity: 0 });
        G.set([].concat.apply([], P.map(function(p){ return p.lis; })), { opacity: 0 });
        P.forEach(function(p, i){
          const at = i * 0.34;
          tl.to(p.step, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' }, at);
          pop(p, tl, at + 0.12);
          content(p, tl, at + 0.3);
        });
      }
      if (triggered) tl.play();
      return function(){ if (tl) tl.kill(); };
    });

    ST.create({
      trigger: flow, start: 'top 80%', end: 'bottom top', once: true,
      onEnter: go, onLeave: go
    });
    function go(){ triggered = true; if (tl && !played) tl.play(); }
  })();

  // ---- Календар у формі ----
  // Підставляє дату в поле «Бажана дата» і читає його назад, тож обидва способи
  // введення лишаються синхронними. Місяці й дні тижня рахуємо від понеділка,
  // назви бере Intl — рік і назва місяця оновлюються самі.
  (function(){
    const cal = document.getElementById('cal');
    const grid = document.getElementById('calGrid');
    const input = document.getElementById('date');
    if (!cal || !grid || !input) return;

    const mLabel = document.getElementById('calMonth');
    const yLabel = document.getElementById('calYear');
    const foot = document.getElementById('calFoot');
    const monthName = new Intl.DateTimeFormat(I18N.locale, { month: 'long' });

    const today = new Date(); today.setHours(0,0,0,0);
    const iso = (d) => d.getFullYear() + '-' +
      String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');

    // Сітка календаря минулі дні гасить, а нативне поле під нею приймало будь-що.
    // Атрибут ставимо звідси, а не в розмітці: «сьогодні» протухає щоночі, і тут
    // воно вже пораховано за локальним часом, без зсуву UTC.
    input.min = iso(today);
    const parse = (v) => {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || '');
      if (!m) return null;
      const d = new Date(+m[1], +m[2]-1, +m[3]);
      return isNaN(d) ? null : d;
    };

    let selected = parse(input.value);
    let view = new Date((selected || today).getFullYear(), (selected || today).getMonth(), 1);

    function render(){
      mLabel.textContent = monthName.format(view);
      yLabel.textContent = view.getFullYear();

      // Понеділок — перший: getDay() дає 0 для неділі, тож зсуваємо.
      const first = new Date(view.getFullYear(), view.getMonth(), 1);
      const lead = (first.getDay() + 6) % 7;
      const start = new Date(first); start.setDate(1 - lead);

      grid.textContent = '';
      const frag = document.createDocumentFragment();
      for (let i = 0; i < 42; i++){
        const d = new Date(start); d.setDate(start.getDate() + i);
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'cal-day';
        b.tabIndex = -1;                    // клавіатурний шлях — саме поле дати
        b.textContent = d.getDate();
        if (d.getMonth() !== view.getMonth()) b.classList.add('other');
        else if (d < today) b.classList.add('past');
        if (+d === +today) b.classList.add('today');
        if (selected && +d === +selected) b.classList.add('sel');
        b.dataset.d = iso(d);
        frag.appendChild(b);
      }
      grid.appendChild(frag);
    }

    grid.addEventListener('click', (e) => {
      const b = e.target.closest('.cal-day');
      if (!b || b.classList.contains('other') || b.classList.contains('past')) return;
      selected = parse(b.dataset.d);
      input.value = b.dataset.d;
      input.dispatchEvent(new Event('change', { bubbles: true }));
      foot.textContent = I18N.cal.foot + new Intl.DateTimeFormat(I18N.locale,
        { day: 'numeric', month: 'long', year: 'numeric' }).format(selected);
      render();
    });

    document.getElementById('calPrev').addEventListener('click', () => {
      view = new Date(view.getFullYear(), view.getMonth() - 1, 1); render();
    });
    document.getElementById('calNext').addEventListener('click', () => {
      view = new Date(view.getFullYear(), view.getMonth() + 1, 1); render();
    });

    // якщо дату ввели в саме поле — календар підхоплює її
    input.addEventListener('change', () => {
      const d = parse(input.value);
      if (!d || (selected && +d === +selected)) return;
      selected = d;
      view = new Date(d.getFullYear(), d.getMonth(), 1);
      render();
    });

    render();
  })();

  // ---- Вирівнювання панелі календаря під поля форми ----
  // Верх .cal лягає на верхній край самого поля вводу «Скільки гостей» (на
  // рівень <select>, а не його підпису над ним), низ .cal — на нижній край
  // кнопки «Надіслати заявку» (сама панель, не тільки текст усередині неї).
  // Рахуємо в JS, а не фіксованими відступами: набір полів праворуч не
  // сталий (з'являється підказка з калькулятора, може дописатись поле), і
  // будь-який зашитий відступ тут же розійшовся б із сусідньою колонкою —
  // так і сталось, коли додали поле «Як ви про нас дізналися».
  (function(){
    const cal = document.getElementById('cal');
    const guests = document.getElementById('guests');
    const dateField = document.getElementById('date');
    const submit = document.getElementById('submitBtn');
    const formRight = document.querySelector('.form-right');
    if (!cal || !guests || !submit || !formRight) return;

    // На планшеті ліва колонка коротша, і календар природно опиняється вже
    // нижче за «Скільки гостей» — прив'язка до нього там не робить нічого
    // (margin-top уміє тільки опускати панель, не піднімати), і верх календаря
    // повисає між полями. Тому на цій ширині рівняємо його на «Бажану дату» —
    // поле, яке календар і дублює.
    const calNarrow = window.matchMedia('(max-width: 1100px)');
    const topAnchor = () => (calNarrow.matches && dateField) ? dateField : guests;

    function alignCalendarToForm(){
      if (getComputedStyle(cal).display === 'none') return; // ховається нижче 761px
      cal.style.marginTop = '0px';
      cal.style.height = 'auto';
      const calTop = cal.getBoundingClientRect().top;
      const anchorTop = topAnchor().getBoundingClientRect().top;
      const submitBottom = submit.getBoundingClientRect().bottom;
      const marginTop = Math.max(0, anchorTop - calTop);
      cal.style.marginTop = marginTop + 'px';
      const height = submitBottom - (calTop + marginTop);
      if (height > 0) cal.style.height = height + 'px';
    }

    alignCalendarToForm();
    if (document.fonts && document.fonts.ready){ document.fonts.ready.then(alignCalendarToForm); }

    let alignW = window.innerWidth;
    window.addEventListener('resize', () => {
      if (window.innerWidth === alignW) return;
      alignW = window.innerWidth;
      alignCalendarToForm();
    });
    // Перехід через 1100px міняє саму точку прив'язки, а не лише розміри.
    if (calNarrow.addEventListener) calNarrow.addEventListener('change', alignCalendarToForm);
    else calNarrow.addListener(alignCalendarToForm);

    // Ловить будь-яку зміну висоти правої колонки — підказку з калькулятора,
    // майбутнє поле, перенесення довгого лейбла на другий рядок — без
    // прив'язки до конкретного місця в коді, яке цю висоту міняє.
    if (window.ResizeObserver){
      let raf = null;
      new ResizeObserver(() => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(alignCalendarToForm);
      }).observe(formRight);
    }
  })();

  // ---- FAQ accordion ----
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    const a = item.querySelector('.faq-a');
    const toggle = () => {
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach(other => {
        if (other !== item) {
          other.classList.remove('open');
          other.querySelector('.faq-a').style.maxHeight = null;
          other.querySelector('.faq-q').setAttribute('aria-expanded', 'false');
        }
      });
      if (isOpen) {
        item.classList.remove('open');
        a.style.maxHeight = null;
      } else {
        item.classList.add('open');
        a.style.maxHeight = a.scrollHeight + 'px';
      }
      // Плюсик, що обертається в хрестик, бачить лише той, хто дивиться на
      // екран. Читач з озвучкою дізнається про стан пункту тільки звідси.
      q.setAttribute('aria-expanded', String(!isOpen));
    };
    q.addEventListener('click', toggle);
    q.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });
  });

  // ---- GA4: cta_click ----
  // Делеговано на document, тому працює для всіх чотирьох CTA одним
  // обробником і не заважає стандартній навігації (#book і далі саме
  // скролить, click тут лише додатково фіксує подію). closest() підіймається
  // й крізь <span class="lbl-wide/lbl-tight"> усередині hero-кнопки.
  document.addEventListener('click', (e) => {
    const cta = e.target.closest('[data-cta]');
    if (cta && typeof gtag === 'function') {
      gtag('event', 'cta_click', { cta_name: cta.dataset.cta });
    }
  });

  // ---- GA4: form_start ----
  // Спрацьовує рівно раз за завантаження сторінки, у момент, коли гість
  // реально починає вводити текст у перше поле форми («Ім'я») — не на фокус
  // (можна просто клікнути й передумати), а на перший символ. Жодних значень
  // полів у подію не йде.
  (function initFormStartTracking(){
    let formStartSent = false;
    const firstField = document.getElementById('name');
    if (!firstField) return;
    firstField.addEventListener('input', () => {
      if (formStartSent || typeof gtag !== 'function') return;
      formStartSent = true;
      gtag('event', 'form_start');
    });
  })();

  // ---- Form: integrate with Google Apps Script ----
  (function initLeadTracking(){
    function parseUTM(){
      const params = new URLSearchParams(window.location.search);
      return {
        utmSource: params.get('utm_source') || '',
        utmMedium: params.get('utm_medium') || '',
        utmCampaign: params.get('utm_campaign') || '',
      };
    }
    function getTechData(){
      const ua = navigator.userAgent;
      let device = 'desktop', os = '', browser = '';
      if (/mobile|android|iphone|ipod|blackberry/i.test(ua)) device = 'mobile';
      if (/iphone|mac os/i.test(ua)) os = 'iOS';
      else if (/android/i.test(ua)) os = 'Android';
      else if (/win/i.test(ua)) os = 'Windows';
      else if (/linux/i.test(ua)) os = 'Linux';
      if (/chrome/i.test(ua)) browser = 'Chrome';
      else if (/firefox/i.test(ua)) browser = 'Firefox';
      else if (/safari/i.test(ua) && !/chrome/i.test(ua)) browser = 'Safari';
      else if (/edge/i.test(ua)) browser = 'Edge';
      return { device, os, browser };
    }
    function generateLeadId(){
      return 'lead_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    const utm = parseUTM();
    const tech = getTechData();
    sessionStorage.setItem('lead_utm', JSON.stringify(utm));
    sessionStorage.setItem('lead_tech', JSON.stringify(tech));
    sessionStorage.setItem('lead_id', generateLeadId());
  })();

  // ---- Світло за курсором у секціях із плямами ----
  // Ланцюг круглих ланок: перша тягнеться до курсора, кожна наступна — до
  // попередньої. Ні обертання, ні розтягу вздовж руху тут немає свідомо: це
  // трансформації твердого тіла, і саме через них шлейф читався жорстким на
  // поворотах. У кола орієнтації немає, тож форму стрічки цілком малює те, де
  // ланки стоять.
  //
  // Рух — не лінійне наближення, а пружина. Проста інтерполяція (x += (ціль-x)
  // * k) завжди тільки гальмує до цілі й ніколи її не проходить, через що рух
  // виходить рівний і механічний. Пружина з тертям дає невеликий перехід за
  // ціль і заспокоєння — на повороті хвіст заносить по дузі, як і має бути в
  // чогось гнучкого.
  //
  // Елементи створюються звідси, а не лежать у розмітці: на телефоні курсора
  // немає, і зайві вузли там ні до чого.
  (function(){
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const LINKS = 14;
    // Жорсткість пружини і тертя. Числа не на око: у дискретної пружини
    // v = (v + (ціль - x) * k) * d характеристичні корені комплексні, коли
    // (1 + d(1-k))^2 < 4d — а комплексні корені означають резонанс, тобто
    // підсилення на власній частоті. Для однієї плями це просто приємний
    // перехід за ціль, але тут ЛАНЦЮГ: кожна ланка ганяється за попередньою,
    // і підсилення множиться чотирнадцять разів. На k 0.22 / d 0.74 воно й
    // розносило шлейф — заміряно, ланцюг розтягувало на десятки тисяч
    // пікселів.
    // Тому ланки взяті трохи ЗА межею резонансу (корені дійсні): кожна
    // працює як фільтр із коефіцієнтом не більше одиниці, і каскад не
    // розгойдується.
    // Голова гониться за курсором, а не за іншою пружиною, тож каскаду там
    // немає — їй лишений легкий перехід за ціль, який і дає плавність.
    const HEAD_K = 0.10, HEAD_D = 0.62;
    const LINK_K = 0.15, LINK_D = 0.50;
    // Страхувальний стелаж на випадок, якщо якийсь кадр вийде аномально
    // довгим: без нього один стрибок здатен викинути ланку за екран.
    const MAX_V = 140;

    // Розрідження рідини: м'якша пружина, ніж у шлейфу, тож воно помітно
    // відстає від світла.
    const VOID_K = 0.07, VOID_D = 0.70;

    // ---- Який колір рідини зараз під курсором ----
    // Поле рідини — це кілька тайльованих радіальних градієнтів на двох шарах,
    // що обертаються. Колір у точці з нього можна не вгадувати, а порахувати:
    // знімаємо з точки поточні rotate і scale шару (вони читаються з
    // обчисленого стилю псевдоелемента, тож фаза завжди справжня, а не
    // відтворена з таймера), заводимо її в систему плитки й дивимось відстань
    // до центру найближчої плитки.
    //
    // Параметри шарів НЕ зашиті числами, а розбираються з того самого
    // обчисленого стилю. Плашка гарантії має власні розміри плитки й власну
    // прозорість, і будь-яка копія констант тут рано чи пізно розійшлася б із
    // CSS — тоді підказка про колір почала б брехати, а це гірше, ніж її
    // відсутність.
    const PSEUDO = 1.9;   // inset: -45% з обох боків

    function розібратиШари(cs){
      const sizes = cs.backgroundSize.split(',').map(v => parseFloat(v));
      const poss  = cs.backgroundPosition.split(',').map(v => v.trim().split(/\s+/).map(parseFloat));
      // Кома всередині rgba() не роздільник, тож ріжемо лише перед самим
      // radial-gradient.
      const grads = cs.backgroundImage.split(/,(?=\s*radial-gradient)/);
      const out = [];
      for (let i = 0; i < grads.length; i++){
        const col = grads[i].match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
        const stop = grads[i].match(/([\d.]+)%\s*\)\s*$/);
        if (!col || !sizes[i]) continue;
        out.push({
          size: sizes[i],
          bx: (poss[i] && poss[i][0]) || 0,
          by: (poss[i] && poss[i][1]) || 0,
          alpha: col[4] === undefined ? 1 : parseFloat(col[4]),
          stop: stop ? parseFloat(stop[1]) / 100 : 0.55,
          // Лайм від малинового відрізняємо за каналами: у лайму зелений
          // більший за червоний, у малинового навпаки.
          lime: +col[2] > +col[1]
        });
      }
      return out;
    }

    function полеВТочці(z, W, H, px, py){
      const pw = W * PSEUDO, ph = H * PSEUDO;
      const cx = W / 2, cy = H / 2;
      let lime = 0, mag = 0;
      for (let n = 0; n < 2; n++){
        const cs = getComputedStyle(z.liq, n ? '::after' : '::before');
        if (cs.display === 'none') continue;          // на телефоні другого шару немає
        if (!z.layers[n]) z.layers[n] = розібратиШари(cs);
        const rot = (parseFloat(cs.rotate) || 0) * Math.PI / 180;
        const sc  = parseFloat(cs.scale) || 1;
        const w   = n ? 0.55 : 1;                     // opacity другого шару
        const vx = (px - cx) / sc, vy = (py - cy) / sc;
        const lx = vx * Math.cos(-rot) - vy * Math.sin(-rot) + pw / 2;
        const ly = vx * Math.sin(-rot) + vy * Math.cos(-rot) + ph / 2;
        for (const L of z.layers[n]){
          const tw = pw * L.size / 100, th = ph * L.size / 100;
          const ox = (pw - tw) * L.bx / 100, oy = (ph - th) * L.by / 100;
          const u = (((lx - ox) % tw) + tw) % tw - tw / 2;
          const v = (((ly - oy) % th) + th) % th - th / 2;
          const f = 1 - Math.hypot(u, v) / (Math.hypot(tw, th) / 2 * L.stop);
          if (f <= 0) continue;
          if (L.lime) lime += L.alpha * f * w; else mag += L.alpha * f * w;
        }
      }
      return lime - mag;    // >0 під курсором лайм, <0 малиновий
    }

    // Колір шлейфу — протилежний до того, що під ним. Змішування плавне, тож
    // перехід читається як перетікання, а не як перемикання.
    const LIME = [198, 255, 0], ACID = [255, 20, 120];

    const zones = [];
    document.querySelectorAll('.benefits-aurora, .uc-aurora, .band-aurora, .cover-aurora').forEach(box => {
      // Порядок важливий: розрідження додається ПЕРШИМ, тож ланки шлейфу
      // лягають поверх нього, а не зникають під ним.
      const hole = document.createElement('span');
      hole.className = 'aurora-void';
      box.appendChild(hole);

      const links = [];
      for (let i = 0; i < LINKS; i++){
        const el = document.createElement('span');
        el.className = 'aurora-pointer p' + (i + 1);
        box.appendChild(el);
        links.push({ el, x: 0, y: 0, vx: 0, vy: 0 });
      }
      // Розміри ланок у CSS розраховані на секцію заввишки близько 1040px.
      // Плашка гарантії вп'ятеро нижча, і в ній ті самі кола були б більші за
      // неї саму — тож масштабуємо їх під висоту коробки, але не менше 0.55:
      // при 0.26 слід виходив діаметром ~100px і губився в розмитті.
      const k = Math.min(1, Math.max(0.55, box.getBoundingClientRect().height / 1040));
      zones.push({ box, links, hole: { el: hole, x: 0, y: 0, vx: 0, vy: 0 },
                   liq: box.querySelector('.aurora-liquid'),
                   layers: [null, null],   // розбираються з CSS при першому зніманні
                   k,
                   mix: 0,        // 0 — малиновий шлейф, 1 — лаймовий
                   frame: 0,
                   placed: false, vis: false, on: false });
    });
    if (!zones.length) return;

    let mx = -1, my = -1, raf = 0;
    const wake = () => { if (!raf) raf = requestAnimationFrame(tick); };
    window.addEventListener('pointermove', (e) => { mx = e.clientX; my = e.clientY; wake(); }, { passive: true });

    const io = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        const z = zones.find(v => v.box === en.target);
        if (z) z.vis = en.isIntersecting;
      });
      wake();
    }, { rootMargin: '150px 0px' });
    zones.forEach(z => io.observe(z.box));

    function tick(){
      raf = 0;
      let alive = false;
      for (const z of zones){
        if (!z.vis){
          if (z.on){ z.on = false; z.links.forEach(l => l.el.classList.remove('on')); }
          continue;
        }
        const r = z.box.getBoundingClientRect();
        const inside = mx >= r.left && mx <= r.right && my >= r.top && my <= r.bottom;
        const tx = mx - r.left, ty = my - r.top;

        if (inside){
          // Перший кадр ставимо весь ланцюг під курсор, інакше він летів би
          // туди через пів секції, і вхід у блок читався б як ривок.
          if (!z.placed){
            z.links.forEach(l => { l.x = tx; l.y = ty; l.vx = 0; l.vy = 0; });
            z.hole.x = tx; z.hole.y = ty; z.hole.vx = 0; z.hole.vy = 0;
            z.placed = true;
          }
          if (!z.on){
            z.on = true;
            z.links.forEach(l => l.el.classList.add('on'));
            z.hole.el.classList.add('on');
          }
        } else if (z.on){
          z.on = false;
          z.links.forEach(l => l.el.classList.remove('on'));
          z.hole.el.classList.remove('on');
        }

        // Колір шлейфу — протилежний до рідини під курсором. Поле знімаємо не
        // щокадру: getComputedStyle псевдоелемента змушує браузер перерахувати
        // стилі, а поле й так рухається повільно — раз на чотири кадри більш
        // ніж досить. Саме змішування при цьому йде щокадру, тож перехід
        // лишається плавним.
        if (inside && z.liq && (z.frame++ & 3) === 0){
          const знак = полеВТочці(z, r.width, r.height, tx, ty);
          z.target = знак > 0 ? 0 : 1;   // під лаймом → малиновий шлейф, і навпаки
        }
        if (z.target !== undefined){
          z.mix += (z.target - z.mix) * 0.035;   // ~1.5s на повний перехід
          const c = [0,1,2].map(i => Math.round(ACID[i] + (LIME[i] - ACID[i]) * z.mix));
          z.box.style.setProperty('--trail-rgb', c.join(', '));
          if (Math.abs(z.target - z.mix) > 0.003) alive = true;
        }

        // Розрідження. Що швидше веде миша, то ширше розступається рідина.
        const hl = z.hole;
        hl.vx = (hl.vx + (tx - hl.x) * VOID_K) * VOID_D;
        hl.vy = (hl.vy + (ty - hl.y) * VOID_K) * VOID_D;
        if (hl.vx > MAX_V) hl.vx = MAX_V; else if (hl.vx < -MAX_V) hl.vx = -MAX_V;
        if (hl.vy > MAX_V) hl.vy = MAX_V; else if (hl.vy < -MAX_V) hl.vy = -MAX_V;
        hl.x += hl.vx; hl.y += hl.vy;
        const hsp = Math.hypot(hl.vx, hl.vy);
        const hsc = (1 + Math.min(hsp / 30, 1) * 0.42) * z.k;
        hl.el.style.transform =
          'translate3d(' + hl.x.toFixed(1) + 'px,' + hl.y.toFixed(1) + 'px,0) ' +
          'translate(-50%,-50%) scale(' + hsc.toFixed(3) + ')';
        if (hsp > 0.25 || Math.abs(tx - hl.x) > 0.4 || Math.abs(ty - hl.y) > 0.4) alive = true;

        for (let i = 0; i < z.links.length; i++){
          const l = z.links[i];
          const ax = i === 0 ? tx : z.links[i - 1].x;
          const ay = i === 0 ? ty : z.links[i - 1].y;
          const k = i === 0 ? HEAD_K : LINK_K;
          const damp = i === 0 ? HEAD_D : LINK_D;

          l.vx = (l.vx + (ax - l.x) * k) * damp;
          l.vy = (l.vy + (ay - l.y) * k) * damp;
          if (l.vx > MAX_V) l.vx = MAX_V; else if (l.vx < -MAX_V) l.vx = -MAX_V;
          if (l.vy > MAX_V) l.vy = MAX_V; else if (l.vy < -MAX_V) l.vy = -MAX_V;
          l.x += l.vx;
          l.y += l.vy;

          // Рівномірний масштаб від швидкості: на різкому русі стрічка худне,
          // як струмінь, що витягується. По обох осях однаково, тож напрямку
          // в ланки не з'являється.
          const sp = Math.hypot(l.vx, l.vy);
          const sc = (1 - Math.min(sp / 34, 1) * 0.26) * z.k;
          l.el.style.transform =
            'translate3d(' + l.x.toFixed(1) + 'px,' + l.y.toFixed(1) + 'px,0) ' +
            'translate(-50%,-50%) scale(' + sc.toFixed(3) + ')';

          if (sp > 0.25 || Math.abs(ax - l.x) > 0.4 || Math.abs(ay - l.y) > 0.4) alive = true;
        }
      }
      if (alive) raf = requestAnimationFrame(tick);
    }
  })();

  // ---- Лайтбокс-карусель для роликів галереї ----
  (function(){
    const box  = document.getElementById('vbox');
    if (!box) return;
    // Стрічка галереї є тільки на головній. Сторінки досвідів дають той самий
    // список окремим прихованим вузлом: він не має класу .gallery-grid, тож
    // його не чіпає ні оформлення стрічки, ні її клонування.
    const grid = document.getElementById('galGrid');
    const listSrc = grid || document.getElementById('vboxList');
    if (!listSrc) return;
    const stage  = document.getElementById('vboxStage');
    const dots   = document.getElementById('vboxDots');
    const toggle = document.getElementById('vboxToggle');
    const prevB  = document.getElementById('vboxPrev');
    const nextB  = document.getElementById('vboxNext');

    let list = [], slides = [], active = -1, lastFocus = null, built = false;

    // Список збирається зі самої стрічки, а не дублюється окремим масивом:
    // джерело правди лишається одне. Стрічка клонується в пʼять копій, тож
    // дублікати відсіюємо за адресою файлу.
    function collect(){
      const seen = new Set();
      list = [];
      listSrc.querySelectorAll('.gal-play').forEach(b => {
        const src = b.dataset.video;
        if (!src || seen.has(src)) return;
        seen.add(src);
        list.push({ src, poster: b.dataset.poster || '' });
      });
    }

    function build(){
      slides = list.map((item, i) => {
        const s = document.createElement('div');
        s.className = 'vbox-slide';
        if (item.poster) s.style.backgroundImage = 'url("' + item.poster + '")';
        const v = document.createElement('video');
        v.playsInline = true;
        v.preload = 'none';
        s.appendChild(v);
        // Клік по сусідньому слайду робить його активним. Активний не слухаємо:
        // інакше пауза ловилася б кліком повз кнопку.
        s.addEventListener('click', () => { if (!s.classList.contains('is-active')) go(i); });
        stage.appendChild(s);
        return s;
      });
      list.forEach((_, i) => {
        const d = document.createElement('button');
        d.type = 'button'; d.className = 'vbox-dot';
        d.setAttribute('aria-label', I18N.video.clip(i + 1));
        d.addEventListener('click', () => go(i));
        dots.appendChild(d);
      });
      // Зони тапу для телефона. На десктопі їх ховає CSS — там для того самого
      // є стрілки й самі сусідні слайди.
      [['prev', I18N.video.prev], ['next', I18N.video.next]].forEach(([dir, label]) => {
        const t = document.createElement('button');
        t.type = 'button';
        t.className = 'vbox-tap vbox-tap-' + dir;
        t.setAttribute('aria-label', label);
        t.addEventListener('click', () => {
          if (swiped) { swiped = false; return; }   // свайп уже перемкнув
          go(active + (dir === 'next' ? 1 : -1));
        });
        box.appendChild(t);
      });
      built = true;
    }

    function stop(i){
      if (i < 0 || !slides[i]) return;
      const v = slides[i].querySelector('video');
      v.pause();
      // Знімаємо джерело й перезавантажуємо: інакше закритий ролик лишається в
      // памʼяті й далі тримає буфер. Шість роликів по 5-7 МБ це помітно.
      v.removeAttribute('src');
      v.load();
    }

    function go(i){
      if (i < 0 || i >= list.length || i === active) return;
      stop(active);
      active = i;
      slides.forEach((s, k) => {
        const off = k - active;
        s.style.setProperty('--off', off);
        // Тримаємо в кадрі активний і по одному сусіду: далі вони все одно за
        // краєм екрана, а кожен зайвий шар — ще одна велика картинка в памʼяті.
        if (Math.abs(off) <= 1) s.dataset.near = String(Math.abs(off));
        else delete s.dataset.near;
        s.classList.toggle('is-active', k === active);
      });
      const v = slides[active].querySelector('video');
      v.src = list[active].src;
      v.play().catch(() => {});
      Array.prototype.forEach.call(dots.children, (d, k) => d.classList.toggle('is-on', k === active));
      prevB.disabled = active === 0;
      nextB.disabled = active === list.length - 1;
    }

    function open(src){
      if (!built) { collect(); build(); }
      lastFocus = document.activeElement;
      box.classList.add('show');
      box.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      const i = list.findIndex(x => x.src === src);
      active = -1;
      go(i < 0 ? 0 : i);
    }
    function close(){
      stop(active);
      box.classList.remove('show', 'playing');
      box.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      active = -1;
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    // Делегування: стрічка клонується, слухачі на самих кнопках cloneNode не
    // переносить.
    // Ловимо всю плитку, а не саму кнопку: у кадр 600x968 цілитися кнопкою
    // 64 px незручно, надто з телефона. Кнопка лишається як позначка «тут відео».
    // scrollLeft звіряємо, бо стрічка горизонтальна: палець, що дотягнув її й
    // зупинився на плитці, не повинен відкривати ролик.
    let gx = 0;
    if (grid) {
    grid.addEventListener('pointerdown', () => { gx = grid.scrollLeft; }, { passive: true });
    grid.addEventListener('click', (e) => {
      const item = e.target.closest('.gallery-item.is-video');
      if (!item) return;
      const btn = item.querySelector('.gal-play');
      if (!btn) return;
      e.preventDefault();
      if (Math.abs(grid.scrollLeft - gx) > 8) return;
      open(btn.dataset.video);
    });
    }

    // Кнопка поза стрічкою. Сторінки досвідів не мають власної галереї, але
    // відкривають ту саму карусель зі свого блоку: список вони оголошують
    // прихованим #galGrid, а сюди приходять лише за відкриттям. Порожній
    // data-vbox-open означає «з першого ролика» — open() сам так і зробить.
    document.addEventListener('click', (e) => {
      const t = e.target.closest('[data-vbox-open]');
      if (!t) return;
      e.preventDefault();
      open(t.getAttribute('data-vbox-open') || '');
    });

    toggle.addEventListener('click', () => {
      const v = slides[active] && slides[active].querySelector('video');
      if (!v) return;
      v.paused ? v.play().catch(() => {}) : v.pause();
    });
    // play і pause не спливають, тож слухаємо на фазі перехоплення.
    stage.addEventListener('play',  (e) => { if (e.target.tagName === 'VIDEO') box.classList.add('playing'); }, true);
    stage.addEventListener('pause', (e) => { if (e.target.tagName === 'VIDEO') box.classList.remove('playing'); }, true);
    // Як у сторіз: доглянув — поїхали далі. На останньому просто зупиняємось.
    stage.addEventListener('ended', () => { if (active < list.length - 1) go(active + 1); }, true);

    prevB.addEventListener('click', () => go(active - 1));
    nextB.addEventListener('click', () => go(active + 1));
    document.getElementById('vboxClose').addEventListener('click', close);
    document.getElementById('vboxBackdrop').addEventListener('click', close);
    // Порожнє поле навколо слайдів. Сцена лежить поверх фону на всю площу, тож
    // до самого фону клік не дійшов би — перевіряємо, що поцілили саме в неї,
    // а не в слайд. На телефоні цього не стається: там зверху зони тапу.
    stage.addEventListener('click', (e) => {
      if (e.target !== stage) return;
      if (swiped) { swiped = false; return; }
      close();
    });

    // Свайп. Слухаємо на фазі перехоплення й на самому вікні, а не на сцені:
    // зверху лежать зони тапу, і до сцени подія просто не дійшла б.
    let px = 0, py = 0, swiped = false;
    box.addEventListener('pointerdown', (e) => { px = e.clientX; py = e.clientY; swiped = false; }, { passive: true, capture: true });
    box.addEventListener('pointerup', (e) => {
      const dx = e.clientX - px, dy = e.clientY - py;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) {
        swiped = true;
        go(active + (dx < 0 ? 1 : -1));
      }
    }, { passive: true, capture: true });

    document.addEventListener('keydown', (e) => {
      if (!box.classList.contains('show')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') go(active + 1);
      else if (e.key === 'ArrowLeft') go(active - 1);
    });
  })();


  // ---- Спливне вікно подяки поверх formSuccess ----
  // Незалежний шар: formSuccess у формі лишається як був, це вікно лише
  // додається поверх нього після відправки й закривається окремо, ніяк
  // не впливаючи на форму чи на дані, що вже пішли в Google Sheets.
  (function () {
    const modal = document.getElementById('leadModal');
    const backdrop = document.getElementById('leadModalBackdrop');
    const closeBtn = document.getElementById('leadModalClose');
    if (!modal) return;

    // Дата з форми повертається людині назад. Це не декор: при одному
    // комплекті на вечір дата і є вся угода, і побачити її написаною — єдине
    // справжнє підтвердження, що заявку зрозуміли правильно. Дата
    // необов'язкова, тож коли її не вказали, рядка просто немає — вигадувати
    // замість неї нічого.
    //
    // Формат дає Intl за локаллю сторінки, тим самим викликом, що в підписі
    // календаря вище: 'T00:00:00' у розборі — щоб рядок YYYY-MM-DD читався як
    // місцева дата, а не як UTC, інакше на схід від Гринвіча підставлявся б
    // попередній день.
    const dateInput = document.getElementById('date');
    const dateRows = document.querySelectorAll('[data-checking-date]');
    function fillLeadDate() {
      const v = dateInput && dateInput.value;
      const d = v ? new Date(v + 'T00:00:00') : null;
      const ok = d && !isNaN(d) && I18N.form && I18N.form.checking;
      const html = ok ? I18N.form.checking(new Intl.DateTimeFormat(I18N.locale,
        { day: 'numeric', month: 'long', year: 'numeric' }).format(d)) : '';
      dateRows.forEach(row => {
        if (ok) row.innerHTML = html;
        row.hidden = !ok;
      });
    }
    // Підтвердження всередині форми показується навіть тоді, коли вікно поверх
    // сторінки закрили, тож рядок дати мусить заповнитись і для нього.
    window.__fillCheckingDate = fillLeadDate;

    function openLeadModal() {
      fillLeadDate();
      modal.classList.add('show');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
    function closeLeadModal() {
      modal.classList.remove('show');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
    window.__openLeadModal = openLeadModal;

    closeBtn.addEventListener('click', closeLeadModal);
    backdrop.addEventListener('click', closeLeadModal);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('show')) closeLeadModal();
    });
  })();

  // ---- Спільне для надісланої й недописаної заявки ----
  // Обидва шляхи мусять слати рівно ті самі поля в тому самому порядку: у
  // таблиці колонки фіксовані, і зайве або відсутнє поле зсуває рядок.
  const LEAD_URL = 'https://script.google.com/macros/s/AKfycbwdSqc1-M0KmHBwIE8_EANY7dbPbqVcOmdTbl-gfDxyASabYJXW55mGQIXhlOBRRLwS/exec';

  function buildLead(name, contact, status){
    const val = (id) => { const el = document.getElementById(id); return el ? el.value : ''; };
    const lead = {
      name: name,
      contact: contact,
      eventType: val('type'),
      guests: val('guests'),
      eventDate: val('date'),
      discovery: val('source'),
      comment: (val('comment') || '').trim(),
      leadId: sessionStorage.getItem('lead_id'),
      submittedDate: new Date().toISOString().split('T')[0],
      submittedTime: new Date().toTimeString().split(' ')[0],
      status: status,
    };
    const utm = JSON.parse(sessionStorage.getItem('lead_utm') || '{}');
    const tech = JSON.parse(sessionStorage.getItem('lead_tech') || '{}');
    Object.assign(lead, utm, tech, {
      referrer: document.referrer || '',
      landingPage: window.location.pathname
    });
    return lead;
  }

  // Уся робота з формою жила на верхньому рівні файла й припускала, що поля
  // існують. На сторінках без форми — як список досвідів — перше ж звертання
  // до неіснуючого поля валило site.js цілком, а з ним і все, що нижче за
  // текстом: поява блоків, стрічка, плаваючий контакт, прапорець __siteJs.
  // Тепер це власна обгортка з перевіркою на вході, як і решта блоків.
  (function(){
    if (!document.getElementById('formError') || !document.getElementById('submitBtn')) return;
    // Захист від дубля generate_lead: форму технічно можна надіслати повторно
    // (кнопка ховається лише після успіху, а не блокується одразу), тож без
    // цього прапорця повторний клік чи гонка подій дали б два events на один лід.
    let leadEventSent = false;

    // alert() забирає фокус у діалог браузера, нічого не каже про те, яке саме
    // поле порожнє, і на телефоні перекриває всю форму. Повідомлення тепер
    // стоїть над кнопкою (role="alert", тож озвучується само), порожні поля
    // позначаються aria-invalid, а фокус іде в перше з них.
    const errBox = document.getElementById('formError');
    const nameEl = document.getElementById('name');
    const contactEl = document.getElementById('contact');

    const dateEl = document.getElementById('date');

    function clearError(){
      errBox.hidden = true;
      errBox.textContent = '';
      nameEl.removeAttribute('aria-invalid');
      contactEl.removeAttribute('aria-invalid');
      dateEl.removeAttribute('aria-invalid');
    }
    [nameEl, contactEl, dateEl].forEach(el => el.addEventListener('input', () => {
      if (!errBox.hidden) clearError();
    }));
    // Дата зі сітки календаря приходить як change, а не input.
    dateEl.addEventListener('change', () => { if (!errBox.hidden) clearError(); });

    // Одне спільне повідомлення казало «вкажіть імʼя і контакт» навіть тоді, коли
    // обидва поля заповнені, а не подобалась дата. Тепер текст називає саме те, що
    // не так, і фокус іде в те саме поле.
    function showError(msg, el){
      clearError();
      errBox.textContent = msg;
      errBox.hidden = false;
      if (el){ el.setAttribute('aria-invalid', 'true'); el.focus(); }
    }

    // Навмисно поблажливо: хибно відхилений живий контакт коштує заявки, а хибно
    // пропущений — лише одного дзвінка в нікуди. Приймаємо три форми, якими люди
    // справді користуються, рівно ті, що обіцяє плейсхолдер поля.
    function contactLooksReal(v){
      const digits = v.replace(/[\s()\-+.]/g, '');
      if (/^\d{9,}$/.test(digits)) return true;
      if (/^@[^\s@]{2,}$/.test(v)) return true;
      return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
    }

    // min на полі відсікає вибір із пікера, але значення можна вписати з клавіатури
    // повз нього — тож те саме правило повторюємо перед надсиланням.
    function isPastDate(v){
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || '');
      if (!m) return false;
      const d = new Date(+m[1], +m[2]-1, +m[3]); d.setHours(0,0,0,0);
      const t = new Date(); t.setHours(0,0,0,0);
      return d < t;
    }

    const submitBtn = document.getElementById('submitBtn');
    const submitLabel = submitBtn.textContent;
    let submitting = false;

    submitBtn.addEventListener('click', () => {
      if (submitting) return;
      const name = nameEl.value.trim();
      const contact = contactEl.value.trim();
      if (!name || !contact){
        clearError();
        errBox.textContent = I18N.form.required;
        errBox.hidden = false;
        if (!name) nameEl.setAttribute('aria-invalid', 'true');
        if (!contact) contactEl.setAttribute('aria-invalid', 'true');
        (!name ? nameEl : contactEl).focus();
        return;
      }
      if (!contactLooksReal(contact)){ showError(I18N.form.contactBad, contactEl); return; }
      if (isPastDate(dateEl.value)){ showError(I18N.form.datePast, dateEl); return; }
      clearError();

      const formData = buildLead(name, contact, 'Нова');
      const utm = JSON.parse(sessionStorage.getItem('lead_utm') || '{}');
      const tech = JSON.parse(sessionStorage.getItem('lead_tech') || '{}');

      const GOOGLE_SCRIPT_URL = LEAD_URL;
      submitting = true;
      submitBtn.disabled = true;
      submitBtn.textContent = I18N.form.sending;

      // Раніше показ успіху стояв наступним рядком після fetch і не залежав від
      // нього взагалі: заявка, яка не доїхала, все одно отримувала «Заявку
      // прийнято». Тепер гілки розходяться.
      //
      // Межу треба знати точно: mode:'no-cors' як не давав прочитати відповідь,
      // так і не дає — помилку на боці Apps Script (500, вичерпана квота,
      // зламаний скрипт) ця перевірка НЕ побачить, такий запит резолвиться
      // непрозоро й піде в .then. Ловиться обрив зв'язку: мертва мережа,
      // заблокований запит, зниклий Wi-Fi. Це і є найчастіший реальний випадок
      // втрати заявки — телефон у дорозі.
      fetch(GOOGLE_SCRIPT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(formData),
        mode: 'no-cors'
      }).then(() => {
        // Клас, а не style.display: поля мусять лишити за собою місце, бо від їхніх
        // прямокутників рахується висота календаря в лівій колонці. Деталі — у
        // коментарі до .form-right у site.css.
        if (typeof window.__fillCheckingDate === 'function') window.__fillCheckingDate();
        document.getElementById('formFields').classList.add('is-sent');
        document.getElementById('formSuccess').classList.add('show');
        if (typeof window.__openLeadModal === 'function') window.__openLeadModal();

        // GA4: generate_lead — саме тут, у гілці успіху, а не одразу після кліку.
        // Подія тепер рахує лише ті надсилання, які реально пішли: у звітах лідів
        // стане трохи менше, і це правдивіша цифра, а не втрата.
        // Жодних персональних даних: ні імʼя, ні контакт, ні коментар сюди не йдуть.
        if (!leadEventSent && typeof gtag === 'function') {
          leadEventSent = true;
          gtag('event', 'generate_lead', {
            event_type: formData.eventType,
            guests: formData.guests,
            discovery: formData.discovery,
            utm_source: utm.utmSource || '',
            utm_medium: utm.utmMedium || '',
            utm_campaign: utm.utmCampaign || '',
            device: tech.device || '',
            os: tech.os || '',
            browser: tech.browser || ''
          });
        }
      }).catch(err => {
        console.error('Помилка при відправці заявки:', err);
        // Введене лишається на місці. Людина вже вибрала дату й дописала коментар —
        // змусити її зробити це вдруге найгірше саме після збою.
        submitting = false;
        submitBtn.disabled = false;
        submitBtn.textContent = submitLabel;
        showError(I18N.form.netFail, null);
      });
    });

  
    // ---- Недописана заявка ----
    // Людина ввела контакт, але пішла, не натиснувши кнопку. Зберігаємо введене
    // зі статусом «Не надіслана», щоб можна було передзвонити. Ця практика
    // описана в політиці конфіденційності — саме тому вона й зʼявилась.
    //
    // sendBeacon, а не fetch: при закритті вкладки браузер обриває звичайні
    // запити, а маячок він зобовʼязаний доставити. fetch з keepalive лишається
    // запасним шляхом для старих рушіїв.
    //
    // visibilitychange, а не beforeunload: на iOS beforeunload не спрацьовує
    // при закритті вкладки взагалі, і саме мобільні випадки губилися б.
    (function(){
      let sentKey = '';

      function maybeSave(){
        if (submitting || leadEventSent) return;          // вже надіслано по-справжньому
        const name = nameEl.value.trim();
        const contact = contactEl.value.trim();
        // Без контакту звертатися нема куди, а кривий контакт — це сміття в
        // таблиці. Той самий поблажливий фільтр, що й на кнопці.
        if (!contact || !contactLooksReal(contact)) return;
        // Один запис на один набір даних: перемикання вкладок туди-сюди не має
        // класти в таблицю десять однакових рядків.
        const key = name + '|' + contact + '|' + (document.getElementById('date') || {}).value;
        if (key === sentKey) return;
        sentKey = key;

        const body = JSON.stringify(buildLead(name, contact, 'Не надіслана'));
        try {
          if (navigator.sendBeacon) {
            navigator.sendBeacon(LEAD_URL, new Blob([body], { type: 'text/plain;charset=utf-8' }));
          } else {
            fetch(LEAD_URL, { method: 'POST', body: body, mode: 'no-cors', keepalive: true,
                              headers: { 'Content-Type': 'text/plain;charset=utf-8' } });
          }
        } catch (e) { /* мовчки: це фоновий запис, він не має нічого ламати */ }
      }

      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') maybeSave();
      });
      window.addEventListener('pagehide', maybeSave);
    })();
  })();

  // ---- Поява плаваючого контакту ----
    // Кнопка чекає, доки людина дійде до середини блоку «Чому silent disco»: у
    // першому вікні вже є лаймова «Перевірити дату», і другий заклик поруч із
    // нею лише ділив би увагу. До того моменту її ховає CSS під html.js.
    (function(){
      const btn = document.querySelector('.tg-float');
      if (!btn) return;
      const idea = document.getElementById('idea');
      // Якщо блоку на сторінці немає, показуємо одразу: краще кнопка без затримки,
      // ніж кнопка, схована назавжди через відсутній орієнтир.
      if (!idea) { btn.classList.add('is-in'); return; }

      let ticking = false;
      function check(){
        ticking = false;
        const r = idea.getBoundingClientRect();
        // Середина блоку піднялась до середини екрана — показуємо. Шлях
        // двонапрямний: повернувшись нагору, людина знову бачить лише
        // лаймову «Перевірити дату», а кнопка не лежить на панелі каналів
        // (на висоті екрана ~780px вона закривала тумблер BLUE).
        const passed = r.top + r.height / 2 <= window.innerHeight / 2;
        btn.classList.toggle('is-in', passed);
      }
      function onScroll(){
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(check);
      }
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll);
      // Сторінку могли відкрити вже прокрученою — переходом за якорем або
      // поверненням назад із відновленою позицією. Перевіряємо двічі: зараз і
      // після load, бо браузер відновлює позицію не обов'язково до цього рядка,
      // а подія scroll при відновленні гарантована не в кожному русі.
      check();
      window.addEventListener('load', check, { once: true });
    })();

  // ---- Мобільна шапка: рідке скло, розʼєднання пігулки при скролі ----
  // На старті шапка — одна пігулка, як і зараз. Після невеликого скролу
  // з'являється nav.nav-split — і вся анімація вище (CSS) розводить капсули,
  // ховає слово «SILENT» за іконку й стискає кнопку, звільняючи місце
  // гамбургеру. Тут же одразу збирається й саме мобільне меню (drawer):
  // посилання клонуються з .nav-links поточної сторінки (вони вже правильні
  // для неї — інших досвідів на сторінці корпоративів, якорів на головній),
  // перемикач мов — так само клон, лише якщо він узагалі є в шапці (є не на
  // кожній сторінці — переклад поки тільки в головної й 404).
  (function(){
    const nav = document.querySelector('body > nav');
    if (!nav) return;
    const logo = nav.querySelector('.logo');
    const navLinks = nav.querySelector('.nav-links');
    const cta = navLinks && navLinks.querySelector('.nav-cta');
    if (!logo || !navLinks || !cta) return;

    // --- Іконка + слово всередині .logo ---
    if (!logo.querySelector('.logo-icon')){
      const iconWrap = document.createElement('span');
      iconWrap.className = 'logo-icon';
      iconWrap.setAttribute('aria-hidden', 'true');
      const img = document.createElement('img');
      img.src = '/images/silent-mark.webp';
      img.alt = '';
      img.width = 24; img.height = 24;
      img.loading = 'eager'; img.decoding = 'async';
      iconWrap.appendChild(img);
      logo.insertBefore(iconWrap, logo.firstChild);

      const word = document.createElement('span');
      word.className = 'logo-word';
      while (logo.childNodes.length > 1) word.appendChild(logo.childNodes[1]);
      logo.appendChild(word);
    }

    // --- Гамбургер одразу після кнопки дати ---
    let burger = navLinks.querySelector('.nav-burger');
    if (!burger){
      burger = document.createElement('button');
      burger.type = 'button';
      burger.className = 'nav-burger';
      burger.setAttribute('aria-label', 'Меню');
      burger.setAttribute('aria-haspopup', 'true');
      burger.setAttribute('aria-expanded', 'false');
      burger.setAttribute('aria-controls', 'navDrawer');
      burger.innerHTML = '<span class="nav-burger-lines" aria-hidden="true"><span></span><span></span><span></span></span>';
      navLinks.appendChild(burger);
    }

    // --- Розʼєднання при скролі: за напрямком свайпу, не за позицією ---
    // SPLIT_AT — не сам поріг перемикання, а «мертва зона» біля самого
    // верху сторінки: нижче неї пігулка завжди суцільна, незалежно від
    // напрямку, — інакше перший же дрібний свайп одразу розʼєднував би
    // шапку ще до того, як під нею взагалі зʼявився прокручений контент.
    // Вище цієї зони власник попросив реагувати на НАПРЯМОК руху, а не на
    // абсолютну позицію: свайп униз (у будь-якому місці сторінки) звужує
    // шапку до капсул, свайп угору — повертає суцільну пігулку, навіть якщо
    // сторінка як і раніше прокручена на тисячі пікселів. anchorY — точка
    // відліку напрямку: посувається слідом за скролом у той бік, куди він
    // щойно підтвердився, тож щоб перемкнути стан назад, завжди треба
    // проскролити DIR_THRESHOLD пікселів у зворотний бік від останнього
    // руху, а не від точки, де курс почався кілька екранів тому.
    const SPLIT_AT = 64;
    const DIR_THRESHOLD = 14;
    let split = false;
    let anchorY = 0;
    let morphTimer = null;
    function setSplit(on){
      if (on === split) return;
      split = on;
      nav.classList.add('is-morphing');
      nav.classList.toggle('nav-split', split);
      clearTimeout(morphTimer);
      morphTimer = setTimeout(() => nav.classList.remove('is-morphing'), 520);
    }
    let ticking = false;
    function check(){
      ticking = false;
      const y = window.scrollY;
      if (y <= SPLIT_AT){
        setSplit(false);
        anchorY = y;
        return;
      }
      if (y - anchorY > DIR_THRESHOLD){
        setSplit(true);
        anchorY = y;
      } else if (anchorY - y > DIR_THRESHOLD){
        setSplit(false);
        anchorY = y;
      }
    }
    function onScroll(){
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(check);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    check();

    // --- Меню-панель (drawer) ---
    if (document.getElementById('navDrawer')) return;
    const drawer = document.createElement('div');
    drawer.className = 'nav-drawer';
    drawer.id = 'navDrawer';

    // Прохід іде по прямих дітях .nav-links, не по всіх <a> всередині:
    // .nav-item-mega несе власну десктопну mega-панель із пʼятьма
    // посиланнями-категоріями (.nav-mega-cat) — плаский querySelectorAll('a')
    // підхопив би і їх, розсипавши мобільне меню зайвими пунктами. Той самий
    // .nav-item-mega тут розгортається в один пункт-акордеон: сам напис
    // веде на /faq/, стрілка поруч розкриває ті ж пʼять розділів підпунктами
    // — контент один, джерело правди єдине (десктопна панель), тут лише
    // читаємо його заново.
    const topEls = [].slice.call(navLinks.children).filter(el =>
      (el.tagName === 'A' && !el.classList.contains('nav-cta')) || el.classList.contains('nav-item-mega')
    );
    const langSwitch = navLinks.querySelector('.lang-switch');

    // --stagger нумерує пункти для хвилі появи в CSS (.nav-drawer.show ...);
    // нижній рядок (соцмережі + мова) іде наступним кроком за посиланнями.
    let linksHtml = '';
    topEls.forEach((el, i) => {
      if (el.classList.contains('nav-item-mega')){
        // Сам рядок — тепер повністю кнопка-перемикач, не посилання: тап по
        // напису більше нікуди не веде, лише розгортає підпункти (власник
        // явно попросив прибрати випадкову навігацію тут). Дістатись самої
        // сторінки можна першим підпунктом — тим самим CTA, що на фото в
        // десктопній панелі («Всі питання» / «Усі формати»), і звідти й
        // бере текст та посилання, а не з окремого хардкоду.
        const trigger = el.querySelector('.nav-mega-trigger');
        const cats = [].slice.call(el.querySelectorAll('.nav-mega-cat'));
        // .nav-mega-cta сам по собі <span> без href — посилання на всю
        // сторінку несе його предок .nav-mega-visual (фото-картка обгорнута
        // в <a>), звідти й href, а текст усе одно з .nav-mega-cta.
        const ctaLink = el.querySelector('.nav-mega-visual');
        const ctaLabel = el.querySelector('.nav-mega-cta');
        let subHtml = '';
        if (ctaLink && ctaLabel){
          subHtml += '<a href="' + ctaLink.getAttribute('href') + '" class="nav-drawer-sub-all">' + ctaLabel.textContent.trim() + '</a>';
        }
        cats.forEach(c => {
          const icon = c.parentElement.querySelector('.nav-mega-icon');
          subHtml += '<a href="' + c.getAttribute('href') + '">' + (icon ? icon.outerHTML : '') + '<span>' + c.textContent + '</span></a>';
        });
        linksHtml +=
          '<button type="button" class="nav-drawer-item-expand" style="--stagger:' + i + '" aria-expanded="false">' +
            '<span>' + trigger.textContent + '</span>' +
            '<span class="nav-drawer-expand" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg></span>' +
          '</button>' +
          '<div class="nav-drawer-sub">' + subHtml + '</div>';
      } else {
        linksHtml += '<a href="' + el.getAttribute('href') + '" style="--stagger:' + i + '">' + el.textContent + '</a>';
      }
    });
    const bottomStagger = topEls.length;

    let langHtml = '';
    if (langSwitch){
      langHtml = '<div class="nav-drawer-lang" role="group" aria-label="Мова сайту">' + langSwitch.innerHTML + '</div>';
    }

    // Іконки соцмереж — той самий набір SVG, що у футері (Instagram, TikTok,
    // Telegram, YouTube, пошта), тут окремим написом: розмітка футера ще не
    // обов'язково дійшла до цього місця сторінки, клонувати її звідти було б
    // крихко.
    const socialsHtml = ''
      + '<a class="f-soc" href="https://www.instagram.com/silent_ukraine/" target="_blank" rel="noopener noreferrer" aria-label="Instagram" title="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.2" y="3.2" width="17.6" height="17.6" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1.05" fill="currentColor" stroke="none"/></svg></a>'
      + '<a class="f-soc" href="https://www.tiktok.com/@silent.ukraine" target="_blank" rel="noopener noreferrer" aria-label="TikTok" title="TikTok"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.6 3.2v11.3a3.6 3.6 0 1 1-3.1-3.57"/><path d="M14.6 3.2a5 5 0 0 0 5 5"/></svg></a>'
      + '<a class="f-soc" href="https://t.me/silent_ukraine" target="_blank" rel="noopener noreferrer" aria-label="Telegram" title="Telegram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21.2 4.5 2.9 11.4a.5.5 0 0 0 .04.94l4.6 1.44 1.77 5.3a.5.5 0 0 0 .88.14l2.5-2.9 4.6 3.4a.5.5 0 0 0 .78-.3l3.05-14a.5.5 0 0 0-.66-.58Z"/><path d="m7.54 13.78 11.1-7.4-8.34 8.36-.36 3.9"/></svg></a>'
      + '<a class="f-soc" href="https://www.youtube.com/channel/UCYJcmOSbk5MDaNXDLjchVyQ" target="_blank" rel="noopener noreferrer" aria-label="YouTube" title="YouTube"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.6" y="5.6" width="18.8" height="12.8" rx="4"/><path d="m10.2 9.4 5 2.6-5 2.6z"/></svg></a>'
      + '<a class="f-soc" href="mailto:hello.silent.ua@gmail.com" aria-label="Пошта" title="Пошта"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.6" y="5.2" width="18.8" height="13.6" rx="2.6"/><path d="m3.4 7 8.05 5.6a1 1 0 0 0 1.1 0L20.6 7"/></svg></a>';

    // Свого верху в панелі більше немає: лого, кнопка й гамбургер — це сама
    // шапка (nav.menu-open зливає її назад в один рядок, CSS вище), а
    // гамбургер, обернений у хрестик, і є кнопкою закриття. Панель — лише
    // те, що під нею: пункти, мова, соцмережі. Підкладка — окремий елемент
    // (не всередині .nav-drawer): їй потрібен свій, нижчий z-index, щоб
    // тьмянити сторінку, не зачіпаючи саму шапку — деталі в CSS.
    drawer.innerHTML =
      '<div class="nav-drawer-panel" role="dialog" aria-modal="true" aria-label="Меню">' +
        '<nav class="nav-drawer-links" aria-label="Розділи сторінки">' + linksHtml + '</nav>' +
        '<div class="nav-drawer-bottom" style="--stagger:' + bottomStagger + '">' +
          '<div class="nav-drawer-socials">' + socialsHtml + '</div>' +
          (langHtml ? '<span class="nav-drawer-divider" aria-hidden="true"></span>' + langHtml : '') +
        '</div>' +
      '</div>';
    const backdrop = document.createElement('div');
    backdrop.className = 'nav-drawer-backdrop';
    backdrop.id = 'navDrawerBackdrop';
    document.body.appendChild(backdrop);
    document.body.appendChild(drawer);

    // Увесь рядок — кнопка-перемикач; сусідній .nav-drawer-sub, що йде
    // одразу за .nav-drawer-item-expand в розмітці, розгортається чи
    // згортається разом з нею.
    drawer.querySelectorAll('.nav-drawer-item-expand').forEach(btn => {
      btn.addEventListener('click', () => {
        const sub = btn.nextElementSibling;
        const open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', open ? 'false' : 'true');
        sub.classList.toggle('is-open', !open);
      });
    });

    // Просте overflow:hidden на body тут не годиться: меню відкривають уже
    // прокрученою сторінкою (сам гамбургер з'являється лише після скролу), а
    // overflow:hidden на body в цьому русі скидає window.scrollY на нуль —
    // під панеллю сторінка стрибала б угору, і після закриття людина
    // опинялась би не там, де була. Тому блокуємо скрол фіксацією body з
    // компенсацією через top, а по закритті повертаємо точну позицію назад.
    //
    // Саму лише body: коли body виходить із normal flow (position:fixed),
    // <html> лишається з висотою вже без body, і браузер може примусово
    // підтягнути її власний scrollTop під нову, меншу межу прокрутки — той
    // самий стрибок екрана вгору-вниз, тільки на рівні html, а не body, тож
    // компенсація через top на body його не ловить. overflow:hidden на
    // <html> лишає її scrollTop недоторканим, доки body заблокований.
    let lockedY = 0;
    // GSAP-поява панелі. Не пружна «крапля» CSS, а розкриття: панель ніби
    // випливає з пігулки зверху донизу (clip-path), пункти по черзі
    // виїжджають зліва з наведенням на різкість, нижній рядок — останнім.
    // Клас gs-menu вимикає CSS-перехід і CSS-хвилю пунктів (site.css), інакше
    // вони б грали разом із GSAP. Без GSAP і при reduce-motion лишається CSS.
    const G = window.gsap;
    const gsMenu = !!G && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (gsMenu) drawer.classList.add('gs-menu');
    const gsPanel = drawer.querySelector('.nav-drawer-panel');
    function gsOpen(){
      const items = [].slice.call(drawer.querySelectorAll('.nav-drawer-links > a, .nav-drawer-links > .nav-drawer-item-expand'));
      const bottom = drawer.querySelector('.nav-drawer-bottom');
      G.killTweensOf([gsPanel, items, bottom]);
      const o = { p: 0 };
      const paint = function(){
        // Знизу -80px у кінці: clip-path інакше зрізав би тінь панелі.
        gsPanel.style.clipPath = 'inset(0 -40px calc(' + ((1 - o.p) * 100).toFixed(2) + '% - ' + (o.p * 80).toFixed(1) + 'px) -40px)';
      };
      G.set(gsPanel, { opacity: 1, y: -14 });
      G.set(items, { opacity: 0, x: -20, filter: 'blur(5px)' });
      G.set(bottom, { opacity: 0, y: 14 });
      paint();
      const tl = G.timeline();
      tl.to(o, { p: 1, duration: 0.6, ease: 'expo.out', onUpdate: paint }, 0)
        .to(gsPanel, { y: 0, duration: 0.6, ease: 'expo.out' }, 0)
        .to(items, { opacity: 1, x: 0, filter: 'blur(0px)', duration: 0.5, ease: 'power3.out', stagger: 0.055,
                     clearProps: 'opacity,transform,filter' }, 0.12)
        .to(bottom, { opacity: 1, y: 0, duration: 0.45, ease: 'power3.out', clearProps: 'opacity,transform' }, 0.12 + items.length * 0.055)
        .add(function(){ gsPanel.style.clipPath = ''; });
    }
    function gsClose(){
      const items = [].slice.call(drawer.querySelectorAll('.nav-drawer-links > a, .nav-drawer-links > .nav-drawer-item-expand'));
      G.killTweensOf([gsPanel, items, drawer.querySelector('.nav-drawer-bottom')]);
      G.set(items, { clearProps: 'opacity,transform,filter' });
      G.set(drawer.querySelector('.nav-drawer-bottom'), { clearProps: 'opacity,transform' });
      gsPanel.style.clipPath = '';
      G.to(gsPanel, { opacity: 0, y: -10, duration: 0.24, ease: 'power2.in' });
    }
    function openDrawer(){
      lockedY = window.scrollY;
      drawer.classList.add('show');
      backdrop.classList.add('show');
      nav.classList.add('menu-open');
      if (gsMenu) gsOpen();
      burger.setAttribute('aria-expanded', 'true');
      document.documentElement.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.top = -lockedY + 'px';
      document.body.style.left = '0';
      document.body.style.right = '0';
      document.body.style.width = '100%';
    }
    function closeDrawer(){
      if (gsMenu) gsClose();
      drawer.classList.remove('show');
      backdrop.classList.remove('show');
      nav.classList.remove('menu-open');
      burger.setAttribute('aria-expanded', 'false');
      // Порядок тут критичний. scrollTo нічого не робить, доки лишається
      // хоч одне з двох: position:fixed на body (в нього тоді просто нема
      // куди прокручувати — html звужена до висоти вікна) або
      // overflow:hidden на html (сама прокрутка вимкнена). Тому спершу
      // знімаємо ОБИДВА обмеження — це самі по собі лише стилі, без
      // проміжного перемальовування між ними — і тільки тоді ставимо
      // scrollTo. Всі три рядки виконуються в одному синхронному такті, тож
      // браузер малює вже кінцевий, правильний кадр, а не проміжний з
      // scrollY=0.
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.left = '';
      document.body.style.right = '';
      document.body.style.width = '';
      document.documentElement.style.overflow = '';
      // { top, behavior: 'instant' }, не (0, lockedY): у html стоїть
      // scroll-behavior:smooth (для якірних посилань), і звичайний
      // виклик з тими самими координатами через нього самe і став видимою
      // прокруткою — сторінка спершу показувала 0, а тоді плавно
      // «доїжджала» до lockedY. Тут це не рух користувача, а повернення
      // на місце, і воно мусить бути миттєвим.
      window.scrollTo({ top: lockedY, left: 0, behavior: 'instant' });
    }
    burger.addEventListener('click', () => {
      if (drawer.classList.contains('show')) closeDrawer(); else openDrawer();
    });
    backdrop.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawer.classList.contains('show')) closeDrawer();
    });
    // Тап по посиланню всередині закриває саму панель — інакше перехід за
    // якорем ховається за ще відкритим меню.
    drawer.addEventListener('click', (e) => {
      if (e.target.closest('a')) closeDrawer();
    });
    // Ресайз у десктопну ширину (поворот пристрою, DevTools): гамбургер там
    // все одно ховає CSS-медіа-запит, але відкриту панель теж закриваємо —
    // інакше вона лишається на весь екран без способу закрити (гамбургер
    // зник разом із шапкою).
    window.addEventListener('resize', () => {
      if (window.innerWidth > 720 && drawer.classList.contains('show')) closeDrawer();
    });
  })();

  // ---- «Flexbox Filtering» (GSAP Flip): перемикання фільтра тем у картках ----
  // Прийом із демо GSAP Flip: знімаємо стан УСІХ карток (getState), одним
  // рухом міняємо видимість і батьківський ряд, а Flip.from сам проводить
  //  • картки, що лишились, — плавним переїздом на нове місце (не стрибком),
  //  • картки, що йдуть, — стиском у нуль із затуханням (absolute:true виймає
  //    їх із потоку, тож сітка одразу перебудовується, а вони ще гаснуть),
  //  • нові — «вмиканням» від нуля з невеликою затримкою, коли решта вже лягла.
  // Раніше це робили руками: absolute-позиції, таймери й transform-компенсація
  // (FLIP на CSS-переходах) — і картки лише вигасали та вигулькували поруч.
  // mutate() — єдине місце, де змінюється DOM (hidden / parent). Повертає false,
  // якщо Flip не завантажився чи ввімкнено reduce-motion: тоді викликач
  // лишається на старій розкладці. Незавершений попередній перехід доводимо до
  // кінця, щоб швидкі кліки по темах не накладались.
  //
  // ВИСОТА КОНТЕЙНЕРА. absolute:true виймає ВСІ картки з потоку, тож контейнер
  // на час переходу миттєво схлопувався б до нуля, а блок під ним (заклик
  // «Не знайшли свій формат?», наступна секція) стрибком їхав угору просто під
  // картки, що ще летять. Тому containers (елементи, висота яких залежить від
  // карток) тримаємо на старій висоті й тягнемо до нової тим самим рухом.
  //
  // ПОРЯДОК ВАЖЛИВИЙ, і саме на ньому вже помилялись. Кінцевий стан Flip знімає в
  // момент виклику Flip.from — у природній розкладці. Якщо висоту контейнера
  // зафіксувати ДО цього, CSS-сітка розтягує рядки на всю зафіксовану висоту
  // (картки завбільшки з пів сторінки), а flex-ряд стискає їх до плоских смуг.
  // Тому: 1) стара висота, 2) знімок стану, 3) mutate, 4) нова висота, 5)
  // Flip.from (картки стають absolute) і ЛИШЕ ТОДІ 6) стара висота.
  //
  // АНІМУЮТЬСЯ ВСІ КАРТКИ, а не «ті, що біля екрана»: absolute:true виймає з потоку
  // лише учасників Flip. Картки, яких ми б виключили, лишились би в потоці й
  // зсунулись би, щойно решта стала absolute, а в кінці стрибнули б назад.
  //
  // Параметри — за демо GreenSock «Smooth Flexbox Filtering with Flip»
  // (scale:true, absolute:true, вхід/вихід через opacity+scale), лише швидші:
  // демо має 0.7с рух і по 1с вхід/вихід, а на сторінці з десятками карток це
  // відчувалось як гальмування.
  let lastFlip = null, flipToken = 0;
  function flipFilter(cards, mutate, containers){
    const G = window.gsap, F = window.Flip;
    if (!G || !F || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    G.registerPlugin(F);
    if (lastFlip){ lastFlip.progress(1); lastFlip = null; }
    flipToken++;   // скасовує відкладене зняття gs-busy попереднього переходу
    const conts = (containers || []).filter(Boolean);
    const h0 = conts.map(e => e.getBoundingClientRect().height);
    // simple:true — режим Flip без обчислення матриць трансформацій кожного
    // елемента. Картки перед переходом не мають ні поворотів, ні масштабу, а
    // повний режим на дорогій розкладці головної коштував ~200мс лише на getState
    // (і ще стільки ж на from) — це і був зависаючий кадр на початку.
    const state = F.getState(cards, { simple: true });
    cards.forEach(c => c.classList.add('gs-busy'));
    mutate();
    // Видимість — і атрибутом hidden (його читає решта коду), і інлайновим
    // display, як у демо (item.style.display = 'none' | 'inline-flex'): Flip
    // тримає й відновлює саме інлайновий display.
    cards.forEach(c => { c.style.display = c.hidden ? 'none' : ''; });
    const h1 = conts.map(e => e.getBoundingClientRect().height);
    // Затримка між картками — щоб рух читався хвилею, а не одним блоком. ВАЖЛИВО:
    // Flip рахує stagger за індексом серед УСІХ елементів стану (44 картки), а не
    // лише видимих. Фіксований крок 0.03 давав картці №40 затримку 1.2с (з кроком
    // 0.08 із демо — 3.5с): частина карток їхала одразу, решта стояла й потім
    // «вилітала». Тому задаємо СУМАРНИЙ розкид (amount), а не крок: усі картки
    // стартують у межах 0.22с незалежно від їхньої кількості.
    lastFlip = F.from(state, {
      duration: 0.5, scale: true, ease: 'power2.inOut', stagger: { amount: 0.22 }, absolute: true, simple: true,
      onEnter: els => G.fromTo(els, { opacity: 0, scale: 0.5 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'power2.out' }),
      onLeave: els => G.to(els, { opacity: 0, scale: 0.5, duration: 0.3, ease: 'power1.in' }),
      onComplete: () => {
        G.set(cards, { clearProps: 'opacity,transform,scale' });
        conts.forEach(e => { e.style.height = ''; e.style.alignContent = ''; e.style.alignItems = ''; });
        lastFlip = null;
        // gs-busy (transition:none) знімаємо НЕ одразу, а через два кадри. Flip і ми
        // щойно очистили інлайновий transform (там було translate3d(…, тисячі px)).
        // Якби клас зник у тому самому такті, браузер побачив би зміну transform
        // уже з увімкненим CSS-переходом (.uc-card має transition: transform .3s) і
        // плавно «повертав» картку з тисяч пікселів назад: вона ставала на місце,
        // а потім вилітала. Це і був стрибок після фільтра.
        const my = ++flipToken;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          if (my === flipToken) cards.forEach(c => c.classList.remove('gs-busy'));
        }));
      }
    });
    conts.forEach((e, i) => {
      e.style.alignContent = 'start'; e.style.alignItems = 'flex-start';
      e.style.height = h0[i] + 'px';
      lastFlip.to(e, { height: h1[i], duration: 0.5, ease: 'power2.inOut' }, 0);
    });
    return true;
  }

  // ---- Фільтр тем на сторінці-списку досвідів ----
  // Кнопки й теми на картках проставляє збірник, тож тут лишається саме
  // перемикання. Стан за замовчуванням — усі картки: якщо цей блок не
  // виконається, сторінка просто лишиться повним списком, а не порожньою.
  (function(){
    const bar = document.querySelector('.exp-filter');
    const grid = document.querySelector('.exp-grid');
    if (!bar || !grid) return;
    const chips = [...bar.querySelectorAll('.exp-chip')];
    const cards = [...grid.querySelectorAll('.uc-card')];
    const count = document.querySelector('.exp-count');
    if (!chips.length || !cards.length) return;

    // Відмінок для числа: 1 формат, 2-4 формати, решта форматів.
    function word(n){
      const t = n % 100, o = n % 10;
      if (t > 10 && t < 20) return 'форматів';
      if (o === 1) return 'формат';
      if (o >= 2 && o <= 4) return 'формати';
      return 'форматів';
    }

    // Картка, яку фільтр щойно виключив, не зникає миттю, але й не тримає
    // сітку заручником: одразу переходить на position:absolute за власними
    // поточними координатами (offsetLeft/offsetTop відносно .exp-grid, який
    // тому й position:relative) — це виймає її з потоку негайно, сітка
    // навколо перевіршовується цим самим кадром, а картка тим часом стоїть
    // на тому самому місці й просто гасне. Лише коли згасання добіжить,
    // hidden прибирає й ці інлайнові стилі. Мапа тримає той таймер per
    // картка — повторний клік до завершення виходу мусить скасувати
    // попередній, інакше картка, яку щойно знову ввімкнули, могла б за стару
    // команду сховатись.
    const leaveTimers = new Map();

    function clearLeaveStyles(c){
      c.style.position = ''; c.style.left = ''; c.style.top = ''; c.style.width = '';
    }

    // FLIP: усе, що лишається на екрані, саме нікуди в DOM не рухається —
    // рухається те, що звільняється чи додається навколо нього, а сітка
    // миттю перевіршовує рештки на нове місце. Без цього перемикання
    // виглядало як п'ятнашки: те саме різке перескакування, тільки з
    // красивою появою нових карток поверх. FLIP бере різницю між «де картка
    // була» і «де вона опинилась після перевіршовки» і одразу компенсує її
    // transform'ом, а потім одним кадром знімає — картка їде, а не стрибає.
    function flip(before){
      cards.forEach(c => {
        if (c.hidden || c.classList.contains('is-leaving')) return;
        const first = before.get(c);
        if (!first) return; // картка щойно з'явилась — про неї подбає expChipIn
        const last = c.getBoundingClientRect();
        const dx = first.left - last.left, dy = first.top - last.top;
        if (Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5) return;
        c.style.transition = 'none';
        c.style.transform = 'translate(' + dx + 'px,' + dy + 'px)';
        // Читання layout-властивості змушує браузер застосувати стилі вище
        // до того, як нижче увімкнеться transition — інакше обидва правила
        // злипаються в один кадр, і ковзання просто не встигає початись.
        void c.offsetWidth;
        c.style.transition = 'transform .34s var(--ease-arrive)';
        c.style.transform = '';
        clearTimeout(c._flipCleanup);
        c._flipCleanup = setTimeout(() => { c.style.transition = ''; }, 380);
      });
    }

    // Стара розкладка (без GSAP Flip): залишається запасним варіантом.
    function applyLegacy(cat){
      const before = new Map();
      cards.forEach(c => { if (!c.hidden) before.set(c, c.getBoundingClientRect()); });
      // Координати картки, що йде, рахуємо від цього ж знімка «до», а не від
      // offsetLeft/offsetTop у момент виходу: цикл нижче міняє сітку по ходу,
      // і картка, оброблена пізніше за сусідню, інакше зчитала б уже трохи
      // перевіршовану позицію.
      const gridBefore = grid.getBoundingClientRect();

      let shown = 0;
      let i = 0;
      cards.forEach(c => {
        // Тем у картки може бути кілька, тож звіряємо зі списком, а не з одним
        // значенням: табір належить і церквам, і дітям, і мусить знайтись в обох.
        const on = cat === 'all' || (c.dataset.cats || '').split(' ').indexOf(cat) !== -1;
        if (on) shown++;

        const pending = leaveTimers.get(c);
        if (pending) { clearTimeout(pending); leaveTimers.delete(c); }

        if (on){
          const wasHidden = c.hidden;
          // hidden і абсолютне позиціювання знімаємо одразу: якщо картка саме
          // дограє вихід, це його й перериває.
          c.hidden = false;
          c.classList.remove('is-leaving');
          clearLeaveStyles(c);
          if (wasHidden){
            // Картка справді нова цього разу — влітає каскадом. Стагер лічить
            // лише такі картки: каскад тоді йде з нуля, а не з випадкового
            // номера в сітці. clearTimeout/remove — щоб клас не лишався
            // навічно й не заважав майбутньому FLIP цієї ж картки.
            c.style.setProperty('--stagger', i++);
            c.classList.add('is-entering');
            clearTimeout(c._enterCleanup);
            c._enterCleanup = setTimeout(() => c.classList.remove('is-entering'), 400);
          }
        } else if (!c.hidden){
          const r = before.get(c);
          c.style.position = 'absolute';
          c.style.left = (r.left - gridBefore.left) + 'px';
          c.style.top = (r.top - gridBefore.top) + 'px';
          c.style.width = r.width + 'px';
          c.classList.add('is-leaving');
          const t = setTimeout(() => {
            c.hidden = true;
            c.classList.remove('is-leaving');
            clearLeaveStyles(c);
            leaveTimers.delete(c);
          }, 180);
          leaveTimers.set(c, t);
        }
      });
      chips.forEach(ch => {
        const on = ch.dataset.cat === cat;
        ch.classList.toggle('is-on', on);
        ch.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
      // Клас вмикає появу лише після першого вибору: на завантаженні сторінки
      // двадцять шість карток не мусять проявлятися по одній.
      grid.classList.toggle('is-filtered', cat !== 'all');
      if (count){
        count.textContent = cat === 'all'
          ? '' : shown + ' ' + word(shown) + ' у цій темі';
      }
      flip(before);
    }

    function apply(cat, animate){
      // Незавершену появу при прокрутці (site.js, «Картки каталогу») доводимо
      // до кінця ДО того, як знімаємо стан.
      if (window.__expFinish) window.__expFinish();
      let shown = 0;
      const done = animate !== false && flipFilter(cards, () => {
        // Картки, що ще виходили за старою схемою, вважаємо вже прихованими.
        leaveTimers.forEach(t => clearTimeout(t)); leaveTimers.clear();
        cards.forEach(c => {
          if (c.classList.contains('is-leaving')){ c.hidden = true; c.classList.remove('is-leaving'); clearLeaveStyles(c); }
          const on = cat === 'all' || (c.dataset.cats || '').split(' ').indexOf(cat) !== -1;
          if (on) shown++;
          c.hidden = !on;
        });
        chips.forEach(ch => {
          const on = ch.dataset.cat === cat;
          ch.classList.toggle('is-on', on);
          ch.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        grid.classList.toggle('is-filtered', cat !== 'all');
        if (count) count.textContent = cat === 'all' ? '' : shown + ' ' + word(shown) + ' у цій темі';
      }, [grid]);
      if (!done) applyLegacy(cat);
    }

    bar.addEventListener('click', (e) => {
      const chip = e.target.closest('.exp-chip');
      if (chip){ apply(chip.dataset.cat); centerChip(bar, chip); }
    });

    // Кнопки «Замовити цей досвід» у сітці: на відміну від стрічки на
    // головній/сторінці досвіду, ця сторінка власної форми не має, тож
    // orderExperience (assets/site.js, зверху файлу) сам піде гілкою
    // редіректу на головну з назвою в query-параметрі.
    grid.addEventListener('click', (e) => {
      const btn = e.target.closest('.uc-order');
      // Картка з власною сторінкою (зараз лише «Корпоративи») малює тут
      // справжнє <a href>, не <button> — його рідну навігацію не чіпаємо.
      if (!btn || btn.tagName !== 'BUTTON') return;
      const card = btn.closest('.uc-card');
      const name = card && card.dataset.uc;
      if (name) orderExperience(name);
    });

    // ?cat=business із mega-меню «Тихі враження» в шапці — та сама тема,
    // яку відкрив би клік по чіпу, тільки одразу при заході на сторінку.
    // Невідома чи відсутня тема — сторінка просто лишається на «Усі», без
    // помилки.
    const wanted = new URLSearchParams(window.location.search).get('cat');
    if (wanted && chips.some(ch => ch.dataset.cat === wanted)) apply(wanted, false);
  })();

  // Знімок і навушники на сторінці «Тихі враження» йдуть за активним каналом.
  // Самим перемиканням тут не керуємо: панель має id="channels", тож звук,
  // еквалайзер і glow бере на себе той самий код, що й на головній. Лишається
  // стежити за тим, який канал став активним, — і автоперемикання теж.
  (function(){
    const stage = document.querySelector('.hp-stage');
    if (!stage) return;
    const row = stage.querySelector('.ch-toggle-row');
    const sets = [
      Array.from(stage.querySelectorAll('.hp-img')),
      Array.from(stage.querySelectorAll('.hp-top-img'))
    ].filter(function(a){ return a.length; });
    if (!row || !sets.length) return;

    // Кадр, що йде, лишається щільним, а новий проявляється поверх нього. Якщо
    // натомість гасити попередній одночасно, посередині переходу обидва
    // напівпрозорі й зображення на мить провалюється у фон.
    // Пульс під навушниками бере колір каналу звідси: сам він живе поза
    // панеллю, тож --ch, який site.js ставить на #channels, до нього не
    // доходить.
    const GLOW = ['var(--red)', 'var(--green)', 'var(--blue)'];

    let z = 2, hideTimer = null;
    function paint(i){
      if (GLOW[i]) stage.style.setProperty('--hp-glow', GLOW[i]);
      sets.forEach(function(set){
        for (let k = 0; k < set.length; k++){
          if (Number(set[k].dataset.ch) !== i) continue;
          z += 1;
          set[k].style.zIndex = String(z);
          set[k].classList.add('is-on');
        }
      });
      // Попередній кадр лишається щільним, поки новий проявляється, інакше
      // посередині переходу обидва напівпрозорі. Але тільки поки: далі його
      // треба прибрати. Силуети трьох рендерів збігаються не піксель у
      // піксель, і нижній визирав з-під верхнього тонким обідком.
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function(){
        sets.forEach(function(set){
          for (let k = 0; k < set.length; k++){
            if (Number(set[k].dataset.ch) !== i) set[k].classList.remove('is-on');
          }
        });
      }, 620);
    }

    let cur = -1;
    function sync(){
      const on = row.querySelector('.ch-toggle.active');
      const i = on ? Number(on.dataset.ch) : 0;
      if (i === cur) return;
      cur = i;
      paint(i);
    }
    new MutationObserver(sync).observe(row, {
      subtree: true, attributes: true, attributeFilter: ['class']
    });
    sync();
  })();

  // Підсвітка карток. Миша веде дугу за курсором, палець засвічує цілу
  // обводку, доки тримає картку. Обидві гілки живуть в одному модулі, бо
  // ділять селектор і не мають знати одна про одну.
  //
  // .exp-facts li в тому самому списку навмисно: у нього нема ні дуги, ні
  // обводки (CSS-правила спотлайту про нього не знають), лише дотик
  // потрібен — той самий держак is-pressed, яким факти геро на корпоративах
  // вмикають анімацію своїх іконок, той самий, що й у карток. Заводити
  // окремий слухач заради одного класу було б дублюванням того, що вже
  // працює рядком нижче.
  (function(){
    if (!window.matchMedia) return;
    const SEL = '.uc-card, .benefit-card, .pb-card:not(.pb-card-accent), .exp-facts li';

    // ---- Миша: координати для дуги ----
    // Саму плашку малює CSS, звідси приходять тільки координати. Слухач один
    // на документ, а не по одному на кожній із сорока карток. Читання
    // розмірів і запис властивостей зведені в один кадр — інакше кожен рух
    // миші змушував би браузер рахувати розкладку посеред обробника.
    // Хто просив менше руху, дістає нерухому дугу по центру картки: її малює
    // те саме правило зі значеннями --spot-x/--spot-y за умовчанням.
    if (matchMedia('(hover: hover) and (pointer: fine)').matches &&
        !matchMedia('(prefers-reduced-motion: reduce)').matches){
      let card = null, cx = 0, cy = 0, queued = false;

      function draw(){
        queued = false;
        if (!card) return;
        const r = card.getBoundingClientRect();
        card.style.setProperty('--spot-x', (cx - r.left).toFixed(1) + 'px');
        card.style.setProperty('--spot-y', (cy - r.top).toFixed(1) + 'px');
      }

      document.addEventListener('pointermove', function(e){
        if (e.pointerType && e.pointerType !== 'mouse') return;
        const hit = e.target && e.target.closest ? e.target.closest(SEL) : null;
        if (hit !== card){
          // Картка, яку лишили, вертається до свого центру: інакше наступного
          // разу вона спалахнула б із дугою там, де курсор пішов геть.
          if (card){
            card.style.removeProperty('--spot-x');
            card.style.removeProperty('--spot-y');
          }
          card = hit;
        }
        if (!card) return;
        cx = e.clientX; cy = e.clientY;
        if (!queued){ queued = true; requestAnimationFrame(draw); }
      }, { passive: true });
    }

    // ---- Палець: обводка, доки картку тримають ----
    // Гілка не за медіазапитом, а за типом вказівника: на ноутбуці з
    // сенсорним екраном працюють обидві, кожна своєму вказівнику.
    let held = null;
    const drop = function(){
      if (held){ held.classList.remove('is-pressed'); held = null; }
    };
    document.addEventListener('pointerdown', function(e){
      if (e.pointerType === 'mouse') return;
      const hit = e.target && e.target.closest ? e.target.closest(SEL) : null;
      if (!hit) return;
      drop();
      held = hit;
      hit.classList.add('is-pressed');
    }, { passive: true });
    ['pointerup', 'pointercancel'].forEach(function(t){
      document.addEventListener(t, drop, { passive: true });
    });
    // Прокрутка забирає палець собі, і pointercancel приходить не всюди
    // однаково: без цього картка лишалась би підсвіченою після того, як її
    // змахнули з екрана.
    window.addEventListener('scroll', drop, { passive: true });
  })();

  // ---- Барабан «Silent + формат» у геро /experiences/ (одна картка на всі
  // ширини) ----
  // Список у DOM потроєний навмисно: рахунок «active» лише росте вперед,
  // ніколи не обнуляється по колу — тому translateY завжди рухається в
  // один бік, без миттєвого скидання назад, яке виглядало б як заїкання.
  // Раз на повне коло (active сягнув другої копії) непомітно віднімаємо
  // довжину списку: з transition:none рівно на один кадр — бо потроєний
  // список повторює той самий порядок слів, картинка на екрані від цього
  // віднімання не змінюється ні на піксель, лише сам лічильник більше не
  // росте нескінченно.
  //
  // Геометрія ЖОДНОГО числа не бере фіксованим (раніше було окремо
  // desktop/mobile — і двічі ламалось, коли реальні пропорції на екрані
  // розходились з тим, що уявлялось на папері): LINE, CENTER і RADIUS усі
  // виміряні з фактичного розміру картки на екрані (CSS малює її у cqw/%,
  // тобто пропорційно її власній ширині на БУДЬ-якому розмірі), а не
  // вгадані під один конкретний брейкпоінт. applyGeometry() перераховує їх
  // при кожній зміні розміру вікна — та сама логіка на 300px і на 650px.
  //
  // Та сама механіка працює і в геро /faq/, лише в другому режимі
  // (data-reel="questions" на списку): без «SILENT.» зліва, рядки — питання
  // від лівого краю картки, дуга глибша, розмір шрифту підганяється так, щоб
  // найдовше питання вмістилось в один рядок, а центральне питання можна
  // натиснути — сторінка відкриває його відповідь. Усе інше (покадровий
  // рендер, потроєний список) — спільне, тож функція одна на обидві сторінки.
  function initReel(list){
    if (!list) return;
    const questions = list.dataset.reel === 'questions';
    const words = [].slice.call(list.children).map(function(li){ return li.textContent.trim(); });
    const n = words.length;
    if (n < 2) return;
    // Найбільший нахил слова на самому краю дуги, у градусах (кут, не
    // піксель, тож розміру картки не стосується). Ділимо його на кількість
    // видимих рядків, а не множимо фіксований крок на відстань: на високій
    // картці рядків 13+, і фіксований крок 5° давав би 30°+ на краях.
    // Питання вдвічі-втричі довші за слово-формат, і той самий кут на
    // довгому рядку задирав би його кінець на кілька рядків угору — тож для
    // них нахил трохи м'якший (вигин дуги дає глибший RADIUS нижче).
    const MAX_TILT = questions ? 16 : 22;
    let LINE, CENTER, RADIUS;
    // data-q (id відповіді, на яку веде рядок барабана питань) переносимо
    // в усі три копії списку — інакше клік по копії не знав би, куди вести.
    const keys = [].slice.call(list.children).map(function(li){ return li.getAttribute('data-q') || ''; });
    list.innerHTML = words.concat(words, words)
      .map(function(w, i){
        const q = keys[i % n];
        return '<li' + (q ? ' data-q="' + q + '"' : '') + '><span>' + w + '</span></li>';
      }).join('');
    const items = [].slice.call(list.children);
    const winEl = list.parentElement;
    const cardEl = winEl.parentElement;
    let active = n;   // ціль: індекс слова, що стане/стоїть по центру
    let pos = n;      // де список ФАКТИЧНО зараз (дробове під час руху)
    // Рух і вигляд кожного рядка рахуємо в JS покадрово від pos, а не
    // CSS-переходами (раніше: translateY списку — один transition, а
    // прозорість/розмиття/колір слів — інші, з іншою тривалістю). Через
    // той розсинхрон на iPhone видно було «стрибок → усе різко → потім
    // розмиття»: Safari до того ж скидає filter на час анімації
    // transform. Тепер кожен кадр кожен рядок отримує рівно той вигляд,
    // який відповідає його поточній дробовій відстані до центру, — фокус
    // перетікає з одного слова на наступне безперервно, разом із рухом.
    //
    // Розмиття — text-shadow, не filter:blur(). filter на десятку
    // рухомих елементів під маскою й backdrop-filter картки змушував iOS
    // виносити кожен у окремий GPU-шар, і Safari не встигав їх
    // домальовувати — звідти фіолетові смужки між словами. text-shadow
    // малюється разом із текстом, шарів не плодить. Прозорість — теж не
    // opacity (той самий шар), а альфа кольору.
    //
    // Дуга кола, не поворот на місці: активне слово — найближча до
    // глядача точка кола (0 зсуву вбік), і в обидва боки рядки однаково
    // «йдуть углиб» — відходять ліворуч за косинусом кута (1-cos: 0 у
    // центрі, RADIUS на краях). rotate — дотична до кола в тій точці.
    // VIS = CENTER+1: на рядок більше, ніж цілком вміщається у вікно,
    // щоб крайній заходив під край картки, а не з'являвся на видноті.
    let LIME = [198, 255, 0];
    (function(){
      const dot = cardEl.querySelector('.exp-reel-dot');
      const m = dot && getComputedStyle(dot).color.match(/\d+(\.\d+)?/g);
      if (m && m.length >= 3) LIME = [+m[0], +m[1], +m[2]];
    })();
    const shown = items.map(function(){ return null; });
    function render(){
      list.style.transform = 'translateY(' + ((CENTER - pos) * LINE + CENTER_OFFSET).toFixed(2) + 'px)';
      const VIS = CENTER + 1;
      for (let i = 0; i < items.length; i++){
        const li = items[i];
        const span = li.firstElementChild;
        const raw = i - pos;
        const a = Math.abs(raw);
        if (a > VIS + 1){
          if (shown[i] !== false){
            span.style.visibility = 'hidden';
            li.setAttribute('data-d', 'gone');
            shown[i] = false;
          }
          continue;
        }
        if (shown[i] !== true){ span.style.visibility = ''; shown[i] = true; }
        const d = String(Math.round(raw));
        if (li.getAttribute('data-d') !== d) li.setAttribute('data-d', d);
        const t = Math.min(a / VIS, 1.15);
        const f = Math.max(0, 1 - a);                  // 1 — у фокусі, 0 — від сусіда далі
        const edge = Math.max(0, 0.92 - 0.7 * t);      // згасання до краю
        const fade = a < 1 ? 1 + (0.92 - 0.7 / VIS - 1) * a : edge;
        const alpha = (0.6 + 0.4 * f) * fade;
        const r = Math.round(255 + (LIME[0] - 255) * f);
        const g = Math.round(255 + (LIME[1] - 255) * f);
        const b = Math.round(255 + (LIME[2] - 255) * f);
        // Уже перший сусід помітно м'який, далі — плавно сильніше до краю:
        // у фокусі лишається тільки одне слово. Числа вдвічі більші, ніж
        // були для filter:blur — радіус розмиття text-shadow за стандартом
        // це ~2σ, тобто той самий px у тіні розмиває вдвічі слабше.
        const blur = LINE * (0.08 + 0.12 * t) * Math.min(1, a);
        const s = Math.max(0, Math.min(1, (blur - 0.3) / 2));
        const col = r + ',' + g + ',' + b + ',';
        span.style.color = 'rgba(' + col + (alpha * (1 - s)).toFixed(3) + ')';
        span.style.textShadow = s > 0
          ? '0 0 ' + blur.toFixed(2) + 'px rgba(' + col + Math.min(1, alpha * (0.4 + 1.1 * s)).toFixed(3) + ')'
          : 'none';
        const angle = (raw / VIS) * (Math.PI / 2);
        const bow = -RADIUS * (1 - Math.cos(angle));
        // Питання в центрі — на повний розмір, сусіди трохи менші: як у
        // колесі вибору, фокус видно не лише кольором. Для слів-форматів
        // масштабу немає — там «SILENT. СЛОВО» мусить стояти одним рядком.
        const zoom = questions ? ' scale(' + (0.84 + 0.16 * f).toFixed(3) + ')' : '';
        span.style.transform = 'translateX(' + bow.toFixed(1) + 'px) rotate(' + (raw * MAX_TILT / VIS).toFixed(2) + 'deg)' + zoom;
      }
    }
    // Той самий характер руху, що був у CSS: cubic-bezier(.16,1,.3,1).
    function ease(x){
      const p1x = .16, p1y = 1, p2x = .3, p2y = 1;
      const bx = function(u){ return 3*p1x*u*(1-u)*(1-u) + 3*p2x*u*u*(1-u) + u*u*u; };
      const by = function(u){ return 3*p1y*u*(1-u)*(1-u) + 3*p2y*u*u*(1-u) + u*u*u; };
      let lo = 0, hi = 1, u = x;
      for (let k = 0; k < 24; k++){ u = (lo + hi) / 2; if (bx(u) < x) lo = u; else hi = u; }
      return by(u);
    }
    let CENTER_OFFSET = 0;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function applyGeometry(){
      const cs = getComputedStyle(cardEl);
      // Вікно — від рамки до рамки по вертикалі: від'ємні margin рівно на
      // padding картки (не відсотком у CSS: відсоток margin рахується від
      // ширини флекс-контейнера, а padding — від ширини предка картки, і
      // вони розходяться на кілька пікселів). Симетрично згори й знизу,
      // тож центр вікна лишається центром картки — там, де й «SILENT.».
      // Ставимо ДО замірів нижче: висота вікна від цього залежить.
      winEl.style.marginTop = '-' + cs.paddingTop;
      winEl.style.marginBottom = '-' + cs.paddingBottom;
      // LINE — фактична висота рядка (CSS: 10.8cqw), не вгадане число:
      // читаємо готовий рендер замість дублювання відсотка тут і ризику
      // розсинхронитись з CSS.
      LINE = items[0].getBoundingClientRect().height || 1;
      const h = winEl.getBoundingClientRect().height;
      const ideal = h > 0 ? (h / LINE - 1) / 2 : 4;
      CENTER = Math.max(1, Math.round(ideal));
      CENTER_OFFSET = (ideal - CENTER) * LINE;
      // Буфер дуги (margin-left вікна) і компенсаційний зсув списку МУСЯТЬ
      // бути тим самим пікселем — у CSS це були дві окремі відсоткові
      // величини (margin-left вікна — % від ШИРИНИ КАРТКИ, бо то відсоток
      // margin флекс-елемента; left списку — % від ширини САМОГО вікна,
      // яке вужче за картку на тег+gap) і сходились тільки випадково, на
      // одній конкретній ширині. Рахуємо обидва від ширини картки (R) і
      // проставляємо inline — так вони гарантовано рівні на будь-якому
      // розмірі. RADIUS — менша частка того самого R, з запасом під буфер.
      const R = cardEl.getBoundingClientRect().width
        - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)
        - parseFloat(cs.borderLeftWidth) - parseFloat(cs.borderRightWidth);
      // Питання: дуга вдвічі глибша, ніж у слів-форматів (власник попросив
      // вигнутішу), і буфер ліворуч під неї відповідно більший — інакше
      // рядки на краях упирались би в лівий край вікна.
      RADIUS = R * (questions ? 0.2 : 0.10);
      const buffer = R * (questions ? 0.22 : 0.13);
      winEl.style.marginLeft = '-' + buffer.toFixed(2) + 'px';
      list.style.left = buffer.toFixed(2) + 'px';
      list.style.width = 'calc(100% - ' + buffer.toFixed(2) + 'px)';
      if (questions){
        // Питання починаються не впритул до лівого краю вмісту, а з відступом
        // (власник: блок був «затиснутий зліва») — 9% ширини вмісту. На
        // рядок тоді лишається R мінус цей відступ і ще стільки ж справа,
        // щоб обводка активного питання не впиралась у край картки. --fit
        // масштабує CSS-розмір шрифту: скидаємо в 1, міряємо найширший
        // рядок (offsetWidth — ширина розкладки, поворот і scale на неї не
        // впливають) і зменшуємо рівно настільки, щоб він уліз.
        const inset = R * 0.09;
        list.style.left = (buffer + inset).toFixed(2) + 'px';
        list.style.width = 'calc(100% - ' + (buffer + inset).toFixed(2) + 'px)';
        list.style.setProperty('--fit', '1');
        let widest = 0;
        for (let k = 0; k < n; k++) widest = Math.max(widest, items[k].firstElementChild.offsetWidth);
        const room = R - inset * 2;
        list.style.setProperty('--fit', widest > room ? (room / widest).toFixed(4) : '1');
      }
    }
    applyGeometry();
    render();
    // Перший рендер міряє LINE/RADIUS з розкладки, яка щойно існує — а на
    // завантаженні сторінки шрифт Unbounded ще міг не встигнути підʼїхати
    // (рядки тоді трохи іншої висоти на системному шрифті) чи aspect-ratio
    // не встиг порахуватись до першого кадру. Обидва перерахунки нижче
    // ловлять цей момент без чекання на ресайз від користувача.
    if (document.fonts && document.fonts.ready){
      document.fonts.ready.then(function(){ applyGeometry(); render(); });
    }
    window.addEventListener('load', function(){ applyGeometry(); render(); });
    const DURATION = 620;
    let timer = null;
    // hovering — курсор на картці питань (режим керування мишею нижче): тоді
    // автопрокрутка мовчить. anim — номер поточної анімації кроку: якщо
    // курсор зайшов на картку посеред кроку, крок обривається там, де був,
    // і далі барабан веде миша.
    let hovering = false, anim = 0;
    function tick(){
      if (hovering) return;
      const from = pos;
      active++;
      const to = active;
      const t0 = performance.now();
      const my = ++anim;
      function frame(now){
        if (my !== anim) return;
        const p = Math.min(1, (now - t0) / DURATION);
        pos = from + (to - from) * ease(p);
        render();
        if (p < 1){ requestAnimationFrame(frame); return; }
        pos = to;
        // Раз на повне коло відкочуємо лічильник на n назад. Вигляд кожного
        // рядка — неперервна функція від (i - pos), а список потроєний: ті
        // самі слова стоять рівно на n позицій раніше, тож кадр до й після
        // відкату піксель у піксель однаковий. Жодних переходів, які могли
        // б «проявляти» нові рядки з нуля, більше немає — і блимання теж.
        if (active >= n * 2){ active -= n; pos -= n; }
        render();
      }
      requestAnimationFrame(frame);
    }
    // Питання читається довше за одне слово, тож і стоїть по центру довше.
    function start(){ if (!timer) timer = setInterval(tick, questions ? 3200 : 2400); }
    if (!reduceMotion) start();

    if (questions){
      // ---- Керування мишею (лише барабан питань) ----
      // Картка — як колесо під курсором: курсор у верхній половині крутить
      // питання донизу (назад по списку), у нижній — угору (вперед), і тим
      // швидше, чим ближче до краю; «вперед» трохи швидший за «назад», бо
      // це природний напрям читання. Смуга посередині — мертва зона: там
      // барабан плавно доводить найближче питання точно в центр і стоїть,
      // тож його можна натиснути. Pointer, не touch: на сенсорі картки
      // немає (вона лише для десктопу), а «наведення» пальцем не існує.
      const DEAD = 0.2;          // половина мертвої зони, частка від пів висоти картки
      const SPEED_DOWN = 7;      // рядків за секунду на самому краю, вперед
      const SPEED_UP = 5;        // те саме назад
      let v = 0, raf = 0, last = 0;
      function loop(now){
        const dt = Math.min(0.05, (now - last) / 1000);
        last = now;
        if (v !== 0){
          pos += v * dt;
        } else {
          // Доводка до найближчого цілого — експоненційна, без ривка.
          const target = Math.round(pos);
          pos += (target - pos) * Math.min(1, dt * 10);
          if (Math.abs(target - pos) < 0.002) pos = target;
        }
        // Той самий непомітний відкат на n, що й в автопрокрутці, в обидва
        // боки: список потроєний, тож кадр до й після відкату однаковий.
        if (pos >= n * 2) pos -= n;
        if (pos < n) pos += n;
        active = Math.round(pos);
        render();
        if (hovering) raf = requestAnimationFrame(loop);
      }
      cardEl.addEventListener('pointerenter', function(e){
        if (e.pointerType !== 'mouse' || reduceMotion) return;
        hovering = true;
        anim++;                      // обриваємо крок автопрокрутки, якщо він іде
        last = performance.now();
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(loop);
      });
      cardEl.addEventListener('pointermove', function(e){
        if (!hovering) return;
        const r = cardEl.getBoundingClientRect();
        const dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
        const a = Math.min(1, Math.abs(dy));
        if (a < DEAD){ v = 0; return; }
        const k = Math.pow((a - DEAD) / (1 - DEAD), 1.4);
        v = dy > 0 ? k * SPEED_DOWN : -k * SPEED_UP;
      });
      cardEl.addEventListener('pointerleave', function(){
        if (!hovering) return;
        hovering = false; v = 0;
        cancelAnimationFrame(raf);
        // Картку покинули посеред руху — доводимо до цілого тим самим кроком,
        // що й автопрокрутка, щоб наступний tick почав з рівного місця.
        const from = pos, to = Math.round(pos), t0 = performance.now(), my = ++anim;
        active = to;
        (function settle(now){
          if (my !== anim) return;
          const p = Math.min(1, (now - t0) / 300);
          pos = from + (to - from) * ease(p);
          render();
          if (p < 1) requestAnimationFrame(settle);
        })(t0);
      });

      // Клік по центральному питанню відкриває його відповідь нижче. У
      // барабані питання скорочені («А якщо дощ?»), тож рядок веде на повне
      // питання не за текстом, а за id його відповіді (data-q). Картка
      // aria-hidden: для клавіатури й читалки ті самі питання — у списку
      // нижче, де вони й так відкриваються. Тут лише прискорення для миші.
      list.addEventListener('click', function(e){
        const li = e.target.closest('li');
        if (!li || li.getAttribute('data-d') !== '0') return;
        const ans = document.getElementById(li.getAttribute('data-q') || '');
        const item = ans && ans.closest('.faq-item');
        if (!item) return;
        // Відкрите питання вище за це зараз згорнеться (акордеон тримає
        // відкритим одне) — його висоту віднімаємо заздалегідь, інакше
        // прокрутка приїхала б нижче, ніж треба.
        let shift = 0;
        document.querySelectorAll('.faq-item.open').forEach(function(o){
          if (o !== item && (o.compareDocumentPosition(item) & Node.DOCUMENT_POSITION_FOLLOWING)){
            shift += o.querySelector('.faq-a').offsetHeight;
          }
        });
        if (!item.classList.contains('open')) item.querySelector('.faq-q').click();
        const top = item.getBoundingClientRect().top + window.scrollY - shift - 110;
        window.scrollTo({ top: top, behavior: reduceMotion ? 'instant' : 'smooth' });
      });
    }
    // Картка масштабується безперервно з шириною вікна браузера (aspect-
    // ratio + cqw/% у CSS), не по брейкпоінтах, тож геометрію перераховуємо
    // на кожен resize (debounce той самий, що в інших resize-обробниках
    // цього файлу), а не лише при переході через якийсь конкретний поріг.
    let geomResizeTimer = null;
    window.addEventListener('resize', function(){
      clearTimeout(geomResizeTimer);
      geomResizeTimer = setTimeout(function(){
        applyGeometry();
        render();
      }, 120);
    }, { passive: true });
  }
  initReel(document.getElementById('expReelList'));

  // ---- Геро /faq/: «хмара питань» ----
  // Замінила барабан-півколо. Питання пливуть ГОРИЗОНТАЛЬНО кількома рядками
  // (рядки не рухаються по вертикалі — стоять стосом), картка помічена
  // «глибиною» за відстанню рядка до середнього: середній різкий і яскравий,
  // вищі й нижчі — тьмяніші, розмиті й трохи швидші (паралакс). Розмиття —
  // text-shadow, не filter:blur (той на рухомих елементах давав на iOS смужки
  // недомальованих GPU-шарів, див. коментар до барабана вище). Оскільки рядки
  // по вертикалі нерухомі, вигляд кожного рахуємо ОДИН раз, а покадрово
  // рухаємо лише translateX. У середньому рядку питання, що проходить біля
  // центру картки, підсвічується лаймом; клік по ньому веде до відповіді.
  function initQuestionCloud(list){
    if (!list) return;
    const winEl = list.parentElement, cardEl = winEl.parentElement;
    const src = [].slice.call(list.children).map(function(li){
      return { text: li.textContent.trim(), key: li.getAttribute('data-q') || '' };
    });
    const n = src.length;
    if (n < 3) return;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const LIME = [198, 255, 0];
    const stage = document.createElement('div');
    stage.className = 'exp-cloud';
    winEl.appendChild(stage);
    list.style.display = 'none';
    let rows = [], mid = 0, cardW = 1;

    function build(){
      stage.innerHTML = '';
      rows = [];
      const h = stage.getBoundingClientRect().height;
      const pitch = parseFloat(getComputedStyle(stage).getPropertyValue('--pitch')) || 50;
      let count = Math.floor(h / pitch);
      count = Math.max(5, Math.min(9, count % 2 ? count : count - 1));
      mid = (count - 1) / 2;
      for (let r = 0; r < count; r++){
        const d = Math.abs(r - mid);
        const row = document.createElement('div');
        row.className = 'exp-cloud-row';
        // Кожен рядок — те саме коло питань зі своїм зсувом початку, двічі
        // підряд, щоб зациклити рух без стику.
        const shift = (r * 4 + (r % 2) * 2) % n;
        let html = '';
        for (let rep = 0; rep < 2; rep++){
          for (let k = 0; k < n; k++){
            const q = src[(k + shift) % n];
            html += '<span' + (q.key ? ' data-q="' + q.key + '"' : '') + '>' + q.text + '</span>';
          }
        }
        row.innerHTML = html;
        // Глибина: 0 у середньому рядку, далі згасання/розмиття зростають.
        const a = d === 0 ? 1 : Math.max(0.2, 0.62 - 0.14 * (d - 1));
        const blur = d === 0 ? 0 : Math.min(3.6, 0.9 + 0.9 * d);
        const s = Math.max(0, Math.min(1, (blur - 0.3) / 2));
        row.style.setProperty('--c', 'rgba(255,255,255,' + (a * (1 - s)).toFixed(3) + ')');
        row.style.setProperty('--ts', blur > 0 ? '0 0 ' + blur.toFixed(2) + 'px rgba(255,255,255,' + Math.min(1, a * (0.4 + 1.1 * s)).toFixed(3) + ')' : 'none');
        row.style.setProperty('--bd', 'rgba(255,255,255,' + (0.14 * a).toFixed(3) + ')');
        row.dataset.d = String(Math.round(r - mid));
        stage.appendChild(row);
        [].forEach.call(row.children, function(sp){ sp._r = r; });
        rows.push({ el: row, d: d, a: a, blur: blur, m: 1, x: Math.random() * 400, speed: 26 * (1 + 0.32 * d), setW: 0, spans: [], centers: [] });
      }
      measure();
    }
    function measure(){
      cardW = cardEl.getBoundingClientRect().width || 1;
      rows.forEach(function(r){
        r.spans = [].slice.call(r.el.children);
        const first = r.spans[0], mid2 = r.spans[n];
        r.setW = mid2.offsetLeft - first.offsetLeft;
        r.centers = r.spans.slice(0, n).map(function(sp){ return sp.offsetLeft + sp.offsetWidth / 2; });
      });
    }
    // Фокус за замовчуванням — по центру (середній рядок, питання біля центру
    // картки). Коли курсор на якомусь питанні, фокус переходить на нього: воно
    // стає різким і лаймовим, підсвітка центру гасне, а його рядок зупиняється,
    // щоб питання не втекло з-під курсора. Усе з плавним наростанням (sp._h,
    // hov), без стрибків.
    let slowTarget = 1, hov = 0, hovSpan = null, ptr = null;
    const hot = [];
    function apply(r, sp, e){
      if (e <= 0.001){
        if (sp._e){ sp.style.color = ''; sp.style.borderColor = ''; sp.style.background = ''; sp.style.textShadow = ''; sp._e = 0; }
        return;
      }
      sp._e = e;
      const al = r.a + (1 - r.a) * e;
      sp.style.color = 'rgba(' + Math.round(255 + (LIME[0] - 255) * e) + ',' + Math.round(255 + (LIME[1] - 255) * e) + ',' + Math.round(255 + (LIME[2] - 255) * e) + ',' + al.toFixed(3) + ')';
      sp.style.textShadow = e > 0.02 && r.blur > 0 ? '0 0 ' + (r.blur * (1 - e)).toFixed(2) + 'px rgba(255,255,255,' + (r.a * (1 - e)).toFixed(3) + ')' : '';
      sp.style.borderColor = 'rgba(198,255,0,' + (0.14 * r.a + (0.64 - 0.14 * r.a) * e).toFixed(3) + ')';
      sp.style.background = 'rgba(198,255,0,' + (0.03 + 0.09 * e).toFixed(3) + ')';
    }
    function paint(dt){
      const k = Math.min(1, dt * 12);
      // Що під курсором зараз: рядки пливуть, тож перевіряємо щокадру.
      let hs = null;
      if (ptr){
        const t = document.elementFromPoint(ptr.x, ptr.y);
        hs = t && t.closest && t.closest('.exp-cloud-row > span');
        if (hs && !stage.contains(hs)) hs = null;
      }
      hovSpan = hs;
      hov += ((hs ? 1 : 0) - hov) * k;
      if (hs){ hs._h = hs._h || 0; if (hot.indexOf(hs) < 0) hot.push(hs); }
      const box = cardEl.getBoundingClientRect();
      const cx = box.width / 2;
      const stageLeft = stage.getBoundingClientRect().left - box.left;
      rows.forEach(function(r){
        const own = hs && hs.parentNode === r.el;
        r.m += ((own ? 0 : slowTarget) - r.m) * Math.min(1, dt * 6);
        if (!reduceMotion) r.x = (r.x + r.speed * r.m * dt) % r.setW;
        r.el.style.transform = 'translate3d(' + (-r.x).toFixed(2) + 'px,0,0)';
        if (r.d !== 0) return;
        for (let q = 0; q < r.spans.length; q++){
          const sp = r.spans[q];
          if (hot.indexOf(sp) >= 0) continue;   // ці рахуємо нижче
          const c = r.centers[q % n] - r.x + (q >= n ? r.setW : 0) + stageLeft;
          const f = Math.max(0, 1 - Math.abs(c - cx) / (cardW * 0.28));
          apply(r, sp, f * f * (3 - 2 * f) * (1 - hov));
        }
      });
      for (let h = hot.length - 1; h >= 0; h--){
        const sp = hot[h];
        sp._h += ((sp === hs ? 1 : 0) - sp._h) * k;
        const r = rows[sp._r];
        let ec = 0;
        if (r.d === 0){
          const q = r.spans.indexOf(sp);
          const c = r.centers[q % n] - r.x + (q >= n ? r.setW : 0) + stageLeft;
          const f = Math.max(0, 1 - Math.abs(c - cx) / (cardW * 0.28));
          ec = f * f * (3 - 2 * f) * (1 - hov);
        }
        const e = Math.max(sp._h, ec);
        apply(r, sp, e);
        if (sp !== hs && sp._h < 0.002){ sp._h = 0; hot.splice(h, 1); }
      }
    }
    build();
    paint(0);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ measure(); paint(0); });
    window.addEventListener('load', function(){ measure(); paint(0); });

    let raf = 0, last = 0, visible = true;
    function loop(now){
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      paint(dt);
      raf = visible && !document.hidden ? requestAnimationFrame(loop) : 0;
    }
    function run(){ if (!raf && !reduceMotion){ last = performance.now(); raf = requestAnimationFrame(loop); } }
    if ('IntersectionObserver' in window){
      new IntersectionObserver(function(es){ visible = es[0].isIntersecting; if (visible) run(); }).observe(cardEl);
    }
    document.addEventListener('visibilitychange', run);
    run();

    // Курсор над хмарою пригальмовує її; питання під курсором отримує фокус.
    cardEl.addEventListener('pointerenter', function(e){ if (e.pointerType === 'mouse') slowTarget = 0.12; });
    cardEl.addEventListener('pointermove', function(e){
      if (e.pointerType !== 'mouse') return;
      ptr = { x: e.clientX, y: e.clientY };
      if (reduceMotion) paint(0.1);
    });
    cardEl.addEventListener('pointerleave', function(){ slowTarget = 1; ptr = null; if (reduceMotion) paint(0.1); });

    // Клік по підсвіченому питанню середнього рядка відкриває його відповідь.
    stage.addEventListener('click', function(e){
      const sp = e.target.closest('span');
      if (!sp || !sp._e || sp._e < 0.35) return;
      const ans = document.getElementById(sp.getAttribute('data-q') || '');
      const item = ans && ans.closest('.faq-item');
      if (!item) return;
      let shift = 0;
      document.querySelectorAll('.faq-item.open').forEach(function(o){
        if (o !== item && (o.compareDocumentPosition(item) & Node.DOCUMENT_POSITION_FOLLOWING)){
          shift += o.querySelector('.faq-a').offsetHeight;
        }
      });
      if (!item.classList.contains('open')) item.querySelector('.faq-q').click();
      const top = item.getBoundingClientRect().top + window.scrollY - shift - 110;
      window.scrollTo({ top: top, behavior: reduceMotion ? 'instant' : 'smooth' });
    });

    // На телефоні при прокрутці ховається/показується адресний рядок браузера —
    // це шле resize БЕЗ зміни ширини. Раніше кожен такий resize перебудовував
    // хмару з випадковими зсувами, і рядки «стрибали» вперед-назад разом із
    // прокруткою. Тепер перебудова лише при реальній зміні ширини картки, і
    // навіть тоді положення рядків зберігається (як частка від довжини кола).
    let rt = null, lastW = Math.round(cardEl.getBoundingClientRect().width);
    window.addEventListener('resize', function(){
      clearTimeout(rt);
      rt = setTimeout(function(){
        const w = Math.round(cardEl.getBoundingClientRect().width);
        if (w === lastW) return;
        lastW = w;
        const fr = rows.map(function(r){ return r.setW ? r.x / r.setW : 0; });
        build();
        rows.forEach(function(r, i){ if (fr[i] !== undefined) r.x = fr[i] * r.setW; });
        paint(0);
      }, 150);
    }, { passive: true });
  }
  initQuestionCloud(document.getElementById('faqReelList'));

  // ---- Прийом ?uc=... після переходу зі сторінки-каталогу /experiences/ ----
  // Та сторінка своєї форми не має, тож кнопка «Замовити цей досвід» веде
  // сюди через query-параметр замість локального scrollIntoView (дивись
  // orderExperience на початку файлу). Тут той самий виклик другою гілкою
  // (форма вже є на сторінці) довершує префіл. #book у самому URL уже
  // прокрутив сторінку туди рідною поведінкою браузера — виклик нижче лише
  // заповнює коментар і фокусить поле, повторний scrollIntoView до тієї ж
  // точки непомітний. history.replaceState прибирає параметр з адресного
  // рядка, щоб перезавантаження чи шаринг посилання не повторювали префіл
  // мовчки за спиною відвідувача.
  (function(){
    const params = new URLSearchParams(location.search);
    const wanted = params.get('uc');
    if (!wanted || !document.getElementById('book')) return;
    orderExperience(wanted);
    params.delete('uc');
    const rest = params.toString();
    const clean = location.pathname + (rest ? '?' + rest : '') + location.hash;
    history.replaceState(null, '', clean);
  })();

  // Прапорець для страхувальника в <head>: він доводить, що цей файл не просто
  // доїхав, а виконався до кінця. Якщо скрипт заблокували, обірвали або він
  // упав десь вище, прапорця не буде — і страхувальник знімає клас js, після
  // чого всі блоки .reveal стають видимі самі, без появи. Півсайту порожнім не
  // лишається ні за яких обставин.
  window.__siteJs = true;
