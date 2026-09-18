// ===== micro:bit 積木冒險 · 互動 =====
var root = document.documentElement;

// 深/淺色（記住選擇）
try { if (localStorage.getItem('mb_theme') === 'dark') root.setAttribute('data-theme', 'dark'); } catch (e) {}
var tb = document.getElementById('themeBtn');
if (tb) tb.onclick = function () {
  var cur = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', cur);
  try { localStorage.setItem('mb_theme', cur); } catch (e) {}
};

// 側邊欄收合
try { if (localStorage.getItem('mb_side') === 'collapsed') root.classList.add('side-collapsed'); } catch (e) {}
var sb = document.getElementById('sideBtn');
if (sb) sb.onclick = function () {
  var c = root.classList.toggle('side-collapsed');
  try { localStorage.setItem('mb_side', c ? 'collapsed' : 'open'); } catch (e) {}
};

// 打勾清單 + 完成課程記錄
var lessonId = document.body.getAttribute('data-lesson') || '';
function doneKey(id){ return 'mb_done_' + id; }
function markLessonDone(){
  // 只看課末那份「我學會了」清單，步驟打勾不算進完成判定
  var boxes = document.querySelectorAll('.check.final li');
  if (!boxes.length || !lessonId) return;
  var all = true;
  boxes.forEach(function(li){ if (!li.classList.contains('ok')) all = false; });
  try { if (all) localStorage.setItem(doneKey(lessonId), '1'); else localStorage.removeItem(doneKey(lessonId)); } catch(e){}
  var badge = document.getElementById('doneBadge');
  if (badge) badge.style.display = all ? 'inline-flex' : 'none';
}
document.querySelectorAll('.check li').forEach(function(li){
  var k = 'mb_chk_' + lessonId + '_' + li.getAttribute('data-k');
  try { if (localStorage.getItem(k) === '1'){ li.classList.add('ok'); li.querySelector('.box').textContent='✓'; } } catch(e){}
  li.onclick = function(){
    var on = li.classList.toggle('ok');
    li.querySelector('.box').textContent = on ? '✓' : '';
    try { on ? localStorage.setItem(k,'1') : localStorage.removeItem(k); } catch(e){}
    markLessonDone();
  };
});
markLessonDone();

// ===== 步驟卡：打勾 ＋ 專注模式（一次只展開一步，預設開）=====
// 專注模式是給注意力不容易集中的小朋友用的：畫面上同時只亮一步，
// 打勾之後自動翻到下一步，其他步驟收起來不干擾。
var FOCUS_KEY = 'mb_focus';
function focusOn(){
  try { return localStorage.getItem(FOCUS_KEY) !== 'off'; } catch(e){ return true; }
}

var steps = Array.prototype.slice.call(document.querySelectorAll('.step'));
var curStep = null;

function stepKey(st){ return 'mb_step_' + lessonId + '_' + st.getAttribute('data-k'); }
function stepDone(st){ return st.classList.contains('ok'); }

function firstUndone(){
  for (var i = 0; i < steps.length; i++) if (!stepDone(steps[i])) return steps[i];
  return steps[steps.length - 1];   // 全部做完就停在最後一步
}
function nextUndone(after){
  for (var i = steps.indexOf(after) + 1; i < steps.length; i++) {
    if (!stepDone(steps[i])) return steps[i];
  }
  return null;
}

function renderSteps(){
  if (!steps.length) return;
  if (!focusOn()){
    steps.forEach(function(st){ st.classList.remove('folded', 'cur'); });
    return;
  }
  if (!curStep || steps.indexOf(curStep) < 0) curStep = firstUndone();
  steps.forEach(function(st){
    st.classList.toggle('folded', st !== curStep);
    st.classList.toggle('cur', st === curStep);
  });
}

function showStep(st){
  curStep = st;
  renderSteps();
  try { st.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  catch(e){ st.scrollIntoView(); }
}

function toggleStep(st){
  var on = !stepDone(st);
  st.classList.toggle('ok', on);
  var box = st.querySelector('.sbox');
  if (box) box.textContent = on ? '✓' : '';
  try { on ? localStorage.setItem(stepKey(st), '1') : localStorage.removeItem(stepKey(st)); } catch(e){}

  var nxt = on && focusOn() ? nextUndone(st) : null;
  if (nxt) showStep(nxt); else renderSteps();
}

steps.forEach(function(st){
  var box = st.querySelector('.sbox');
  var hd = st.querySelector('.hd');
  if (!box || !hd) return;
  try { if (localStorage.getItem(stepKey(st)) === '1'){ st.classList.add('ok'); box.textContent = '✓'; } } catch(e){}

  // 打勾框永遠是「做完了」
  box.onclick = function(e){ e.stopPropagation(); toggleStep(st); };
  // 標題列：收起來的步驟點一下是「打開來看」，正在做的那一步點一下才是打勾
  hd.onclick = function(){
    if (focusOn() && st !== curStep) showStep(st);
    else toggleStep(st);
  };
});

var fb = document.getElementById('focusBtn');
if (fb) {
  var syncFocusBtn = function(){
    var on = focusOn();
    fb.classList.toggle('on', on);
    fb.textContent = on ? '🎯' : '📖';
    fb.title = on ? '專注模式：開（一次只看一步）' : '專注模式：關（全部攤開）';
  };
  syncFocusBtn();
  fb.onclick = function(){
    try { localStorage.setItem(FOCUS_KEY, focusOn() ? 'off' : 'on'); } catch(e){}
    syncFocusBtn();
    curStep = null;
    renderSteps();
  };
}

renderSteps();

// 首頁：把已完成的課程加上 ✓
document.querySelectorAll('.lesson[data-lesson]').forEach(function(a){
  try { if (localStorage.getItem(doneKey(a.getAttribute('data-lesson'))) === '1') a.classList.add('done'); } catch(e){}
});

// ===== 積木圖：交給 MakeCode 官方渲染器畫（外觀跟編輯器完全一樣）=====
// head 已經先設好 PXT_LANG=zh-TW cookie，並用 async 載入 makecode.microbit.org/--embed。
// 這裡等 runner 就緒再渲染；畫完發出 mb:blocks-ready 事件（圖鑑測驗要等 SVG 出來才能出題）。
// 15 秒內沒畫出來（離線、被擋）就換成提示，不要把原始程式碼丟給孩子看。
(function () {
  var SEL = 'code.lang-block, code.lang-blocks, code.lang-blocksxml';
  if (!document.querySelector(SEL)) return;
  var done = false;

  function finish(ok) {
    if (done) return;
    done = true;
    // 還留著原始 <code> 的片段就是沒畫出來的，只替換那些
    document.querySelectorAll('.mc').forEach(function (m) {
      if (m.querySelector(SEL)) {
        m.innerHTML = '<div class="mc-offline">🧩 積木圖要連上網路才看得到，先照著文字做也可以</div>';
      }
    });
    root.classList.add(ok ? 'blocks-ready' : 'blocks-offline');
    document.dispatchEvent(new CustomEvent('mb:blocks-ready', { detail: { ok: ok } }));
  }

  var timer = setTimeout(function () { finish(false); }, 15000);

  // MakeCode 文件站會另外載入 fieldeditors.js，註冊「姿勢」「引腳」這種特製下拉。
  // 只用 --embed 不會載入它，「當姿勢 晃動 發生」的「晃動 ▾」就整個不見（實測踩過）。
  // 網址從 pxt.webConfig 取，跟著 MakeCode 版本走，不寫死 commit。
  function registerFieldEditors() {
    return new Promise(function (resolve) {
      try {
        var s = document.createElement('script');
        s.src = pxt.webConfig.commitCdnUrl + 'fieldeditors.js';
        s.onload = function () {
          var init = pxt.editor && pxt.editor.initFieldExtensionsAsync;
          Promise.resolve(init ? init({}) : null).then(function (res) {
            ((res && res.fieldEditors) || []).forEach(function (fe) {
              pxt.blocks.registerFieldEditor(fe.selector, fe.editor, fe.validator);
            });
          }).catch(function () {}).then(resolve);
        };
        s.onerror = resolve;   // 載不到就照畫，只是姿勢下拉會少字
        document.head.appendChild(s);
      } catch (e) { resolve(); }
    });
  }

  function render() {
    var o = Object.assign(pxt.runner.defaultClientRenderOptions(), {
      snippetReplaceParent: true, showEdit: false, showJavaScript: false, simulator: false
    });
    registerFieldEditors().then(function () {
      return pxt.runner.renderAsync(o);
    }).then(function () {
      clearTimeout(timer);
      finish(!document.querySelector(SEL));
    }, function () {
      clearTimeout(timer);
      finish(false);
    });
  }

  // 載入器是 async 的：先等它定義出 ksRunnerReady，再用它排隊，等 MakeCode 真的初始化完才渲染。
  // 不能直接偵測 pxt.runner——物件會先出現、目標還沒載好，renderAsync 什麼都沒畫就結束（實測踩過）。
  (function wait() {
    if (typeof window.ksRunnerReady === 'function') return window.ksRunnerReady(render);
    if (!done) setTimeout(wait, 150);
  })();
})();

// ===== 積木入門的小小 LED 播放器 =====
// MakeCode 官方模擬器不能嵌在第三方網站（實測 /---run 會回「Oops, wrong arguments」），
// 所以自己做一個：照 data-frames 的「圖樣 ＋ 停留毫秒」切換 25 顆燈的 .on。
// 步驟卡被收起來時自動停，才不會有看不見的動畫在背景一直跑。
document.querySelectorAll('.ledplay').forEach(function (box) {
  var cells = Array.prototype.slice.call(box.querySelectorAll('.leds i'));
  var btn = box.querySelector('.playbtn');
  var frames;
  try { frames = JSON.parse(box.getAttribute('data-frames')); } catch (e) { return; }
  if (!frames || !frames.length || !btn) return;
  var loop = box.getAttribute('data-loop') === '1';
  var idleLabel = btn.textContent;
  var timer = null, idx = 0;

  function draw(pat) {
    var flat = String(pat).replace(/\n/g, '');
    cells.forEach(function (c, i) { c.classList.toggle('on', flat.charAt(i) === '#'); });
  }
  function stop() {
    if (timer) { clearTimeout(timer); timer = null; }
    idx = 0;
    draw(frames[0][0]);
    btn.textContent = idleLabel;
    box.classList.remove('playing');
  }
  function tick() {
    draw(frames[idx][0]);
    var ms = frames[idx][1];
    idx++;
    if (idx >= frames.length) {
      if (!loop) { timer = setTimeout(stop, ms); return; }
      idx = 0;
    }
    timer = setTimeout(tick, ms);
  }

  draw(frames[0][0]);
  btn.onclick = function () {
    if (timer) { stop(); return; }
    box.classList.add('playing');
    btn.textContent = '⏹ 停下來';
    idx = 0;
    tick();
  };

  // 這張卡被折起來就停
  var card = box.closest ? box.closest('.step') : null;
  if (card && window.MutationObserver) {
    new MutationObserver(function () {
      if (card.classList.contains('folded') && timer) stop();
    }).observe(card, { attributes: true, attributeFilter: ['class'] });
  }
});

// ===== 積木圖鑑 101 =====
// 兩種狀態：seen（翻圖鑑點過）和 got（測驗答對過）。進度條算的是 got。
(function () {
  var dex = document.getElementById('dex');
  if (!dex) return;                       // 其他頁面直接跳過

  var cards = Array.prototype.slice.call(dex.querySelectorAll('.dexcard'));
  var total = cards.length;
  var pNum = document.getElementById('p101');
  var pFill = document.getElementById('p101fill');
  var badge = document.getElementById('dexBadge');

  function key(kind, i) { return 'mb101_' + kind + '_' + i; }
  function read(kind, i) { try { return localStorage.getItem(key(kind, i)) === '1'; } catch (e) { return false; } }
  function save(kind, i, on) {
    try { on ? localStorage.setItem(key(kind, i), '1') : localStorage.removeItem(key(kind, i)); } catch (e) {}
  }

  function refresh() {
    var got = cards.filter(function (c) { return c.classList.contains('got'); }).length;
    if (pNum) pNum.textContent = got;
    if (pFill) pFill.style.width = (total ? got / total * 100 : 0) + '%';
    if (badge) badge.style.display = (got === total && total) ? 'inline-flex' : 'none';
  }

  cards.forEach(function (c) {
    var i = c.getAttribute('data-i');
    if (read('seen', i)) c.classList.add('seen');
    if (read('got', i)) c.classList.add('got');
    c.onclick = function () {
      var on = c.classList.toggle('seen');
      save('seen', i, on);
    };
  });
  refresh();

  // ---- 抽屜分頁 ----
  dex.querySelectorAll('.dextab').forEach(function (t) {
    t.onclick = function () {
      var cat = t.getAttribute('data-cat');
      dex.querySelectorAll('.dextab').forEach(function (x) { x.classList.toggle('cur', x === t); });
      dex.querySelectorAll('.dexpanel').forEach(function (p) {
        p.classList.toggle('cur', p.getAttribute('data-cat') === cat);
      });
    };
  });

  // ---- 模式切換 ----
  var quiz = document.getElementById('quiz');
  var mDex = document.getElementById('modeDex');
  var mQuiz = document.getElementById('modeQuiz');
  function setMode(quizOn) {
    dex.hidden = quizOn;
    quiz.hidden = !quizOn;
    mDex.classList.toggle('cur', !quizOn);
    mQuiz.classList.toggle('cur', quizOn);
    if (quizOn) ask();
  }
  mDex.onclick = function () { setMode(false); };
  mQuiz.onclick = function () { setMode(true); };

  // ---- 出題 ----
  var qBlock = document.getElementById('qblock');
  var qMsg = document.getElementById('qmsg');
  var qNext = document.getElementById('qnext');
  var opts = Array.prototype.slice.call(quiz.querySelectorAll('.qopt'));
  var cur = null;

  function ask() {
    // 先考還沒收集到的；全部收集完就整副重抽
    var pool = cards.filter(function (c) { return !c.classList.contains('got'); });
    if (!pool.length) pool = cards;
    cur = pool[Math.floor(Math.random() * pool.length)];

    qBlock.innerHTML = '';
    // 題目直接拿圖鑑卡片上已經渲染好的 SVG（官方渲染器畫的，本來就沒有抽屜名，不會洩答案）
    var svg = cur.querySelector('.bwrap svg');
    if (svg) {
      var box = document.createElement('div');
      box.className = 'mc';
      box.appendChild(svg.cloneNode(true));
      qBlock.appendChild(box);
    } else if (!root.classList.contains('blocks-ready') && !root.classList.contains('blocks-offline')) {
      // 還沒畫完就先等，畫完再出題
      qBlock.textContent = '🧩 積木載入中…';
      document.addEventListener('mb:blocks-ready', function () { if (!quiz.hidden) ask(); }, { once: true });
      return;
    } else {
      // 離線：沒有積木圖，就用一句話描述出題
      qBlock.textContent = '「' + cur.querySelector('.d').textContent + '」';
    }
    qMsg.textContent = '';
    qMsg.className = 'qmsg';
    qNext.style.display = 'none';
    opts.forEach(function (o) { o.classList.remove('right', 'wrong'); o.disabled = false; });
  }

  opts.forEach(function (o) {
    o.onclick = function () {
      if (!cur || o.disabled) return;
      var want = cur.getAttribute('data-cat');
      var picked = o.getAttribute('data-cat');
      opts.forEach(function (x) { x.disabled = true; });

      if (picked === want) {
        o.classList.add('right');
        cur.classList.add('got');
        save('got', cur.getAttribute('data-i'), true);
        // 答對也算看過
        cur.classList.add('seen');
        save('seen', cur.getAttribute('data-i'), true);
        qMsg.textContent = '答對了！收集 +1 🏅';
        qMsg.className = 'qmsg ok';
        refresh();
      } else {
        // 答錯不扣分，直接指出正確答案，這題留在題庫裡下次再出
        o.classList.add('wrong');
        opts.forEach(function (x) { if (x.getAttribute('data-cat') === want) x.classList.add('right'); });
        var name = '';
        opts.forEach(function (x) { if (x.getAttribute('data-cat') === want) name = x.textContent.trim(); });
        qMsg.textContent = '它在「' + name + '」抽屜喔，再看一次 👀';
        qMsg.className = 'qmsg no';
      }
      qNext.style.display = 'block';
    };
  });

  qNext.onclick = ask;
})();
