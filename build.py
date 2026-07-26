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
    dict(id="l3", em="🅰️", short="按鈕魔法", title="按鈕魔法", sub="按 A、按 B 做不同的事", status="soon"),
    dict(id="l4", em="🔢", short="神奇計數器", title="神奇計數器", sub="學會「變數」，按一下加一", status="soon"),
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
DUCK  = ".##..\n####.\n.####\n.###.\n....."
ARROW = "..#..\n.###.\n#.#.#\n..#..\n..#.."

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
        nav(prev=("index", "回地圖"), next=("l2", "第 2 課：LED 畫畫板"))
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
        nav(prev=("l1", "第 1 課"), next=None)
    )
    open(os.path.join(REPO, "l2.html"), "w").write(page("l2", body, "第 2 課：LED 畫畫板", ' data-lesson="l2"'))

def main():
    build_index(); build_l1(); build_l2()
    print("已生成：index.html, l1.html, l2.html")
    print(f"開放課程：{[L['id'] for L in LESSONS if L['status']=='open']}")

if __name__ == "__main__":
    main()
