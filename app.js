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
  var boxes = document.querySelectorAll('.check li');
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

// 首頁：把已完成的課程加上 ✓
document.querySelectorAll('.lesson[data-lesson]').forEach(function(a){
  try { if (localStorage.getItem(doneKey(a.getAttribute('data-lesson'))) === '1') a.classList.add('done'); } catch(e){}
});
