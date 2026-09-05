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
