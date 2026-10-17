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

// 注音開／關（預設開、記住選擇）。開著時只有步驟卡這些「他動手時要讀的地方」有注音，
// 範圍在 style.css 用 :root:not(.zy-off) 決定；head 的小腳本會先套一次，關著時不會閃注音。
try { if (localStorage.getItem('mb_zhuyin') === 'off') root.classList.add('zy-off'); } catch (e) {}
var zb = document.getElementById('zyBtn');
function zySync() {
  if (!zb) return;
  var on = !root.classList.contains('zy-off');
  zb.classList.toggle('on', on);
  zb.setAttribute('aria-pressed', on ? 'true' : 'false');
}
zySync();
if (zb) zb.onclick = function () {
  var off = root.classList.toggle('zy-off');
  try { localStorage.setItem('mb_zhuyin', off ? 'off' : 'on'); } catch (e) {}
  zySync();
};

// 側邊欄收合
try { if (localStorage.getItem('mb_side') === 'collapsed') root.classList.add('side-collapsed'); } catch (e) {}
var sb = document.getElementById('sideBtn');
if (sb) sb.onclick = function () {
  var c = root.classList.toggle('side-collapsed');
  try { localStorage.setItem('mb_side', c ? 'collapsed' : 'open'); } catch (e) {}
};

// 側邊欄的抽屜（積木入門、101 遊戲區）：▾ 開合。正在看的頁面所在的抽屜（.here）一律打開，
// 其他抽屜記住上次的選擇。手機的側邊欄疊在內容上面，自動展開會把教材推到很下面，
// 所以手機一律照上次的選擇（預設收起）。
var narrow = window.matchMedia && window.matchMedia('(max-width:820px)').matches;
document.querySelectorAll('.sgroup').forEach(function (g) {
  var k = 'mb_sg_' + g.getAttribute('data-g');
  var btn = g.querySelector('.scaret');
  function set(open) {
    g.classList.toggle('open', open);
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (narrow || !g.classList.contains('here')) {
    try { set(localStorage.getItem(k) === 'open'); } catch (e) {}
  }
  if (btn) btn.onclick = function () {
    var open = !g.classList.contains('open');
    set(open);
    try { localStorage.setItem(k, open ? 'open' : 'closed'); } catch (e) {}
  };
});

// ===== 「做給我看」的紀錄 =====
// 每個考題一份：mb_ev_<id> = {pass, lock, wrong, hint, tries:[{at, seq, conf, ans, want, diag, ms}]}。
// pass 是答對過；wrong 是這次舉手前錯了幾次，老師打暗號後歸零；hint 是看過「不看步驟自己做」的提示。
function evGet(id){
  try { return JSON.parse(localStorage.getItem('mb_ev_' + id)) || {}; } catch(e){ return {}; }
}
function evSet(id, ev){
  try { localStorage.setItem('mb_ev_' + id, JSON.stringify(ev)); } catch(e){}
}

// 「我學會了」的自動版（.check.auto）：不能自己點，看紀錄有沒有答對過
function renderAuto(){
  document.querySelectorAll('.check.auto li[data-ev]').forEach(function(li){
    var ok = !!evGet(li.getAttribute('data-ev')).pass;
    li.classList.toggle('ok', ok);
    li.querySelector('.box').textContent = ok ? '✓' : '';
  });
}
renderAuto();

// 打勾清單 + 完成課程記錄
var lessonId = document.body.getAttribute('data-lesson') || '';
function doneKey(id){ return 'mb_done_' + id; }
function markLessonDone(){
  // 只看課末那份「我學會了」清單，步驟打勾不算進完成判定。
  // .later（⭐⭐，下一課才驗）不擋這一課的完成章，不然今天做完永遠蓋不到章。
  var boxes = document.querySelectorAll('.check.final li:not(.later)');
  if (!boxes.length || !lessonId) return;
  var all = true;
  boxes.forEach(function(li){ if (!li.classList.contains('ok')) all = false; });
  try { if (all) localStorage.setItem(doneKey(lessonId), '1'); else localStorage.removeItem(doneKey(lessonId)); } catch(e){}
  var badge = document.getElementById('doneBadge');
  if (badge) badge.style.display = all ? 'inline-flex' : 'none';
}
document.querySelectorAll('.check:not(.auto) li').forEach(function(li){
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
    fb.title = on ? '專注模式：開（一\u{E01E1}次只看一\u{E01E1}步）' : '專注模式：關（全部攤開）';
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
// 25 秒內沒畫出來（離線、被擋）就換成提示，不要把原始程式碼丟給孩子看。
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
        m.innerHTML = '<div class="mc-offline">🧩 積木圖要連上網路才看得\u{E01E1}到，先照著文字做也可以</div>';
      }
    });
    root.classList.add(ok ? 'blocks-ready' : 'blocks-offline');
    document.dispatchEvent(new CustomEvent('mb:blocks-ready', { detail: { ok: ok } }));
  }

  // 實測 2026-09-20：積木入門 89 塊（48 張卡 ＋ 41 個答案）在本機約 9 秒畫完，
  // 跟 48 塊時差不多——時間主要花在抓 CDN，不是塊數。所以 15 秒其實還夠用，
  // 但塊數變多後網路一慢就容易誤判成離線，拉到 25 秒留約 2.7 倍餘裕。
  // 不要再往上加：真的連不上時，孩子要盯著空白等這麼久才看到提示。
  var timer = setTimeout(function () { finish(false); }, 25000);

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

  // 渲染器是一塊接一塊畫的（2026-10-17 實測快取後每塊約 0.1 秒：第 3 課 6 塊 1.3 秒、圖鑑 49 塊 4.9 秒），
  // 而且看不到的也照樣排隊——收起來的步驟卡、還沒輪到的題目、其他分頁。
  // 所以分兩輪：先畫畫面上看得到的，再補畫藏起來的。藏起來的先把 class 改掉，renderAsync 就不會挑到它。
  // mb:blocks-ready 還是等全部畫完才發（圖鑑測驗要拿藏起來的分頁裡的 SVG 出題）。
  // 只延後「排在看得到的積木前面」的隱藏積木：排在後面的本來就會在看得到的之後才畫，
  // 再多跑一輪 renderAsync 反而多花時間（圖鑑實測：看得到的分頁本來就在最前面，分兩輪全部畫完從 5.0 秒變 7.3 秒）。
  function deferHidden() {
    var all = Array.prototype.slice.call(document.querySelectorAll(SEL));
    var seen = all.map(function (c) { return !!(c.closest('.mc') || c).getClientRects().length; });
    var lastSeen = seen.lastIndexOf(true);
    var later = [];
    all.forEach(function (c, i) {
      if (!seen[i] && i < lastSeen) {               // display:none 的祖先 → 現在看不到
        c.setAttribute('data-lazy', c.className);
        c.className = 'lazy-block';
        later.push(c);
      }
    });
    return later;
  }

  function render() {
    var o = Object.assign(pxt.runner.defaultClientRenderOptions(), {
      snippetReplaceParent: true, showEdit: false, showJavaScript: false, simulator: false
    });
    var later = [];
    registerFieldEditors().then(function () {
      later = deferHidden();
      return pxt.runner.renderAsync(o);
    }).then(function () {
      if (!later.length) return;
      later.forEach(function (c) { c.className = c.getAttribute('data-lazy'); c.removeAttribute('data-lazy'); });
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
  var rep = parseInt(box.getAttribute('data-repeat') || '0', 10) || 0;
  var idleLabel = btn.textContent;
  var timer = null, idx = 0, rounds = 0;

  function draw(pat) {
    var flat = String(pat).replace(/\n/g, '');
    cells.forEach(function (c, i) { c.classList.toggle('on', flat.charAt(i) === '#'); });
  }
  function stop() {
    if (timer) { clearTimeout(timer); timer = null; }
    idx = 0;
    rounds = 0;
    draw(frames[0][0]);
    btn.textContent = idleLabel;
    box.classList.remove('playing');
  }
  function tick() {
    draw(frames[idx][0]);
    var ms = frames[idx][1];
    idx++;
    if (idx >= frames.length) {
      rounds++;
      // data-repeat：播完 N 遍就自己停（「重複 4 次」）。沒給 data-repeat 時行為跟以前一樣。
      if (rep ? rounds >= rep : !loop) { timer = setTimeout(stop, ms); return; }
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
    rounds = 0;
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

// ===== 聲音播放器 =====
// 「play tone」和「演奏 音階」在紙上看不出差別，所以這裡真的讓它響：
// 頻率直接用積木上那個音名的赫茲，playTone 會自己停、ringTone 不會（要按停）。
// AudioContext 必須等使用者點過才能建立，所以第一次按下去才 new。
var _ac = null;
function learnAudio() {
  if (!_ac) {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    _ac = new AC();
  }
  if (_ac.state === 'suspended') _ac.resume();
  return _ac;
}

document.querySelectorAll('.soundplay').forEach(function (box) {
  var btn = box.querySelector('.playbtn');
  var notes;
  try { notes = JSON.parse(box.getAttribute('data-notes')); } catch (e) { return; }
  if (!notes || !notes.length || !btn) return;
  var idleLabel = btn.textContent;
  var timer = null, osc = null, gain = null;

  function silence() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (osc) { try { osc.stop(); } catch (e) {} osc.disconnect(); osc = null; }
    if (gain) { gain.disconnect(); gain = null; }
  }
  function stop() {
    silence();
    btn.textContent = idleLabel;
    box.classList.remove('playing');
  }
  function play(i) {
    var ac = learnAudio();
    if (!ac) { stop(); return; }
    silence();
    // 頻率 0 = 休止符：什麼都不發，只安靜等那段時間（「rest」那塊就靠這個示範）
    if (notes[i][0] > 0) {
      gain = ac.createGain();
      gain.gain.setValueAtTime(0, ac.currentTime);
      gain.gain.linearRampToValueAtTime(0.12, ac.currentTime + 0.01);   // 不要「啪」一聲
      gain.connect(ac.destination);
      osc = ac.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = notes[i][0];
      osc.connect(gain);
      osc.start();
    }
    var ms = notes[i][1];
    if (ms == null) return;              // null = 一直響，要按停（ringTone）
    timer = setTimeout(function () {
      if (i + 1 < notes.length) play(i + 1); else stop();
    }, ms);
  }

  btn.onclick = function () {
    if (box.classList.contains('playing')) { stop(); return; }
    box.classList.add('playing');
    btn.textContent = '⏹ 讓它閉嘴';
    play(0);
  };

  // 這張卡被折起來就閉嘴
  var card = box.closest ? box.closest('.step') : null;
  if (card && window.MutationObserver) {
    new MutationObserver(function () {
      if (card.classList.contains('folded') && box.classList.contains('playing')) stop();
    }).observe(card, { attributes: true, attributeFilter: ['class'] });
  }
});

// ===== 偷看答案前先打字 =====
// 學生會手比腦快，一路點開答案照抄，「先自己拼一次」就跳過了。
// 這道關卡要他打 answer 才給看。說清楚：這是減速丘不是鎖——
// 答案本來就在 HTML 裡，會按 F12 的人照樣看得到，我們擋的是「順手一點」。
// 只擋 .optional.answer，其他選讀（第 8 課的音名那種）不受影響。
(function () {
  var boxes = document.querySelectorAll('details.optional.answer');
  if (!boxes.length) return;
  var WORD = 'answer';
  var gate = null, onPass = null;

  function build() {
    gate = document.createElement('div');
    gate.className = 'gate';
    gate.innerHTML =
      '<div class="gbox" role="dialog" aria-modal="true" aria-label="想看答案？">' +
        '<h3>🙈 想看答案？</h3>' +
        '<p>先自己拼拼看，拼不出來再看 👍</p>' +
        '<p class="ghint">在下面打上 <b>answer</b></p>' +
        '<input class="gin" type="text" autocapitalize="none" autocorrect="off" ' +
               'spellcheck="false" aria-label="打 answer">' +
        '<p class="gerr" hidden>打錯了，再試一\u{E01E1}次 🙈</p>' +
        '<div class="gbtns">' +
          '<button class="btn ghost gno" type="button">再想一\u{E01E1}下</button>' +
          '<button class="btn g gyes" type="button">看答案</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(gate);
    gate.addEventListener('click', function (e) { if (e.target === gate) close(); });
    gate.querySelector('.gno').onclick = close;
    gate.querySelector('.gyes').onclick = check;
    gate.querySelector('.gin').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); check(); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && gate.classList.contains('on')) close();
    });
  }

  function open(cb) {
    if (!gate) build();
    onPass = cb;
    var input = gate.querySelector('.gin');
    input.value = '';
    gate.querySelector('.gerr').hidden = true;
    gate.classList.add('on');
    setTimeout(function () { input.focus(); }, 30);
  }

  function close() { if (gate) gate.classList.remove('on'); onPass = null; }

  function check() {
    // trim ＋ 轉小寫：手機自動大寫成 Answer 也算對，我們不是在考打字
    var v = gate.querySelector('.gin').value.trim().toLowerCase();
    if (v !== WORD) {
      gate.querySelector('.gerr').hidden = false;
      gate.querySelector('.gin').select();
      return;
    }
    var cb = onPass;
    close();
    if (cb) cb();
  }

  boxes.forEach(function (d) {
    var s = d.querySelector('summary');
    if (!s) return;
    s.addEventListener('click', function (e) {
      if (d.open) return;          // 收起來不用擋，只擋「要打開」
      e.preventDefault();          // 先不要展開，等他打對
      open(function () {
        d.open = true;
        // 「不看步驟自己做」的提示：記下來給老師看（右下角會變黃）
        if (d.closest && d.closest('.redo') && lessonId) {
          var ev = evGet(lessonId);
          ev.hint = true;
          evSet(lessonId, ev);
          document.dispatchEvent(new CustomEvent('mb:ev'));
        }
      });
    });
  });
})();

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
        qMsg.textContent = '它在「' + name + '」抽屜喔，再看一\u{E01E1}次 👀';
        qMsg.className = 'qmsg no';
      }
      qNext.style.display = 'block';
    };
  });

  qNext.onclick = ask;
})();

// ===== 通關數字（.qcheck）=====
// 看程式 → 先選有沒有把握 → 用想的打出螢幕上的數字。
// 題目每次隨機出，答案不在頁面上；打錯的數字拿去跟「常見的錯誤想法」算出來的結果比，
// 對到哪一個就只亮那一句提示（提示文字在 HTML 裡，build.py 才加得上注音）。
// 錯兩次就鎖住請他舉手，老師打暗號（data-tw）才繼續。已經通關之後的練習不會再鎖。
// 題型只負責「出一題」：next(box, 上一題的 key) 回傳 {key, want, wrong:[[錯誤想法, 數字]…], show}，
// hide(box) 把題目收起來（通關後回到頁面時用）。其餘流程所有題型共用。
function counterSim(seq, mode) {
  var c = 0;
  seq.forEach(function (k) {
    if (k === 'A') c = mode === 'aset' ? 1 : c + 1;        // aset：以為「改變 1」是變成 1
    else if (mode === 'bplus') c += 1;                     // bplus：以為 B 也是加
    else if (mode !== 'bkeep') c = 0;                      // bkeep：忘了 B 會歸零
  });
  return c;
}
var CHECK_KINDS = {
  // 第 4 課計數器：A「改變 1」＋顯示，B「設為 0」＋顯示。程式固定，JS 隨機出按鍵順序。
  counter: {
    next: function (box, prev) {
      // A×(1–3)、B、[A×(1–2)、B]、A×(2–4)：最後至少兩個 A，
      // 這樣正確答案一定跟三種錯誤想法算出來的都不一樣，錯數字才分得出是哪一種。
      function a(lo, hi) { var n = lo + Math.floor(Math.random() * (hi - lo + 1)), r = []; while (n--) r.push('A'); return r; }
      var seq, tries = 0;
      do {
        seq = a(1, 3).concat(['B']);
        if (Math.random() < 0.5) seq = seq.concat(a(1, 2), ['B']);
        seq = seq.concat(a(2, 4));
      } while (seq.join('') === prev && ++tries < 20);
      return {
        key: seq.join(''),
        want: counterSim(seq, 'ok'),
        wrong: ['aset', 'bkeep', 'bplus'].map(function (m) { return [m, counterSim(seq, m)]; }),  // 對應 COUNTER_DIAGS
        show: function () {
          box.querySelector('.seq').innerHTML = seq.map(function (k) {
            return '<span class="key k' + k + '">' + k + '</span>';
          }).join('');
        }
      };
    },
    hide: function (box) { box.querySelector('.seq').innerHTML = ''; }
  },
  // 積木入門：積木圖只能在載入時畫，所以 build.py 先出好幾個變體（.qv），這裡挑一個秀。
  // data-v 是 base64 的 {w: 答案, d: [[錯誤想法, 數字]…]}——減速丘，不是鎖。
  pool: {
    next: function (box, prev) {
      var vs = Array.prototype.slice.call(box.querySelectorAll('.qv'));
      var i, tries = 0;
      do { i = Math.floor(Math.random() * vs.length); } while (String(i) === prev && vs.length > 1 && ++tries < 20);
      var data = JSON.parse(atob(vs[i].getAttribute('data-v')));
      return {
        key: String(i), want: data.w, wrong: data.d,
        show: function () { vs.forEach(function (v, k) { v.hidden = k !== i; }); }
      };
    },
    hide: function (box) { box.querySelectorAll('.qv').forEach(function (v) { v.hidden = true; }); }
  }
};

document.querySelectorAll('.qcheck').forEach(function (box) {
  var id = box.getAttribute('data-check');
  var kind = CHECK_KINDS[box.getAttribute('data-kind')];
  if (!id || !kind) return;
  var tw = (box.getAttribute('data-tw') || '').toLowerCase();
  var confEl = box.querySelector('.conf');
  var confBtns = Array.prototype.slice.call(box.querySelectorAll('.conf button'));
  var ansRow = box.querySelector('.ansrow');
  var ans = box.querySelector('.ans');
  var nextq = box.querySelector('.nextq');
  var tcode = box.querySelector('.tcode');
  var cur = null, conf = null, shownAt = 0;

  function hideFb() { box.querySelectorAll('.fb').forEach(function (f) { f.hidden = true; }); }
  function show(sel) { var f = box.querySelector(sel); if (f) f.hidden = false; }

  function newQ() {
    cur = kind.next(box, cur ? cur.key : '');
    cur.show();
    conf = null;
    confBtns.forEach(function (b) { b.classList.remove('cur'); b.disabled = false; });
    confEl.hidden = false;
    ansRow.hidden = true;
    ans.value = '';
    ans.disabled = false;
    nextq.hidden = true;
    hideFb();
    shownAt = Date.now();
  }

  function locked() {
    confEl.hidden = true;
    ansRow.hidden = true;
    nextq.hidden = true;
    hideFb();
    show('.fb.help');
  }

  confBtns.forEach(function (b) {
    b.onclick = function () {
      conf = b.getAttribute('data-c');
      confBtns.forEach(function (x) { x.classList.toggle('cur', x === b); });
      ansRow.hidden = false;
      ans.focus();
    };
  });

  function submit() {
    var v = ans.value.trim();
    if (!cur || !conf || !/^\d{1,2}$/.test(v)) { ans.select(); return; }
    var n = parseInt(v, 10), ok = n === cur.want, diag = ok ? '' : 'other';
    if (!ok) {
      for (var i = 0; i < cur.wrong.length; i++) {
        if (cur.wrong[i][1] === n) { diag = cur.wrong[i][0]; break; }
      }
    }
    var ev = evGet(id);
    var practice = !!ev.pass;          // 通關後的練習：照樣記，但不鎖
    ev.tries = ev.tries || [];
    ev.tries.push({ at: new Date().toISOString(), q: cur.key, conf: conf,
                    ans: n, want: cur.want, diag: diag, ms: Date.now() - shownAt });
    ans.disabled = true;
    confBtns.forEach(function (x) { x.disabled = true; });
    hideFb();
    if (ok) {
      ev.pass = true;
      ev.wrong = 0;
      show('.fb.ok');
      nextq.hidden = false;
    } else {
      if (!practice) ev.wrong = (ev.wrong || 0) + 1;
      if (!practice && ev.wrong >= 2) {
        ev.lock = true;
      } else {
        show('.fb.no[data-diag="' + diag + '"]');
        show('.fb.try');
        nextq.hidden = false;
      }
    }
    evSet(id, ev);
    if (ev.lock) locked();
    renderAuto();
    markLessonDone();
    document.dispatchEvent(new CustomEvent('mb:ev'));
  }

  box.querySelector('.go').onclick = submit;
  ans.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); submit(); } });
  nextq.onclick = newQ;

  function unlock() {
    if (tcode.value.trim().toLowerCase() !== tw) { tcode.value = ''; tcode.focus(); return; }
    var ev = evGet(id);
    ev.lock = false;
    ev.wrong = 0;
    ev.unlocks = (ev.unlocks || 0) + 1;
    evSet(id, ev);
    tcode.value = '';
    newQ();
    document.dispatchEvent(new CustomEvent('mb:ev'));
  }
  box.querySelector('.tgo').onclick = unlock;
  tcode.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); unlock(); } });

  newQ();
  var ev0 = evGet(id);
  if (ev0.lock) locked();
  else if (ev0.pass) {
    // 回到這頁時，通關過的直接顯示通關，想再練可以按換一題
    confEl.hidden = true;
    kind.hide(box);
    show('.fb.ok');
    nextq.hidden = false;
  }
});

// 側邊欄的章節：通關過的後面加一顆 ⭐
document.querySelectorAll('.lrow.sub[data-ev]').forEach(function (a) {
  if (evGet(a.getAttribute('data-ev')).pass && !a.querySelector('.done')) {
    var st = document.createElement('span');
    st.className = 'done';
    st.textContent = '⭐';
    a.appendChild(st);
  }
});

// 積木入門目錄：每一章的 ⭐（通關）和 ⭐⭐（下一章暖身）
document.querySelectorAll('.chcard[data-ev]').forEach(function (c) {
  c.classList.toggle('got1', !!evGet(c.getAttribute('data-ev')).pass);
  c.classList.toggle('got2', !!evGet(c.getAttribute('data-ev2')).pass);
});

// ===== 右下角的狀態圓點（給走過去的老師瞄一眼）=====
// 🔴 鎖住在等老師 > 🟣 說有把握卻答錯過 > 🟡 還沒通關但錯過或看過提示 > 🟢 順利
(function () {
  var ids = Array.prototype.map.call(document.querySelectorAll('.qcheck'), function (b) {
    return b.getAttribute('data-check');
  });
  if (document.querySelector('.redo') && lessonId && ids.indexOf(lessonId) < 0) ids.push(lessonId);
  if (!ids.length) return;
  var LABEL = {
    red: '🔴 錯兩次了，在等老師',
    purple: '🟣 說有把握，卻答錯過',
    yellow: '🟡 錯過或看過提示，還沒通關',
    green: '🟢 順利'
  };
  var dot = document.createElement('div');
  dot.className = 'mbstat';
  document.body.appendChild(dot);

  function level(ev) {
    var tries = ev.tries || [];
    if (ev.lock) return 3;
    if (tries.some(function (t) { return t.conf === 'sure' && t.diag; })) return 2;
    if (!ev.pass && (ev.hint || tries.some(function (t) { return t.diag; }))) return 1;
    return 0;
  }
  function paint() {
    var lv = 0;
    ids.forEach(function (i) { lv = Math.max(lv, level(evGet(i))); });
    var s = ['green', 'yellow', 'purple', 'red'][lv];
    dot.setAttribute('data-s', s);
    dot.title = LABEL[s];
    dot.setAttribute('aria-label', LABEL[s]);
  }
  paint();
  document.addEventListener('mb:ev', paint);
})();
