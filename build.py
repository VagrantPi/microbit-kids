#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從單一課程大綱生成整個 micro:bit 教材網站。新增/修改課程只要改這裡再重跑。"""
import os, html
REPO = os.path.dirname(os.path.abspath(__file__))

# ===== 課程大綱（單一來源，側邊欄與首頁都從這裡長出來）=====
LESSONS = [
    dict(id="l1", em="🔤", short="認識 micro:bit", title="認識 micro:bit ＆ 我的第一支程式",
         sub="打招呼、顯示愛心和你的名字", status="open"),
    dict(id="l2", em="🎨", short="LED 畫畫板", title="LED 畫畫板",
         sub="用 25 顆燈畫圖、做動畫", status="open"),
    dict(id="l3", em="🅰️", short="按鈕魔法", title="按鈕魔法", sub="按 A、按 B 做不同的事", status="open"),
    dict(id="l4", em="🔢", short="神奇計數器", title="神奇計數器", sub="學會「變數」，按一下加一", status="open"),
    dict(id="l5", em="🔁", short="重複的力量", title="重複的力量", sub="用迴圈做跑馬燈和閃爍", status="soon"),
    dict(id="l6", em="🎲", short="搖一搖骰子", title="搖一搖骰子", sub="亂數加判斷，做電子骰子", status="soon"),
    dict(id="l7", em="🌡️", short="神奇感測器", title="神奇感測器", sub="溫度、光線、傾斜都感覺得到", status="soon"),
    dict(id="l8", em="🎵", short="音樂盒", title="音樂盒", sub="播放音符，做一個小樂器", status="soon"),
    dict(id="l9", em="🏆", short="電子寵物", title="電子寵物大挑戰", sub="把學會的通通用上！", status="soon"),
]

# ===== 小工具 =====
def esc(s): return html.escape(str(s))

def head(title):
    return ('<!doctype html><html lang="zh-Hant"><head>\n'
            '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n<link rel="stylesheet" href="style.css">\n'
            '<script>try{if(localStorage.getItem("mb_theme")==="dark")document.documentElement.setAttribute("data-theme","dark");'
            'if(localStorage.getItem("mb_side")==="collapsed")document.documentElement.classList.add("side-collapsed")}catch(e){}</script>\n'
            '</head>')

def topbar():
    return ('<header class="bar"><div class="in">'
            '<button class="iconbtn" id="sideBtn" title="收合選單" aria-label="收合選單">☰</button>'
            '<a class="brand" href="index.html" style="text-decoration:none"><span class="chip">micro:bit</span> 積木冒險</a>'
            '<span class="spacer"></span>'
            '<button class="iconbtn" id="themeBtn" title="換個顏色" aria-label="切換深淺色">🌙</button>'
            '</div></header>')

def sidebar(cur):
    rows = ['<nav class="outline"><div class="cap">🗺️ 課程地圖</div>']
    for i, L in enumerate(LESSONS, 1):
        if L["status"] == "open":
            c = " cur" if L["id"] == cur else ""
            rows.append(f'<a class="lrow{c}" href="{L["id"]}.html"><span class="em">{L["em"]}</span>'
                        f'<span>{i}. {esc(L["short"])}</span></a>')
        else:
            rows.append(f'<span class="lrow soon"><span class="em">{L["em"]}</span>'
                        f'<span>{i}. {esc(L["short"])}</span><span class="lock">🔒</span></span>')
    rows.append('</nav>')
    return '<aside class="side">' + ''.join(rows) + '</aside>'

def page(cur, body, title, lesson_attr=""):
    return (head(title) + f'<body{lesson_attr}>' + topbar() +
            '<div class="wrap"><div class="layout">' + sidebar(cur) +
            '<main class="content">' + body + '</main></div></div>\n<script src="app.js"></script></body></html>\n')

# ---- 積木產生器 ----
def blk(cat, tag, *chunks, hat=False, nest_html=""):
    cls = f"block b-{cat}" + (" hat" if hat else "")
    inner = f'<span class="tag">{esc(tag)}</span>' + "".join(chunks)
    out = f'<div class="{cls}">{inner}</div>'
    if nest_html:
        out += f'<div class="nest">{nest_html}</div>'
    return out
def slot(t, round=False): return f'<span class="slot{" round" if round else ""}">{esc(t)}</span>'
def prog(*items): return '<div class="prog">' + "".join(items) + '</div>'

# ---- LED 5x5 螢幕 ----
def leds(pattern, cap=""):
    rows = [r for r in pattern.strip("\n").split("\n")]
    cells = ""
    for r in rows:
        for ch in r.ljust(5)[:5]:
            cells += '<i class="on"></i>' if ch == '#' else '<i></i>'
    capt = f'<span class="led-cap">{esc(cap)}</span>' if cap else ""
    return f'<span class="led-wrap"><span class="leds">{cells}</span>{capt}</span>'

HEART = "#.#.#\n#####\n#####\n.###.\n..#.."
SMILE = "#...#\n.....\n#...#\n#...#\n.###."
SAD   = "#...#\n.....\n#...#\n.###.\n#...#"
DUCK  = ".##..\n####.\n.####\n.###.\n....."
ARROW = "..#..\n.###.\n#.#.#\n..#..\n..#.."
THREE = ".###.\n....#\n..##.\n....#\n.###."

def checklist(lesson_id, items):
    out = ['<ul class="check">']
    for k, t in enumerate(items):
        out.append(f'<li data-k="{k}"><span class="box"></span><span>{esc(t)}</span></li>')
    out.append('</ul>')
    return "".join(out)

def nav(prev=None, next=None):
    left = f'<a class="btn ghost" href="{prev[0]}.html">← {esc(prev[1])}</a>' if prev else '<a class="btn ghost" href="index.html">← 回地圖</a>'
    right = f'<a class="btn g" href="{next[0]}.html">{esc(next[1])} →</a>' if next else ''
    return f'<div class="nav">{left}<span class="sp"></span>{right}</div>'

def nav_for(lid):
    """依課程大綱自動算出上一課／下一課（只連到已開放的課）。"""
    opened = [L for L in LESSONS if L["status"] == "open"]
    ids = [L["id"] for L in opened]
    i = ids.index(lid)
    def num(L): return LESSONS.index(L) + 1
    prev = ("index", "回地圖") if i == 0 else (opened[i-1]["id"], f"第 {num(opened[i-1])} 課")
    nxt = None if i == len(opened)-1 else (opened[i+1]["id"], f"第 {num(opened[i+1])} 課：{opened[i+1]['short']}")
    return nav(prev, nxt)

def done_badge():
    return ('<span id="doneBadge" class="eyebrow" style="display:none;background:var(--go);margin-left:8px">🎉 這一課完成！</span>')

# ================= 首頁 =================
def build_index():
    cards = ['<div class="grid">']
    for i, L in enumerate(LESSONS, 1):
        if L["status"] == "open":
            cards.append(f'<a class="lesson" href="{L["id"]}.html" data-lesson="{L["id"]}">'
                         f'<span class="no">第 {i} 課</span><span class="em">{L["em"]}</span>'
                         f'<h3>{esc(L["short"])}</h3><p>{esc(L["sub"])}</p></a>')
        else:
            cards.append(f'<div class="lesson soon"><span class="no">第 {i} 課</span>'
                         f'<span class="em">{L["em"]}</span><h3>{esc(L["short"])}</h3><p>{esc(L["sub"])}</p></div>')
    cards.append('</div>')
    body = (
        '<div class="hero"><div class="mb">🤖</div>'
        '<h1>micro:bit 積木冒險</h1>'
        '<p class="lead">你已經會 Scratch 了，對不對？那你已經成功一半了！🎉<br>'
        'micro:bit 的積木長得跟 Scratch 好像，但它是一塊<b>真的電腦</b>——會亮燈、會發出聲音、還會感覺到你在搖它。一起來玩吧！</p>'
        '<div class="pill"><span>🧩 拖積木就會</span><span>💡 馬上看到燈亮</span><span>🎮 每課都做一個小遊戲</span><span>🆓 不用買東西也能玩</span></div>'
        '</div>'
        + leds(HEART, "micro:bit 會這樣跟你打招呼") + leds(SMILE, "還會對你微笑") +
        '<h2>先準備一下 🧰</h2>'
        '<div class="note"><span class="hd">不用急著買 micro:bit！</span>先用電腦上的「模擬器」就能玩。打開 '
        '<code>makecode.microbit.org</code>，按一下<b>「新專案」</b>，右邊會出現一塊會動的 micro:bit——那就是我們的玩具。</div>'
        '<h2>開始冒險 🚀</h2>'
        '<p class="lead" style="margin-top:0">從第 1 課開始，一課一課闖關。完成一課就會蓋一個 🎉 完成章！</p>'
        + "".join(cards) +
        '<footer>micro:bit 積木冒險 · 為小小創客打造 · 用 MakeCode 積木從零開始</footer>'
    )
    open(os.path.join(REPO, "index.html"), "w").write(
        head("micro:bit 積木冒險 · 給小朋友的第一堂程式課") + "<body>" + topbar() +
        '<div class="wrap">' + body + '</div>\n<script src="app.js"></script></body></html>\n')

# ================= 第 1 課 =================
def build_l1():
    body = (
        '<div class="crumb"><a href="index.html">課程地圖</a> / 第 1 課</div>'
        '<span class="eyebrow">第 1 課</span>' + done_badge() +
        '<h1>🔤 認識 micro:bit ＆ 我的第一支程式</h1>'
        '<div class="goal"><div class="big">❤️</div><div><h3>這一課要做到</h3>'
        '<p>讓 micro:bit 亮出一顆<b>愛心</b>，再讓它<b>說出你的名字</b>！</p></div></div>'

        '<h2>1. micro:bit 是什麼？</h2>'
        '<p>它是一塊小小的電腦，只有一片餅乾那麼大，但很厲害：</p>'
        '<div class="note">'
        '💡 <b>正面有 25 顆紅色小燈</b>（排成 5×5），可以排出圖案和文字。<br>'
        '🅰️🅱️ <b>兩顆按鈕</b>叫做 A 和 B，可以按它來玩。<br>'
        '🤝 <b>會感覺</b>：搖一搖、亮不亮、冷不冷，它都知道！<br>'
        '🔊 還會<b>發出聲音</b>唱歌。</div>'
        + leds(HEART, "25 顆燈排出愛心") +

        '<div class="scratch"><span class="hd">🐱 跟 Scratch 比一比</span>'
        'Scratch 是讓螢幕上的<b>貓咪</b>動；micro:bit 是讓你手上<b>真的東西</b>動。積木長得幾乎一樣，'
        '你會 Scratch，就一定學得會！</div>'

        '<h2>2. 打開我們的玩具 🧸</h2>'
        '<div class="note">① 打開瀏覽器，到 <code>makecode.microbit.org</code>。<br>'
        '② 按藍色的<b>「新專案」</b>，幫它取個名字（例如「打招呼」）。<br>'
        '③ 右邊會出現一塊 micro:bit——這是<b>模擬器</b>，沒有真的板子也能看效果！</div>'

        '<h2>3. 拼出第一支程式 🧩</h2>'
        '<p>我們要跟 micro:bit 說：「一開始，就顯示一顆愛心。」把積木拼成這樣：</p>'
        + prog(
            blk("basic", "基本", slot("當程式開始"), hat=True,
                nest_html=blk("basic", "基本", "顯示圖示 ", slot("❤️"))),
        ) +
        '<p>拼好以後，看看右邊的 micro:bit——燈會亮成這樣：</p>'
        + leds(HEART, "成功的話會看到愛心 ❤️") +
        '<div class="tip"><span class="hd">🧩 積木在哪裡？</span>「顯示圖示」在左邊<b>藍色的「基本」</b>抽屜裡。點一下抽屜，把積木拖出來，'
        '放進「當程式開始」的凹槽裡就會卡住（跟 Scratch 一樣會「喀」一聲）。</div>'

        '<h2>4. 讓它說出你的名字 ✨</h2>'
        '<p>再加一塊「顯示文字」，把字換成你的名字（要用英文字母，例如 <code>LILY</code>）：</p>'
        + prog(
            blk("basic", "基本", slot("當程式開始"), hat=True,
                nest_html=blk("basic", "基本", "顯示圖示 ", slot("❤️")) +
                          blk("basic", "基本", "顯示文字 ", slot("LILY"))),
        ) +
        '<p>micro:bit 上的字會像跑馬燈一樣，一個字母一個字母<b>滑過去</b>➡️。太酷了！</p>'

        '<div class="try"><h3>🎯 試試看（換你當魔法師）</h3><ol>'
        '<li>把愛心換成<b>笑臉</b>：在「顯示圖示」點一下圖案，選 😀。</li>'
        '<li>顯示你最喜歡的<b>數字</b>（用「顯示數字」積木）。</li>'
        '<li>先顯示名字、再顯示一顆愛心，順序自己決定！</li>'
        '</ol></div>'

        '<h2>✅ 我學會了</h2><p>點一下把學會的打勾（三個都打勾就完成這一課囉）：</p>'
        + checklist("l1", [
            "我知道 micro:bit 有 25 顆燈和 A、B 兩顆按鈕",
            "我會打開 makecode.microbit.org 開新專案",
            "我讓 micro:bit 顯示了圖案，也顯示了我的名字",
        ]) +
        nav_for("l1")
    )
    open(os.path.join(REPO, "l1.html"), "w").write(page("l1", body, "第 1 課：認識 micro:bit", ' data-lesson="l1"'))

# ================= 第 2 課 =================
def build_l2():
    body = (
        '<div class="crumb"><a href="index.html">課程地圖</a> / 第 2 課</div>'
        '<span class="eyebrow">第 2 課</span>' + done_badge() +
        '<h1>🎨 LED 畫畫板</h1>'
        '<div class="goal"><div class="big">🎨</div><div><h3>這一課要做到</h3>'
        '<p>把 25 顆燈當成<b>畫布</b>，畫出你自己的圖案，還要讓它<b>動起來</b>！</p></div></div>'

        '<h2>1. 25 顆燈 = 一張小畫布</h2>'
        '<p>micro:bit 正面的燈排成 5 排、每排 5 顆。每一顆燈可以<b>亮</b>或<b>不亮</b>，'
        '就像畫畫時決定哪一格塗顏色。塗出不同的格子，就變成不同的圖！</p>'
        + leds(SMILE, "笑臉 😊") + leds(DUCK, "小鴨 🦆") + leds(ARROW, "箭頭 ⬆️") +

        '<h2>2. 認識「顯示 LED」積木 🧩</h2>'
        '<p>在<b>藍色「基本」</b>抽屜裡，有一塊「顯示 LED」積木，上面就是一張 5×5 的小格子。'
        '<b>點一下格子</b>就會亮，再點一下就熄掉——像這樣畫出笑臉：</p>'
        + prog(
            blk("basic", "基本", "顯示 LED", ),
        ) +
        '<div class="tip"><span class="hd">👆 怎麼畫</span>把積木上的格子，照著你想要的圖案一格一格點亮。點亮的格子，'
        '真的 micro:bit 上那顆燈就會發光！</div>'
        + leds(SMILE, "點出這些格子就會變笑臉") +

        '<div class="scratch"><span class="hd">🐱 跟 Scratch 比一比</span>'
        'Scratch 是換<b>造型</b>讓貓咪變樣子；micro:bit 是<b>點亮不同的燈</b>來畫圖。都是「決定看起來長怎樣」。</div>'

        '<h2>3. 讓圖案動起來 🎞️</h2>'
        '<p>動畫的祕密是：<b>換得很快</b>。先給一張圖，停一下下，再換另一張，一直重複，眼睛就覺得它在動！</p>'
        '<p>下面讓愛心一大一小地跳動——用到<b>「暫停」</b>積木（也在「基本」裡），還有<b>綠色「迴圈」</b>裡的「重複無限次」：</p>'
        + prog(
            blk("loop", "迴圈", "重複無限次", hat=True,
                nest_html=blk("basic", "基本", "顯示圖示 ", slot("❤️ 大愛心")) +
                          blk("basic", "基本", "暫停 ", slot("500"), " 毫秒") +
                          blk("basic", "基本", "顯示圖示 ", slot("🩷 小愛心")) +
                          blk("basic", "基本", "暫停 ", slot("500"), " 毫秒")),
        ) +
        '<div class="note"><span class="hd">毫秒是什麼？</span>1000 毫秒 = 1 秒。所以 <code>500</code> 就是半秒。'
        '數字改小一點（例如 200），愛心就會跳得更快！</div>'

        '<h2>4. 內建圖案寶庫 📦</h2>'
        '<p>「顯示圖示」裡藏了好多現成的圖案：愛心、笑臉、哭臉、打勾 ✓、打叉 ✗、小鴨、房子、音符…'
        '點開來每一個都試試看，找出你最喜歡的！</p>'

        '<div class="try"><h3>🎯 試試看（換你當畫家）</h3><ol>'
        '<li>用「顯示 LED」畫出你<b>名字的第一個字母</b>（例如 L、A、T）。</li>'
        '<li>做一個<b>2 格動畫</b>：笑臉 😊 換哭臉 😢 一直換，看它變表情。</li>'
        '<li>畫一個你自己想的圖案（愛心、星星、貓咪…都可以）。</li>'
        '</ol></div>'

        '<h2>✅ 我學會了</h2><p>點一下把學會的打勾：</p>'
        + checklist("l2", [
            "我知道畫面是 5×5、每顆燈可以亮或不亮",
            "我會用「顯示 LED」點格子畫出自己的圖案",
            "我用「暫停」讓兩張圖輪流換，做出動畫",
        ]) +
        nav_for("l2")
    )
    open(os.path.join(REPO, "l2.html"), "w").write(page("l2", body, "第 2 課：LED 畫畫板", ' data-lesson="l2"'))

# ================= 第 3 課 =================
def build_l3():
    body = (
        '<div class="crumb"><a href="index.html">課程地圖</a> / 第 3 課</div>'
        '<span class="eyebrow">第 3 課</span>' + done_badge() +
        '<h1>🅰️ 按鈕魔法</h1>'
        '<div class="goal"><div class="big">🪄</div><div><h3>這一課要做到</h3>'
        '<p>按 <b>A</b> 出現一個表情，按 <b>B</b> 出現另一個——換你當<b>按鈕魔法師</b>！</p></div></div>'

        '<h2>1. 什麼是「事件」？</h2>'
        '<p>事件就是「<b>當…的時候，就做…</b>」。前兩課的程式一開機就自己跑；'
        '這一課不一樣——micro:bit 會<b>乖乖等你</b>，你<b>按下按鈕</b>它才動作。</p>'
        '<div class="scratch"><span class="hd">🐱 跟 Scratch 比一比</span>'
        'Scratch 有「<b>當 🚩 被點擊</b>」「<b>當空白鍵被按下</b>」；micro:bit 換成「<b>當按鈕 A 被按下</b>」。'
        '一模一樣的概念，你早就會了！</div>'

        '<h2>2. 找到「當按鈕 A 被按下」積木 🧩</h2>'
        '<p>它在左邊<b>「輸入」</b>抽屜裡（藍紫色的）。這是一塊<b>帽子積木</b>——'
        '像帽子一樣蓋在最上面，下面夾什麼，按下按鈕就做什麼。</p>'
        + prog(blk("event", "輸入", "當按鈕 ", slot("A", True), " 被按下", hat=True)) +

        '<h2>3. 拼出按鈕魔法 ✨</h2>'
        '<p>做兩頂帽子：按 <b>A</b> 笑臉 😀、按 <b>B</b> 哭臉 😢。</p>'
        + prog(
            blk("event", "輸入", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                nest_html=blk("basic", "基本", "顯示圖示 ", slot("😀"))),
        )
        + prog(
            blk("event", "輸入", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                nest_html=blk("basic", "基本", "顯示圖示 ", slot("😢"))),
        ) +
        '<p>在模擬器上用滑鼠點 <b>A</b> 和 <b>B</b> 試試看：</p>'
        + leds(SMILE, "按 A → 笑臉") + leds(SAD, "按 B → 哭臉") +
        '<div class="note"><span class="hd">💡 兩頂帽子不會打架</span>'
        'micro:bit 會<b>同時記住</b>兩個規則，你按哪一顆，它就做哪一件事。你可以做好多好多頂帽子！</div>'

        '<h2>4. 隱藏魔法：A＋B 一起按 🤝</h2>'
        '<p>把按鈕名字的<b>小三角形</b>點開，還有一個 <code>A+B</code>——代表兩顆<b>一起</b>按！</p>'
        + prog(
            blk("event", "輸入", "當按鈕 ", slot("A+B", True), " 被按下", hat=True,
                nest_html=blk("basic", "基本", "顯示圖示 ", slot("❤️"))),
        )
        + leds(HEART, "A＋B 一起按 → 愛心") +

        '<div class="try"><h3>🎯 試試看（換你變魔法）</h3><ol>'
        '<li>按 <b>A</b> 顯示你的<b>名字</b>，按 <b>B</b> 顯示你最喜歡的<b>數字</b>。</li>'
        '<li>讓 <b>A＋B</b> 一起按時，顯示一顆愛心 ❤️。</li>'
        '<li>加一頂新帽子：在「輸入」找「<b>當搖動</b>」，搖一搖 micro:bit 就顯示閃電或箭頭！（下一關會學更多感覺魔法 🌡️）</li>'
        '</ol></div>'

        '<h2>✅ 我學會了</h2><p>點一下把學會的打勾：</p>'
        + checklist("l3", [
            "我知道「事件」就是「當…的時候就做…」",
            "我用「當按鈕 A／B 被按下」讓兩顆按鈕做不同的事",
            "我試過 A＋B 一起按的隱藏魔法",
        ]) +
        nav_for("l3")
    )
    open(os.path.join(REPO, "l3.html"), "w").write(page("l3", body, "第 3 課：按鈕魔法", ' data-lesson="l3"'))

# ================= 第 4 課 =================
def build_l4():
    body = (
        '<div class="crumb"><a href="index.html">課程地圖</a> / 第 4 課</div>'
        '<span class="eyebrow">第 4 課</span>' + done_badge() +
        '<h1>🔢 神奇計數器</h1>'
        '<div class="goal"><div class="big">🔢</div><div><h3>這一課要做到</h3>'
        '<p>做一個<b>計數器</b>：每按一下 A 就<b>加 1</b>，數字顯示在螢幕上——數跳繩、數敲門都行！</p></div></div>'

        '<h2>1. 變數是什麼？</h2>'
        '<p>變數就像一個<b>小盒子</b>📦，裡面裝一個數字。你可以<b>看</b>盒子裡是多少，也可以<b>換掉</b>裡面的數字。'
        '我們要用一個盒子，把「按了幾下」記住。</p>'
        '<div class="scratch"><span class="hd">🐱 跟 Scratch 比一比</span>'
        'Scratch 玩遊戲會用「<b>分數</b>」變數，答對就「<b>分數改變 1</b>」；micro:bit 一模一樣——'
        '一樣在<b>「變數」</b>抽屜，一樣可以「設定」和「改變」。</div>'

        '<h2>2. 做一個盒子（建立變數）📦</h2>'
        '<p>在左邊<b>橘色「變數」</b>抽屜，按<b>「建立一個變數」</b>，取名叫 <code>count</code>（計數的意思）。'
        '然後一開機先把盒子<b>歸零</b>：</p>'
        + prog(
            blk("basic", "基本", slot("當程式開始"), hat=True,
                nest_html=blk("var", "變數", "設定 ", slot("count"), " 為 ", slot("0"))),
        ) +
        '<div class="note"><span class="hd">💡 「設定」= 把盒子換成這個數字</span>'
        '「設定 count 為 0」就是把盒子裡的數字<b>直接換成 0</b>，不管本來是多少。</div>'

        '<h2>3. 按一下，加一個 ➕</h2>'
        '<p>按 A 的時候，讓盒子<b>改變 1</b>（就是加 1），再把盒子裡的數字<b>顯示</b>出來：</p>'
        + prog(
            blk("event", "輸入", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                nest_html=blk("var", "變數", slot("count"), " 改變 ", slot("1")) +
                          blk("basic", "基本", "顯示數字 ", slot("count"))),
        ) +
        '<p>按一下 → 1，再按 → 2，再按 → 3⋯⋯盒子會一直<b>記住</b>！</p>'
        + leds(THREE, "按了 3 下 → 顯示 3") +
        '<div class="note"><span class="hd">✨ 「改變 1」和「設定」不一樣</span>'
        '「<b>改變 1</b>」是在<b>原本的數字上再加 1</b>（3 變 4）；「設定」是<b>整個換掉</b>。這是最重要的分別喔！</div>'

        '<h2>4. 按 B 重來（歸零）🔄</h2>'
        '<p>數字太大想重數？讓 B 把盒子<b>設定回 0</b>：</p>'
        + prog(
            blk("event", "輸入", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                nest_html=blk("var", "變數", "設定 ", slot("count"), " 為 ", slot("0")) +
                          blk("basic", "基本", "顯示數字 ", slot("count"))),
        ) +

        '<div class="try"><h3>🎯 試試看（換你設計）</h3><ol>'
        '<li>把「改變 1」改成「<b>改變 2</b>」，看看每按一下跳多少。</li>'
        '<li>做一個<b>比分板</b>：A 加 1 分、B <b>減 1 分</b>（改變 <code>-1</code>）。</li>'
        '<li>挑戰：按 A＋B 一起時，顯示一顆愛心說「你好棒」❤️。</li>'
        '</ol></div>'

        '<h2>✅ 我學會了</h2><p>點一下把學會的打勾：</p>'
        + checklist("l4", [
            "我知道變數是一個會記住數字的小盒子",
            "我會用「建立變數」做一個 count，並在開機時設定為 0",
            "我分得出「改變 1（加上去）」和「設定（換掉）」不一樣",
        ]) +
        nav_for("l4")
    )
    open(os.path.join(REPO, "l4.html"), "w").write(page("l4", body, "第 4 課：神奇計數器", ' data-lesson="l4"'))

def main():
    build_index(); build_l1(); build_l2(); build_l3(); build_l4()
    opened = [L['id'] for L in LESSONS if L['status']=='open']
    print("已生成：index.html, " + ", ".join(f"{i}.html" for i in opened))
    print(f"開放課程：{opened}")

if __name__ == "__main__":
    main()
