/* SILENT — спільний скрипт української та англомовної версій.
   Вийнятий з двох <script> в index.html, логіка не змінена. Увесь текст, який
   скрипт виводить сам (рядки hero, підписи калькулятора, календар, лайтбокс),
   винесений у window.SILENT_I18N: його оголошує сама сторінка перед цим
   файлом. Так поведінка лишається однією на дві мови, а різниться тільки
   набір рядків. */
const I18N = window.SILENT_I18N;

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
        // progress: how far the section center is from the viewport center
        const sectionCenter = r.top + r.height / 2;
        let delta = (sectionCenter - vh / 2) * -l.speed;
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
  const heroPhotos = [0,1,2].map(i => document.getElementById('heroPhoto' + i)).filter(Boolean);
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

  const heroNarrow = window.matchMedia('(max-width: 760px)');
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
  // документа — на старті сторінки це заважає першому paint. Класи ж
  // (heroPhoto/heroDancer .active) мають лишитись синхронними: якщо
  // додати їх пізніше, ПІСЛЯ того як браузер уже намалював кадр без них,
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
    // Активний лишається один — інакше три знімки світилися б один крізь одного.
    heroPhotos.forEach((p, idx) => p.classList.toggle('active', idx === i));
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

  // База: 40 навушників / 4 год = 9 800 грн. Стеля: 90 навушників / 4 год = 22 000 грн.
  // Максимальна конфігурація (90 навушників, 8 год, усі три опції) дає рівно
  // 50 000 грн: 22 000 пакет + 22 000 за 4 додаткові години + 3 × 2 000 опції.
  const MAX_QTY = 90;
  function calcPrice(qty){
    const base = 9800;
    const extraQty = Math.max(0, qty - 40);
    const extra = Math.round(extraQty * (12200 / (MAX_QTY - 40)));
    // Година рахується від самого пакета, а не фіксованою ставкою: базові
    // 4 години коштують base + extra, тож одна година — рівно чверть від цього.
    const hourPrice = Math.round((base + extra) / MIN_HOURS);
    const extraHours = Math.max(0, hours - MIN_HOURS);
    const hoursCost = extraHours * hourPrice;
    const options =
      (outsideKyiv.checked ? 2000 : 0) +
      (contentReel.checked ? 2000 : 0) +
      (smokeLight.checked ? 2000 : 0);
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
    // At the ceiling show "90+": the slider stops there, but larger events are
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
  hourMinus.addEventListener('click', () => {
    if (hours > MIN_HOURS){ hours--; hoursValueEl.textContent = hours; updateCalculator(); }
  });
  hourPlus.addEventListener('click', () => {
    if (hours < MAX_HOURS){ hours++; hoursValueEl.textContent = hours; updateCalculator(); }
  });
  updateCalculator();

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
          alt: img ? img.getAttribute('alt') : ''
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

    function fill(){
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
    const start = () => { if (period) { view.scrollLeft = MID * period; fill(); } };

    view.addEventListener('pointerdown', () => { held = 1; }, { passive: true });
    ['pointerup','pointercancel','touchend','touchcancel'].forEach(ev =>
      window.addEventListener(ev, () => { held = 0; }, { passive: true }));
    view.addEventListener('scroll', () => { normalise(); sync(); }, { passive: true });

    let touched = false;
    ['pointerdown','touchstart','wheel','keydown'].forEach(ev =>
      view.addEventListener(ev, () => { touched = true; }, { passive: true }));

    function nudge(dir){ view.scrollBy({ left: dir * step * 2, behavior: 'smooth' }); }
    if (prev) prev.addEventListener('click', () => nudge(-1));
    if (next) next.addEventListener('click', () => nudge(1));

    // картки переставні, тож кнопки замовлення ловимо делегуванням
    view.addEventListener('click', (e) => {
      const btn = e.target.closest('.uc-order');
      if (!btn) return;
      const card = btn.closest('.uc-card');
      const name = card && card.dataset.uc;
      if (!name) return;
      const line = I18N.uc.line(name);
      const field = document.getElementById('comment');
      if (field && !field.value.includes(line)) {
        field.value = field.value ? field.value + '\n' + line : line;
      }
      const note = document.getElementById('calcSummaryNote');
      if (note) {
        note.style.display = 'block';
        note.innerHTML = I18N.uc.note(name);
      }
      const form = document.getElementById('book');
      if (form) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(() => { if (field) field.focus({ preventScroll: true }); }, 600);
    });

    // ---- Паралакс між рядами ----
    // Ряди пливуть у різні боки, поки секція йде через екран. Суто візуально:
    // трансформи не чіпають scrollLeft, тож на арифметику слотів не впливають.
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce && rows.length > 1){
      const DRIFT = 46;
      let ticking = false;
      function drift(){
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
    const boot = () => { if (booted) return; booted = true; build(); start(); remember(); };
    window.addEventListener('resize', () => {
      if (!booted) return;                 // ще нема чого перебудовувати
      if (view.clientWidth === lastW && metrics()[0] === lastCol) return;
      clearTimeout(rt);
      rt = setTimeout(() => { build(); start(); remember(); }, 200);
    }, { passive: true });

    whenNear(document.getElementById('cases'), boot);
    // start() усередині захищений `if (period)`, тож до побудови він тихо
    // нічого не робить — колбек прогріву кешу лишається безпечним.
    warmStripCache(document.getElementById('cases'), urls, () => { if (!touched) start(); });
  })();

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

  litOnScroll(document.querySelector('.slabs'), '.slab', { pinOnTap: true });
  litOnScroll(document.querySelector('.flow'), '.flow-step', { mode: 'progress' });
  litOnScroll(document.querySelector('.benefits-grid'), '.benefit-card', { mode: 'progress' });

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
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach((el, i) => {
    // Усередині нескінченних стрічок поодинокі появи заборонені: там сотні
    // клонованих карток, і кожна проявлялась би окремо — при вертикальній
    // прокрутці порядно, при горизонтальній по одній, збиваючи паралакс.
    // Стрічка проявляється цілком, одним контейнером.
    if (el.closest('.uc-grid, .gallery-grid')) { el.classList.add('in'); return; }
    el.style.transitionDelay = (Math.min(i%4,3)*0.06)+'s';
    io.observe(el);
  });

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
        }
      });
      if (isOpen) {
        item.classList.remove('open');
        a.style.maxHeight = null;
      } else {
        item.classList.add('open');
        a.style.maxHeight = a.scrollHeight + 'px';
      }
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
    document.querySelectorAll('.benefits-aurora, .uc-aurora, .band-aurora').forEach(box => {
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
      // неї саму — тож масштабуємо їх під висоту коробки.
      const k = Math.min(1, Math.max(0.26, box.getBoundingClientRect().height / 1040));
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
    const grid = document.getElementById('galGrid');
    if (!box || !grid) return;
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
      grid.querySelectorAll('.gal-play').forEach(b => {
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

    function openLeadModal() {
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

  // Захист від дубля generate_lead: форму технічно можна надіслати повторно
  // (кнопка ховається лише після успіху, а не блокується одразу), тож без
  // цього прапорця повторний клік чи гонка подій дали б два events на один лід.
  let leadEventSent = false;

  document.getElementById('submitBtn').addEventListener('click', () => {
    const name = document.getElementById('name').value.trim();
    const contact = document.getElementById('contact').value.trim();
    if (!name || !contact){
      alert(I18N.form.required);
      return;
    }

    const formData = {
      name: name,
      contact: contact,
      eventType: document.getElementById('type').value,
      guests: document.getElementById('guests').value,
      eventDate: document.getElementById('date').value,
      discovery: document.getElementById('source').value,
      comment: document.getElementById('comment').value.trim(),
      leadId: sessionStorage.getItem('lead_id'),
      submittedDate: new Date().toISOString().split('T')[0],
      submittedTime: new Date().toTimeString().split(' ')[0],
      status: 'Нова',
    };

    const utm = JSON.parse(sessionStorage.getItem('lead_utm') || '{}');
    const tech = JSON.parse(sessionStorage.getItem('lead_tech') || '{}');
    const referrer = document.referrer || '';
    const landingPage = window.location.pathname;
    Object.assign(formData, utm, tech, { referrer, landingPage });

    const GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwdSqc1-M0KmHBwIE8_EANY7dbPbqVcOmdTbl-gfDxyASabYJXW55mGQIXhlOBRRLwS/exec';
    fetch(GOOGLE_SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(formData),
      mode: 'no-cors'
    }).catch(err => console.error('Помилка при відправці заявки:', err));

    document.getElementById('formFields').style.display = 'none';
    document.getElementById('formSuccess').classList.add('show');
    if (typeof window.__openLeadModal === 'function') window.__openLeadModal();

    // GA4: generate_lead — рівно тут, бо саме це і є «успішна відправка» в
    // термінах цієї форми (mode:'no-cors' не дає прочитати відповідь Apps
    // Script, тож успіхом вважається пройдена валідація й показ formSuccess,
    // так само як і для самого запису в Google Sheets вище).
    // Жодних персональних даних: ні ім'я, ні контакт, ні коментар сюди не йдуть.
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
  });

