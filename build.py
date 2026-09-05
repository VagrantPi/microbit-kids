#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從單一課程大綱生成整個 micro:bit 教材網站。新增/修改課程只要改這裡再重跑。

積木文字全部對齊 makecode.microbit.org 繁體中文版的實際畫面（實測 v9.0.12）。
要改積木文字前，請先去真的編輯器確認一次，不要憑印象寫。
"""
import os, html
REPO = os.path.dirname(os.path.abspath(__file__))

# ===== 課程大綱（單一來源，側邊欄與首頁都從這裡長出來）=====
LESSONS = [
    dict(id="l0", em="🔌", short="送進板子", title="準備篇：把程式送進 micro:bit",
         sub="開專案、按下載、傳到真的板子", status="open"),
    dict(id="l1", em="🔤", short="認識 micro:bit", title="認識 micro:bit ＆ 我的第一支程式",
         sub="顯示圖案、文字和數字", status="open"),
    dict(id="l2", em="🎨", short="LED 畫畫板", title="LED 畫畫板",
         sub="用 25 顆燈畫圖、做動畫", status="open"),
    dict(id="l3", em="🅰️", short="按鈕魔法", title="按鈕魔法", sub="按 A、按 B 做不同的事", status="open"),
    dict(id="l4", em="🔢", short="神奇計數器", title="神奇計數器", sub="學會「變數」，按一下加一", status="open"),
    dict(id="l5", em="🔁", short="重複的力量", title="重複的力量", sub="用重複做閃爍和數數", status="open"),
    dict(id="l6", em="🎲", short="搖一搖骰子", title="搖一搖骰子", sub="抽籤加判斷，做電子骰子", status="open"),
    dict(id="l7", em="🦸", short="超能力", title="micro:bit 的超能力", sub="冷熱、亮暗、歪一邊都知道", status="open"),
    dict(id="l8", em="🎵", short="音樂盒", title="音樂盒", sub="按按鈕就發出聲音，做一台小鋼琴", status="open"),
    dict(id="l9", em="🏆", short="電子寵物", title="電子寵物大挑戰", sub="把學會的通通用上！", status="open"),
    dict(id="l10", em="📡", short="廣播雙人", title="廣播雙人連線", sub="兩台 micro:bit 隔空聊天", status="open"),
    dict(id="l11", em="🎮", short="LED 小遊戲", title="LED 小遊戲：燈光快停", sub="做一個反應遊戲", status="open"),
    dict(id="l12", em="🍌", short="香蕉鋼琴", title="觸摸香蕉鋼琴", sub="碰水果就發出聲音", status="open"),
]

# ===== 抽屜：名稱 ＋ 講給小孩聽的顏色（色碼在 style.css 的 --c-*）=====
# 這裡的名字就是 MakeCode 繁中畫面上的字，不要自己改。
DRAWER = {
    "basic": ("基本", "藍色"),
    "event": ("輸入", "紫紅色"),
    "music": ("音效", "紅色"),
    "led":   ("LED", "深紫色"),
    "radio": ("廣播", "粉紅色"),
    "loop":  ("迴圈", "綠色"),
    "logic": ("邏輯", "藍綠色"),
    "var":   ("變數", "深紅色"),   # 跟音效的紅色很像，find() 之外還要靠色點和位置分辨
    "math":  ("數學", "紫色"),
    "pin":   ("引腳", "磚紅色"),
}

# ===== 小工具 =====
def esc(s): return html.escape(str(s))

def head(title):
    return ('<!doctype html><html lang="zh-Hant"><head>\n'
            '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)}</title>\n<link rel="stylesheet" href="style.css">\n'
            '<script>try{if(localStorage.getItem("mb_theme")==="dark")document.documentElement.setAttribute("data-theme","dark");'
            'if(localStorage.getItem("mb_side")==="collapsed")document.documentElement.classList.add("side-collapsed")}catch(e){}</script>\n'
            '</head>')

def topbar(focus_btn=False, side_btn=False):
    """課程頁多一顆專注模式開關；首頁沒有步驟卡也沒有側邊欄，兩顆都不放。
    （首頁放 ☰ 會按了沒反應，卻把收合狀態寫進 localStorage，害其他頁的課程地圖消失。）"""
    fb = ('<button class="iconbtn" id="focusBtn" title="專注模式" aria-label="切換專注模式">🎯</button>'
          if focus_btn else '')
    sbtn = ('<button class="iconbtn" id="sideBtn" title="收合選單" aria-label="收合選單">☰</button>'
            if side_btn else '')
    return ('<header class="bar"><div class="in">'
            + sbtn +
            '<a class="brand" href="index.html" style="text-decoration:none"><span class="chip">micro:bit</span><span class="wm"> 積木冒險</span></a>'
            '<span class="spacer"></span>'
            + fb +
            '<button class="iconbtn" id="themeBtn" title="換個顏色" aria-label="切換深淺色">🌙</button>'
            '</div></header>')

def lesson_no(L):
    """準備篇不編號，其餘從 1 開始。"""
    return "準備篇" if L["id"] == "l0" else f"第 {LESSONS.index(L)} 課"

def sidebar(cur):
    rows = ['<nav class="outline"><div class="cap">🗺️ 課程地圖</div>']
    # 圖鑑和遊戲區都不是「課」，所以不放進 LESSONS（免得課程編號跟著跑掉），單獨釘在最上面。
    cb = " cur" if cur == "blocks" else ""
    rows.append(f'<a class="lrow tool{cb}" href="blocks.html"><span class="em">🔍</span>'
                f'<span>積木圖鑑</span></a>')
    # 在任何一個遊戲頁裡，都高亮「101 遊戲區」這一列
    cg = " cur" if cur == "101" or cur in [g["id"] for g in GAMES] else ""
    rows.append(f'<a class="lrow tool last{cg}" href="101.html"><span class="em">🎮</span>'
                f'<span>101 遊戲區</span></a>')
    for i, L in enumerate(LESSONS):
        pre = "準備 ·" if L["id"] == "l0" else f"{i}."
        if L["status"] == "open":
            c = " cur" if L["id"] == cur else ""
            rows.append(f'<a class="lrow{c}" href="{L["id"]}.html"><span class="em">{L["em"]}</span>'
                        f'<span>{pre} {esc(L["short"])}</span></a>')
        else:
            rows.append(f'<span class="lrow soon"><span class="em">{L["em"]}</span>'
                        f'<span>{pre} {esc(L["short"])}</span><span class="lock">🔒</span></span>')
    rows.append('</nav>')
    return '<aside class="side">' + ''.join(rows) + '</aside>'

def page(cur, body, title, lesson_attr=""):
    return (head(title) + f'<body{lesson_attr}>' + topbar(focus_btn=True, side_btn=True) +
            '<div class="wrap"><div class="layout">' + sidebar(cur) +
            '<main class="content">' + body + '</main></div></div>\n<script src="app.js"></script></body></html>\n')

# ---- 積木產生器 ----
def blk(cat, *chunks, hat=False, nest_html=""):
    """畫一塊積木。抽屜標籤自動從 DRAWER 取，避免抽屜名寫錯。"""
    cls = f"block b-{cat}" + (" hat" if hat else "")
    inner = f'<span class="tag">{esc(DRAWER[cat][0])}</span>' + "".join(chunks)
    out = f'<div class="{cls}">{inner}</div>'
    if nest_html:
        out += f'<div class="nest">{nest_html}</div>'
    return out

def slot(t, round=False): return f'<span class="slot{" round" if round else ""}">{esc(t)}</span>'
def prog(*items): return '<div class="prog">' + "".join(items) + '</div>'

def ifelse(cond_html, then_html, else_html=None):
    """「如果…那麼…否則」在 MakeCode 是【同一塊】積木，不是兩塊。"""
    out = '<div class="ifwrap">'
    out += f'<div class="block b-logic"><span class="tag">{DRAWER["logic"][0]}</span>如果 {cond_html} 那麼</div>'
    out += f'<div class="nest">{then_html}</div>'
    if else_html:
        out += f'<div class="block b-logic">否則</div><div class="nest">{else_html}</div>'
    out += '<div class="ifend"></div></div>'
    return out

# ---- 教學版面元件 ----
def dot(cat): return f'<span class="dot b-{cat}"></span>'

def find(cat, block_name, note=""):
    """『去哪找』：色點 ＋ 抽屜名 ＋ 顏色 ＋ 積木名。"""
    name, color = DRAWER[cat]
    extra = f' <span class="fnote">{note}</span>' if note else ''
    return (f'<div class="find">{dot(cat)}去 <b>{esc(name)}</b> 抽屜（{esc(color)}的），'
            f'找 <b class="bname">{esc(block_name)}</b>{extra}</div>')

def look(text): return f'<div class="look"><b>👀 看一下</b>{text}</div>'

def step(n, title, *chunks):
    return (f'<section class="step" data-k="s{n}">'
            f'<div class="hd"><span class="n">{n}</span><span class="t">{esc(title)}</span>'
            '<span class="sbox"></span></div>'
            '<div class="sbody">' + "".join(chunks) + '</div></section>')

def goal(emoji, text):
    return (f'<div class="goal"><div class="big">{emoji}</div><div>'
            f'<h3>今天只做一件事 🎯</h3><p>{text}</p></div></div>')

def tryit(*items):
    lis = "".join(f'<li>{i}</li>' for i in items)
    return f'<div class="try"><h3>🎮 換你玩</h3><ol>{lis}</ol></div>'

def tip(hd, text): return f'<div class="tip"><span class="hd">{hd}</span>{text}</div>'
def note(hd, text): return f'<div class="note"><span class="hd">{hd}</span>{text}</div>'

def optional(hd, text):
    """給孩子的選讀。想知道就點開，不看也不影響做出東西——跟 adult() 的對象不同。"""
    return (f'<details class="optional"><summary>{hd}</summary>'
            f'<div>{text}</div></details>')

def adult(text):
    """給大人的補充，預設收起來。孩子看的主文只留一句話，細節放這裡。"""
    return f'<details class="adult"><summary>👩‍🏫 給大人</summary><div>{text}</div></details>'

def playtone(note_name="中音 C", beat="1 拍"):
    """MakeCode 目前這塊積木是【英文未翻譯】：play tone (中音 C) for (1 拍) until done。
    實測 makecode.microbit.org zh-TW v9.0.12。教材一定要照螢幕畫，不要寫成「演奏音階」，
    那是旁邊另一塊 ringTone（聲音不會停）。"""
    # 「中音 C」「1 拍」「until done」在螢幕上都是白色圓角的下拉選單，所以三個都用 slot。
    return blk("music", "play tone ", slot(note_name), " for ", slot(beat), " ", slot("until done"))

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
EMPTY = ".....\n.....\n.....\n.....\n....."
# 入門遊戲用的圖案（猜拳機／反應王）
ROCK  = ".....\n.###.\n.###.\n.###.\n....."
SCISS = "#...#\n.#.#.\n..#..\n.#.#.\n#...#"
PAPER = "#####\n#####\n#####\n#####\n#####"
LEFT  = "##...\n##...\n##...\n##...\n##..."
RIGHT = "...##\n...##\n...##\n...##\n...##"
STAR  = "..#..\n#####\n.###.\n.#.#.\n#...#"
DICE6 = "#...#\n.....\n#...#\n.....\n#...#"
ARROW_L = "..#..\n.#...\n#####\n.#...\n..#.."
ARROW_R = "..#..\n...#.\n#####\n...#.\n..#.."
NOTE  = "...##\n...#.\n...#.\n##.#.\n##..."
CENTER = ".....\n.....\n..#..\n.....\n....."

def final(lesson_id, items):
    out = ['<h2>✅ 我學會了</h2><p>都做到了就點一下，蓋完成章 🎉</p><ul class="check final">']
    for k, t in enumerate(items):
        out.append(f'<li data-k="c{k}"><span class="box"></span><span>{esc(t)}</span></li>')
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
    prev = ("index", "回地圖") if i == 0 else (opened[i-1]["id"], lesson_no(opened[i-1]))
    nxt = None if i == len(opened)-1 else (opened[i+1]["id"], f"{lesson_no(opened[i+1])}：{opened[i+1]['short']}")
    return nav(prev, nxt)

def done_badge():
    return ('<span id="doneBadge" class="eyebrow" style="display:none;background:var(--go);margin-left:8px">🎉 這一課完成！</span>')

def top(lid, label, title):
    L = [x for x in LESSONS if x["id"] == lid][0]
    return (f'<div class="crumb"><a href="index.html">課程地圖</a> / {lesson_no(L)}</div>'
            f'<span class="eyebrow">{label}</span>' + done_badge() + f'<h1>{title}</h1>')

def write(lid, body, title):
    open(os.path.join(REPO, f"{lid}.html"), "w").write(page(lid, body, title, f' data-lesson="{lid}"'))

# ================= 積木圖鑑的資料表 =================
# 九個抽屜的常用積木，全部實測自 makecode.microbit.org zh-TW（編輯器 v9.0.12）。
# parts 的寫法：純字串＝積木上的文字，("s",x)＝白色方框，("r",x)＝圓角下拉，
#              ("n",cat,[...])＝積木裡面還卡著一塊小積木。
# 積木上的字一律照螢幕，desc（一句話）才用孩子聽得懂的講法。
# id 是給遊戲頁宣告「我用到哪幾塊」用的，改動要同步 GAMES 的 uses（build 時會檢查）。
def B(bid, cat, parts, desc, hat=False):
    return dict(id=bid, cat=cat, parts=parts, desc=desc, hat=hat)

def render_parts(parts):
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append(esc(p))
        elif p[0] == "s":
            out.append(slot(p[1]))
        elif p[0] == "r":
            out.append(slot(p[1], True))
        elif p[0] == "n":
            # 巢狀的小積木不掛抽屜標籤——它是 shadow，不是從那個抽屜拖出來的
            out.append(f'<div class="block b-{p[1]}">' + "".join(render_parts(p[2])) + '</div>')
    return out

def render_block(b):
    return blk(b["cat"], *render_parts(b["parts"]), hat=b["hat"])

BLOCKS = [
    # ---- 基本（藍色）----
    B("basic.showNumber", "basic", ["顯示數字 ", ("s", "0")], "在螢幕上寫一個數字"),
    B("basic.showLeds", "basic", ["顯示指示燈 ", ("s", "5×5 格子")], "點格子，自己畫一張圖"),
    B("basic.showIcon", "basic", ["顯示圖示 ", ("s", "❤️")], "從現成的小圖裡挑一張"),
    B("basic.showString", "basic", ["顯示文字 ", ("s", "Hello!")], "讓字一個一個滑過去"),
    B("basic.clearScreen", "basic", ["清空畫面"], "把 25 顆燈全部關掉"),
    B("basic.forever", "basic", ["重複無限次"], "裡面的事一直做，不會停", hat=True),
    B("basic.onStart", "basic", [("s", "當啟動時")], "一開機就做裡面的事，只做一次", hat=True),
    B("basic.pause", "basic", ["暫停 ", ("s", "100"), " 毫秒"], "停一下下再做下一件（500 就是半秒）"),
    B("basic.showArrow", "basic", ["顯示箭頭 ", ("n", "math", ["箭頭數字 ", ("r", "北")])], "秀出一個指方向的箭頭"),
    # ---- 輸入（紫紅色）----
    B("event.onButton", "event", ["當按鈕 ", ("r", "A"), " 被按下"], "你按 A，它才做裡面的事", hat=True),
    B("event.onGesture", "event", ["當姿勢 ", ("r", "晃動"), " 發生"], "你搖它、翻它、歪一邊，它就做", hat=True),
    B("event.onPin", "event", ["當引腳 ", ("r", "P0"), " 被按下"], "手碰到金色的孔就做", hat=True),
    B("event.buttonIsPressed", "event", ["按鈕 ", ("r", "A"), " 被按下？"], "回答「現在有沒有在按」"),
    B("event.pinIsPressed", "event", ["引腳 ", ("r", "P0"), " 被按下？"], "回答「金色的孔現在有沒有被碰」"),
    B("event.lightLevel", "event", ["光線感測值"], "它感覺到的亮度（0 全黑、255 很亮）"),
    B("event.temperature", "event", ["溫度感測值 (°C)"], "它感覺到的溫度"),
    # ---- 音效（紅色）----
    B("music.playTone", "music", ["play tone ", ("s", "中音 C"), " for ", ("s", "1 拍"), " ", ("s", "until done")],
      "彈一個音，彈完會自己停。上面是英文，找最長的那塊"),
    B("music.ringTone", "music", ["演奏 音階 ", ("s", "中音 C")], "也是彈一個音，但它不會自己停"),
    B("music.rest", "music", ["rest for ", ("s", "1 拍")], "安靜一下下，不出聲"),
    B("music.stopAll", "music", ["停止播放所有音效"], "叫它閉嘴，馬上安靜"),
    # ---- LED（深紫色）----
    B("led.plot", "led", ["點亮 x ", ("s", "0"), " y ", ("s", "0")], "指定一顆燈亮起來"),
    B("led.unplot", "led", ["不點亮 x ", ("s", "0"), " y ", ("s", "0")], "指定一顆燈熄掉"),
    B("led.toggle", "led", ["點的狀態切換 x ", ("s", "0"), " y ", ("s", "0")], "亮的變暗、暗的變亮"),
    B("led.point", "led", ["點的狀態 x ", ("s", "0"), " y ", ("s", "0")], "回答「那顆燈現在亮不亮」"),
    B("led.brightness", "led", ["燈光 亮度設為 ", ("s", "255")], "整片燈調亮或調暗"),
    # ---- 廣播（粉紅色）----
    B("radio.setGroup", "radio", ["廣播群組設為 ", ("s", "1")], "跟朋友約好同一個暗號"),
    B("radio.sendNumber", "radio", ["廣播發送數字 ", ("s", "0")], "隔空喊一個數字出去"),
    B("radio.sendString", "radio", ["廣播發送文字 ", ("s", " ")], "隔空喊一句話出去"),
    B("radio.onNumber", "radio", ["當收到廣播數字 ", ("r", "receivedNumber")], "聽到別人喊數字就做", hat=True),
    B("radio.onString", "radio", ["當收到廣播文字 ", ("r", "receivedString")], "聽到別人喊話就做", hat=True),
    # ---- 迴圈（綠色）----
    B("loop.repeat", "loop", ["重複 ", ("s", "4"), " 次 執行"], "裡面的事做 4 遍就停"),
    B("loop.while", "loop", ["重複 判斷 ", ("s", "false"), " 執行"], "只要條件還成立，就一直做"),
    B("loop.forIndex", "loop", ["計次 ", ("r", "index"), " 從 0 到 ", ("s", "4"), " 執行"], "從 0 數到 4，一邊數一邊做"),
    # ---- 邏輯（藍綠色）----
    B("logic.if", "logic", ["如果 ", ("s", "　"), " 那麼"], "條件成立才做裡面的事"),
    B("logic.ifElse", "logic", ["如果 ", ("s", "　"), " 那麼 … 否則"], "岔路口：成立走上面，不成立走下面"),
    B("logic.eq", "logic", [("s", "0"), " = ", ("s", "0")], "問「這兩個一樣嗎」"),
    B("logic.lt", "logic", [("s", "0"), " < ", ("s", "0")], "問「左邊比右邊小嗎」"),
    B("logic.and", "logic", [("s", "　"), " 且 ", ("s", "　")], "兩邊都成立，才算成立"),
    B("logic.or", "logic", [("s", "　"), " 或 ", ("s", "　")], "只要一邊成立，就算成立"),
    B("logic.true", "logic", ["true"], "「對」。旁邊還有一塊 false，是「不對」"),
    # ---- 變數（深紅色）----
    B("var.set", "var", ["變數 ", ("s", "x"), " 設為 ", ("s", "0")], "把盒子裡的東西整個換掉"),
    B("var.change", "var", ["變數 ", ("s", "x"), " 改變 ", ("s", "1")], "在原本的數字上再加"),
    B("var.get", "var", [("s", "x")], "圓圓的那塊，就是盒子裡現在裝的數字"),
    # ---- 數學（紫色）----
    B("math.add", "math", [("s", "0"), " + ", ("s", "0")], "加起來"),
    B("math.sub", "math", [("s", "0"), " - ", ("s", "0")], "減掉"),
    B("math.mul", "math", [("s", "0"), " × ", ("s", "0")], "乘起來"),
    B("math.div", "math", [("s", "0"), " / ", ("s", "0")], "除以"),
    B("math.random", "math", ["隨機取數 ", ("s", "0"), " 到 ", ("s", "10")], "抽籤，每次給不一樣的數字"),
]

DEX_CATS = ["basic", "event", "music", "led", "radio", "loop", "logic", "var", "math"]

# ================= 積木圖鑑（blocks.html）=================
def build_blocks():
    total = len(BLOCKS)

    tabs, panels = [], []
    for ci, c in enumerate(DEX_CATS):
        name, color = DRAWER[c]
        items = [(i, b) for i, b in enumerate(BLOCKS) if b["cat"] == c]
        cur = " cur" if ci == 0 else ""
        tabs.append(f'<button class="dextab{cur}" data-cat="{c}">{dot(c)}'
                    f'<span>{esc(name)}</span><span class="cnt">{len(items)}</span></button>')
        cards = []
        for i, b in items:
            cards.append(
                f'<div class="dexcard" data-i="{i}" data-cat="{c}">'
                f'<span class="box"></span>'
                f'<div class="bwrap">{render_block(b)}</div>'
                f'<p class="d">{esc(b["desc"])}</p>'
                f'<span class="medal">🏅</span></div>')
        panels.append(f'<div class="dexpanel{cur}" data-cat="{c}">' + "".join(cards) + '</div>')

    opts = "".join(
        f'<button class="qopt" data-cat="{c}">{dot(c)}<span>{esc(DRAWER[c][0])}</span></button>'
        for c in DEX_CATS)

    body = (
        '<div class="crumb"><a href="index.html">課程地圖</a> / 積木圖鑑</div>'
        '<span class="eyebrow">認識積木</span>'
        '<span id="dexBadge" class="eyebrow" style="display:none;background:var(--go);margin-left:8px">'
        '🎉 全部收集完成！</span>'
        '<h1>🔍 積木圖鑑</h1>'

        + goal("🗂️", f"把 <b>{total} 塊</b>積木看熟，以後上課<b>不用一直找</b>。")

        + '<p>micro:bit 的積木放在<b>九個抽屜</b>裡。</p>'
        '<p>每個抽屜有自己的<b>顏色</b>。顏色記起來，就找得很快 🎨</p>'

        + '<div class="bar101"><div class="fill" id="p101fill"></div>'
        '<span class="txt">收集了 <b id="p101">0</b> / ' + str(total) + ' 塊</span></div>'

        + '<div class="modes">'
        '<button class="mode cur" id="modeDex">📖 翻圖鑑</button>'
        '<button class="mode" id="modeQuiz">🎯 來考考我</button>'
        '</div>'

        # ---- 圖鑑 ----
        + '<section class="dex" id="dex">'
        + '<div class="dextabs">' + "".join(tabs) + '</div>'
        + note("👆 怎麼玩", "點一下卡片，就表示「這塊我看過了」✅<br>"
                           "九個抽屜都翻一翻，再去玩「來考考我」。")
        + "".join(panels)
        + '</section>'

        # ---- 測驗 ----
        + '<section class="quiz" id="quiz" hidden>'
        '<div class="qhead">這塊積木在<b>哪一個抽屜</b>？</div>'
        '<div class="qblock" id="qblock"></div>'
        '<div class="quizopts">' + opts + '</div>'
        '<div class="qmsg" id="qmsg"></div>'
        '<button class="btn g" id="qnext" style="display:none">下一題 →</button>'
        '</section>'

        + '<div class="nav"><a class="btn ghost" href="index.html">← 回地圖</a>'
        '<span class="sp"></span>'
        '<a class="btn g" href="l0.html">準備篇：送進板子 →</a></div>'
    )
    open(os.path.join(REPO, "blocks.html"), "w").write(
        page("blocks", body, "積木圖鑑：認識所有積木", ' data-lesson="blocks"'))

# ================= 首頁 =================
def build_index():
    cards = ['<div class="grid">']
    for L in LESSONS:
        no = lesson_no(L)
        if L["status"] == "open":
            cards.append(f'<a class="lesson" href="{L["id"]}.html" data-lesson="{L["id"]}">'
                         f'<span class="no">{no}</span><span class="em">{L["em"]}</span>'
                         f'<h3>{esc(L["short"])}</h3><p>{esc(L["sub"])}</p></a>')
        else:
            cards.append(f'<div class="lesson soon"><span class="no">{no}</span>'
                         f'<span class="em">{L["em"]}</span><h3>{esc(L["short"])}</h3><p>{esc(L["sub"])}</p></div>')
    cards.append('</div>')
    body = (
        '<div class="hero"><div class="mb">🤖</div>'
        '<h1>micro:bit 積木冒險</h1>'
        '<p class="lead">micro:bit 是一塊<b>真的小電腦</b>，只有餅乾那麼大。<br>'
        '它會<b>亮燈</b>、會<b>唱歌</b>，還<b>感覺得到你在搖它</b>。<br>'
        '你只要<b>拖積木</b>，就能叫它做事。一起來玩！</p>'
        '<div class="pill"><span>🧩 拖積木就會</span><span>💡 馬上看到燈亮</span>'
        '<span>👣 一次只做一小步</span><span>🎉 每一步都能打勾</span></div>'
        '</div>'
        + leds(HEART, "它會這樣跟你打招呼") + leds(SMILE, "還會對你微笑") +
        '<h2>怎麼玩這份教材 🗺️</h2>'
        '<div class="note"><span class="hd">一次只做一步，做完就打勾</span>'
        '每一課都切成<b>幾個小步驟</b>。每一步都會告訴你：<br>'
        '① 去<b>哪個抽屜</b>找積木（有顏色小圓點幫你認）<br>'
        '② 拼完<b>長什麼樣子</b><br>'
        '③ 螢幕上<b>應該看到什麼</b>——看到了才往下走 👀</div>'
        '<h2>認識積木 ＆ 做遊戲 🎒</h2>'
        '<a class="bigcard" href="blocks.html"><span class="em">🔍</span>'
        '<span class="tx"><b>積木圖鑑</b>'
        f'<span>把 {len(BLOCKS)} 塊積木看熟，上課就不用一直找。<br>'
        '翻完再玩「這塊在哪個抽屜？」小測驗 🎯</span></span>'
        '<span class="go">開始 →</span></a>'
        '<a class="bigcard game" href="101.html"><span class="em">🎮</span>'
        '<span class="tx"><b>101 遊戲區</b>'
        f'<span>用積木做出 {len(GAMES)} 個<b>真的能玩</b>的小遊戲。<br>'
        f'前兩個<b>不用變數也不用座標</b>，做得完 👍 合計用到 {len(covered_ids())} / {len(BLOCKS)} 塊積木 🧱</span></span>'
        '<span class="go">開始 →</span></a>'
        '<h2>開始冒險 🚀</h2>'
        '<p class="lead" style="margin-top:0">從<b>準備篇</b>開始，一關一關闖。</p>'
        + "".join(cards) +
        '<footer>micro:bit 積木冒險 · 為小小創客打造 · 用 MakeCode 積木從零開始</footer>'
    )
    open(os.path.join(REPO, "index.html"), "w").write(
        head("micro:bit 積木冒險 · 給小朋友的第一堂程式課") + "<body>" + topbar() +
        '<div class="wrap">' + body + '</div>\n<script src="app.js"></script></body></html>\n')

# ================= 準備篇 =================
def build_l0():
    body = (
        top("l0", "準備篇", "🔌 把程式送進 micro:bit") +
        goal("❤️", "讓<b>真的</b> micro:bit 亮出一顆愛心。") +

        step(1, "打開 MakeCode 網站",
             '<p>打開瀏覽器，網址打 <code>makecode.microbit.org</code>。</p>'
             + look("看到一個有很多彩色積木的網站。")) +

        step(2, "開一個新專案",
             '<p>按左上角的 <b>「新增專案」</b>。</p>'
             '<p>會跳出一個小視窗問名字，隨便打（例如 <code>hello</code>）。</p>'
             '<p>再按 <b>「創建」</b>。</p>'
             + look('中間出現兩塊積木：<b>「當啟動時」</b>和<b>「重複無限次」</b>。<br>'
                    '右邊有一台 micro:bit 的圖 🖥️ 那是<b>電腦裡的假 micro:bit</b>，'
                    '後面都叫它<b>「假的那台」</b>。')
             + adult("「假的那台」就是模擬器。手邊沒有實體板子也能上完整套教材，"
                     "只有第 12 課（香蕉鋼琴）需要真板子和鱷魚夾。")) +

        step(3, "找出「顯示圖示」這塊積木",
             find("basic", "顯示圖示")
             + '<p>先<b>不要</b>拖，找到它就好。</p>'
             + look("在藍色的<b>基本</b>抽屜裡看到它了嗎？看到就打勾 ✅")) +

        step(4, "把它拖進「當啟動時」裡面",
             '<p>用滑鼠<b>拖</b>到「當啟動時」的<b>凹槽裡面</b>。</p>'
             '<p>會「喀」一聲卡住。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("❤️"))))
             + look("積木卡進去了，跟上面那張圖一樣。")
             + adult("拖放對小手不容易。訣竅：<b>不要放太準</b>——只要拖到凹槽<b>附近</b>，"
                     "出現一條灰色的影子線就可以放手，它會自己吸過去。<br>"
                     "拼錯了想丟掉：把積木拖到右下角的<b>垃圾桶</b>，或按鍵盤 Delete。")) +

        step(5, "點圖案，選一顆愛心",
             '<p>積木上那個圖案是<b>選單</b>。點它一下。</p>'
             '<p>會跳出好多小圖，選<b>愛心</b>。</p>'
             + look("假的那台亮出一顆愛心 ❤️")
             + leds(HEART, "假的那台會長這樣")) +

        step(6, "把真的 micro:bit 接上電腦",
             '<p>拿 USB 線，一頭插 micro:bit，一頭插電腦。</p>'
             + look("電腦上會多出一個隨身碟，名字叫 <code>MICROBIT</code>。")) +

        step(7, "按「下載」，程式就飛過去了",
             '<p>按畫面<b>左下角</b>那顆大大的 <b>「下載」</b>。</p>'
             + note("會發生兩種情況之一",
                    "🅰️ 跳出視窗問你要連哪一台 → 選 <b>micro:bit</b>，按<b>連線</b>。<br>"
                    "🅱️ 直接下載一個檔案 → 把那個檔案<b>拖進</b> <code>MICROBIT</code> 那個隨身碟。")
             + look("板子<b>背面</b>有一顆黃燈會一直閃。<b>閃完</b>，正面就亮出愛心了 🎉")
             + adult("情況 🅰️ 只有 Chrome／Edge 才有（WebUSB），第一次要手動配對一次，"
                     "之後就記住了。Safari 只會走 🅱️。<br>"
                     "黃燈閃完前不要拔線。")) +

        tryit("把愛心換成<b>笑臉</b>，再按一次「下載」。",
              "拔掉 USB 線，接<b>電池盒</b>——沒接電腦它也會亮！") +

        note("💡 記住這一招",
             "以後<b>每一課</b>做完，都是按<b>「下載」</b>把程式送進板子。<br>"
             "如果懶得接線，只看<b>假的那台</b>也可以玩。") +

        final("l0", [
            "我會開新專案（新增專案 → 創建）",
            "我會把積木拖進「當啟動時」裡面",
            "我會按「下載」把程式送進真的 micro:bit",
        ]) + nav_for("l0")
    )
    write("l0", body, "準備篇：把程式送進 micro:bit")

# ================= 第 1 課 =================
def build_l1():
    body = (
        top("l1", "第 1 課", "🔤 認識 micro:bit ＆ 我的第一支程式") +
        goal("🔤", "讓 micro:bit 顯示<b>圖案</b>、<b>你的名字</b>，還有<b>數字</b>。") +

        '<h2>micro:bit 身上有什麼？</h2>'
        '<div class="note">'
        '💡 正面有 <b>25 顆紅色小燈</b>，排成 5 排、每排 5 顆。<br>'
        '🅰️🅱️ 兩顆按鈕，一顆叫 <b>A</b>、一顆叫 <b>B</b>。<br>'
        '🤸 它<b>感覺得到</b>你在搖它、天黑了、變熱了。<br>'
        '🔊 它還會<b>唱歌</b>。</div>'
        + leds(HEART, "25 顆燈排出愛心") +

        step(1, "先讓它亮一顆愛心",
             find("basic", "顯示圖示")
             + '<p>拖進「當啟動時」裡面，圖案選<b>愛心</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("❤️"))))
             + look("假的那台亮出愛心 ❤️")) +

        step(2, "換一個圖案玩玩",
             '<p>點積木上的<b>圖案</b>，選一個<b>笑臉</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("😀"))))
             + look("愛心變成笑臉 😀")
             + leds(SMILE, "笑臉")) +

        step(3, "拖一塊「顯示文字」下來",
             find("basic", "顯示文字", "（積木上本來寫 <code>Hello!</code>）")
             + '<p>拖到<b>「顯示圖示」的下面</b>，貼著它放。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("😀")) +
                                  blk("basic", "顯示文字 ", slot("Hello!"))))
             + look("先笑臉，再跑出 <code>Hello!</code> ➡️")) +

        step(4, "把它改成你的名字",
             '<p>點 <code>Hello!</code> 那一格，打上你的名字。</p>'
             + note("🔤 要用<b>英文字母</b>", "例如 <code>LILY</code>。中文字它顯示不出來。")
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("😀")) +
                                  blk("basic", "顯示文字 ", slot("LILY"))))
             + look("笑臉之後，名字一個字母一個字母<b>滑過去</b> ➡️")) +

        step(5, "最後加一個數字",
             find("basic", "顯示數字")
             + '<p>放在最下面，把 <code>0</code> 改成你的<b>年紀</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("😀")) +
                                  blk("basic", "顯示文字 ", slot("LILY")) +
                                  blk("basic", "顯示數字 ", slot("7"))))
             + look("笑臉 → 名字 → 數字，一個接一個出現。")
             + adult("這一課的觀念是<b>順序</b>：積木由上往下，一個做完才做下一個。<br>"
                     "「換你玩」的第一題就是在驗收這件事——換順序，出來的東西就換順序。"
                     "讓他先<b>猜</b>會變怎樣，再動手驗證。")) +

        tryit("把三塊積木的<b>順序換一換</b>，先<b>猜猜看</b>會變怎樣，再試。",
              "按<b>「下載」</b>，讓真的 micro:bit 也跟大家打招呼 👋") +

        final("l1", [
            "我知道 micro:bit 有 25 顆燈和 A、B 兩顆按鈕",
            "我會用「顯示圖示」換不同的圖案",
            "我讓它顯示了我的名字和數字",
        ]) + nav_for("l1")
    )
    write("l1", body, "第 1 課：認識 micro:bit")

# ================= 第 2 課 =================
def build_l2():
    body = (
        top("l2", "第 2 課", "🎨 LED 畫畫板") +
        goal("🎨", "把 25 顆燈當<b>畫布</b>，畫出自己的圖，再讓它<b>動起來</b>。") +

        '<p>25 顆燈就是你的畫紙。</p>'
        '<p>每一顆可以<b>亮</b>，也可以<b>不亮</b>。</p>'
        + leds(SMILE, "笑臉") + leds(DUCK, "小鴨") + leds(ARROW, "箭頭") +

        step(1, "拖出畫畫板",
             find("basic", "顯示指示燈", "（積木上有 5×5 的小格子）")
             + note("⚠️ 它在「基本」抽屜（藍色）",
                    "<b>不在</b> LED 抽屜裡，去 LED 抽屜找會找不到。")
             + '<p>把它拖進 <b>「當啟動時」</b> 裡面。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示指示燈 ", slot("5×5 格子"))))
             + look("假的那台整個黑黑的。還沒點格子，所以是對的 👍")) +

        step(2, "點格子，畫一個笑臉",
             '<p><b>點</b>一格 → 亮。<b>再點</b>一次 → 暗。</p>'
             '<p>照著下面這張，把該亮的點亮：</p>'
             + leds(SMILE, "照這樣點")
             + look("假的那台出現笑臉 😊")) +

        step(3, "找到綠色的「重複無限次」",
             '<p>它<b>一開始就在畫面上</b>了，不用去抽屜找。</p>'
             + prog(blk("loop", "重複無限次", hat=True))
             + tip("🔁 它會做什麼", "把積木放進去，它就會<b>一直做、不停下來</b>。")
             + look("找到那塊綠色的了嗎？找到就打勾 ✅")
             + adult("這一步不動手，只是先認位置。下一步要往裡面放東西，"
                     "先確認孩子指得出那塊綠色積木，再往下走。")) +

        step(4, "放第一張圖進去：笑臉",
             '<p>再拖<b>一塊</b>「顯示指示燈」，放進 <b>「重複無限次」</b> 裡面。</p>'
             '<p>點格子，畫<b>笑臉</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "顯示指示燈 ", slot("😊 笑臉"))))
             + look("笑臉一直亮著，沒有變化。對的 👍")) +

        step(5, "放第二張圖：哭臉",
             '<p>再拖<b>一塊</b>「顯示指示燈」，放在<b>笑臉的下面</b>。</p>'
             '<p>這次畫<b>哭臉</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "顯示指示燈 ", slot("😊 笑臉")) +
                                  blk("basic", "顯示指示燈 ", slot("😢 哭臉"))))
             + look("兩張圖換<b>超快</b>，糊成一團 😵 下一步修好它 👇")) +

        step(6, "在笑臉後面加一塊「暫停」",
             find("basic", "暫停 100 毫秒")
             + '<p>放在<b>笑臉的下面</b>，把 <code>100</code> 改成 <code>500</code>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "顯示指示燈 ", slot("😊 笑臉")) +
                                  blk("basic", "暫停 ", slot("500"), " 毫秒") +
                                  blk("basic", "顯示指示燈 ", slot("😢 哭臉"))))
             + tip("⏱️ 500 是多久", "<b>500 就是半秒</b>，眨一下眼睛那麼久。")
             + look("笑臉會<b>停一下</b>了，哭臉還是一閃就過。")) +

        step(7, "在哭臉後面也加一塊",
             '<p>再拖一塊「暫停」，放在<b>哭臉的下面</b>，也改成 <code>500</code>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "顯示指示燈 ", slot("😊 笑臉")) +
                                  blk("basic", "暫停 ", slot("500"), " 毫秒") +
                                  blk("basic", "顯示指示燈 ", slot("😢 哭臉")) +
                                  blk("basic", "暫停 ", slot("500"), " 毫秒")))
             + look("笑臉、哭臉、笑臉、哭臉⋯⋯換表情了 🎞️")
             + adult("積木上寫的是「毫秒」，1000 毫秒 = 1 秒。"
                     "孩子只要記住「500 是半秒」就夠了，不用背單位換算。<br>"
                     "動畫 = 圖片 + 停一下 + 換下一張。這是這一課真正的重點，"
                     "可以問他：「把停一下拿掉會怎樣？」讓他自己拔掉試試。")) +

        tryit("把 <code>500</code> 改成 <code>150</code>，看它變多快。",
              "畫一個<b>你自己想的圖案</b>（星星、貓咪都可以）。") +

        final("l2", [
            "我知道畫面是 5 排 × 5 個，每顆燈可以亮或不亮",
            "我會用「顯示指示燈」點格子畫圖",
            "我用「暫停」讓兩張圖輪流換，做出動畫",
        ]) + nav_for("l2")
    )
    write("l2", body, "第 2 課：LED 畫畫板")

# ================= 第 3 課 =================
def build_l3():
    body = (
        top("l3", "第 3 課", "🅰️ 按鈕魔法") +
        goal("🪄", "按 <b>A</b> 出現笑臉，按 <b>B</b> 出現哭臉。") +

        '<p>前面兩課的程式，一開機就自己跑。</p>'
        '<p>這一課不一樣：micro:bit 會<b>乖乖等你</b>，你<b>按下去</b>它才動。</p>'

        + step(1, "拿一頂「帽子」出來",
               find("event", "當按鈕 A 被按下")
               + '<p>拖到畫面<b>空白的地方</b>放著就好，<b>不用</b>放進「當啟動時」。</p>'
               + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True))
               + tip("🎩 為什麼叫帽子",
                     "它上面圓圓的、蓋在最上面，像一頂帽子。<b>帽子底下夾什麼，就做什麼。</b>")
               + look("畫面上多了一塊紫紅色的積木，裡面空空的。")) +

        step(2, "帽子底下放一個笑臉",
             find("basic", "顯示圖示")
             + '<p>拖進帽子裡面，圖案選<b>笑臉</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("😀"))))
             + look("在假的那台上，用滑鼠<b>點 A 按鈕</b> → 笑臉跳出來 😀")
             + leds(SMILE, "按 A")) +

        step(3, "再拖一頂帽子，改成 B",
             '<p>再拖一塊 <b>「當按鈕 A 被按下」</b> 出來。</p>'
             '<p>點積木上的 <b>A</b>，選單裡改成 <b>B</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True))
             + look("現在有<b>兩頂</b>帽子：一頂 A、一頂 B。")) +

        step(4, "B 的帽子裡放哭臉",
             '<p>拖一塊「顯示圖示」進去，圖案選<b>哭臉</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("😢"))))
             + look("點 A → 笑臉；點 B → 哭臉。")
             + leds(SAD, "按 B")
             + adult("兩頂帽子不會打架——micro:bit 同時記住兩個規則，按哪顆就做哪件事。<br>"
                     "這是「事件」的核心：程式不是從頭跑到尾，而是<b>等你觸發</b>。")) +

        step(5, "再拉一頂，改成 A+B",
             '<p>再拖一頂帽子，點按鈕的選單，選 <b>A+B</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A+B", True), " 被按下", hat=True))
             + look("第三頂帽子出現了。")) +

        step(6, "裡面放愛心",
             '<p>放一塊「顯示圖示」，選<b>愛心</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A+B", True), " 被按下", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("❤️"))))
             + look("<b>兩顆一起按</b> → 愛心 ❤️")
             + leds(HEART, "A＋B 一起按")) +

        tryit("讓按 <b>A</b> 顯示你的<b>名字</b>（用「顯示文字」）。",
              "按<b>「下載」</b>，用<b>真的</b>手指按板子上的 A 和 B 試試看 👆") +

        final("l3", [
            "我知道「帽子積木」就是「當…的時候，就做…」",
            "我做了 A 和 B 兩頂帽子，做不同的事",
            "我試過 A＋B 一起按",
        ]) + nav_for("l3")
    )
    write("l3", body, "第 3 課：按鈕魔法")

# ================= 第 4 課 =================
def build_l4():
    body = (
        top("l4", "第 4 課", "🔢 神奇計數器") +
        goal("🔢", "每按一下 A 就<b>加 1</b>，數字顯示在螢幕上。") +

        '<p>要記住「按了幾下」，需要一個<b>小盒子</b> 📦。</p>'
        '<p>盒子裡裝一個數字。</p>'
        '<p>可以<b>看</b>裡面是多少，也可以<b>換掉</b>它。</p>'
        + adult("程式裡這種盒子叫「變數」。孩子這一課只要抓住「盒子裝一個數字」的畫面就夠了，"
                "「變數」這個詞不用背，之後自然會接上。")

        + step(1, "打開變數抽屜",
               f'<div class="find">{dot("var")}去 <b>變數</b> 抽屜（深紅色的）</div>'
               + note("🔍 它在<b>很下面</b>",
                      "抽屜由上往下數：基本、輸入、音效、LED、廣播、迴圈、邏輯、"
                      "<b>變數</b>、數學。<br>"
                      "上面的<b>音效</b>也是紅色的，別點錯——變數在<b>倒數第二個</b>。")
               + '<p>最上面有一顆按鈕：<b>「建立一個變數…」</b>。</p>'
               + look("看到那顆按鈕了嗎？看到就打勾 ✅")) +

        step(2, "做一個盒子，名字叫 count",
             '<p>按下 <b>「建立一個變數…」</b>。</p>'
             '<p>打上 <code>count</code>，按<b>確定</b>。</p>'
             + look("抽屜裡多出<b>三塊</b>新積木，上面都有 <code>count</code>。")
             + adult("<code>count</code> 是英文「數數」。用英文是因為 MakeCode 的變數名不吃中文，"
                     "打不出來時可以改用 <code>n</code> 之類的短名字，不影響學習。")) +

        step(3, "開機先把盒子歸零",
             find("var", "變數 count 設為 0")
             + '<p>拖進 <b>「當啟動時」</b> 裡面。</p>'
             '<p>數字<b>不用改</b>，就留 <code>0</code>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 設為 ", slot("0"))))
             + tip("📦 「設為 0」是什麼", "把盒子裡的東西<b>整個換成</b> 0。")
             + look("畫面<b>沒有變化</b>。這一步是在做準備，是正常的 👍")) +

        step(4, "拉一頂 A 的帽子",
             '<p>去 <b>輸入</b> 抽屜，拿 <b>「當按鈕 A 被按下」</b>（第 3 課學過）。</p>'
             '<p>放在空白的地方。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True))
             + look("畫面上多了一頂空空的帽子。")) +

        step(5, "帽子裡放「加一個」",
             find("var", "變數 count 改變 1")
             + '<p>拖進帽子裡。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 改變 ", slot("1"))))
             + look("點 A <b>還是沒反應</b>。因為還沒叫它秀出來，下一步 👇")) +

        step(6, "放一塊「顯示數字」",
             find("basic", "顯示數字")
             + '<p>放在「改變 1」的<b>下面</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 改變 ", slot("1")) +
                                  blk("basic", "顯示數字 ", slot("0"))))
             + look("點 A → 一直出現 <b>0</b>。快好了，再一步 👇")) +

        step(7, "把圓圓的 count 拖進白框框",
             '<p>回 <b>變數</b> 抽屜，最下面有一塊<b>圓圓的</b> <b class="bname">count</b>。</p>'
             '<p>把它<b>拖進</b>「顯示數字」的白色框框裡。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 改變 ", slot("1")) +
                                  blk("basic", "顯示數字 ", slot("count"))))
             + look("點 A → <b>1</b>，再點 → <b>2</b>，再點 → <b>3</b>⋯⋯它記住了！")
             + leds(THREE, "點了 3 下")
             + adult("圓形積木要「塞進」白框框，這個拖放動作對小手是難的。"
                     "如果對不準，可以先把「顯示數字」拉到空白處放大空間，塞好再拖回帽子裡。")) +

        step(8, "再拉一頂 B 的帽子",
             '<p>做法跟第 4 步一樣，但把 <b>A</b> 改成 <b>B</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True))
             + look("畫面上有<b>兩頂</b>帽子了。")) +

        step(9, "B 的帽子裡放「設為 0」",
             '<p>再拖一塊 <b>「變數 count 設為 0」</b> 進去。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 設為 ", slot("0"))))
             + look("點 A 幾下讓數字變大，再點 B——螢幕<b>沒反應</b>。再一步就好 👇")) +

        step(10, "最後放一塊「顯示數字 count」",
             '<p>跟第 6、7 步一樣：放「顯示數字」，再把圓圓的 <code>count</code> 塞進去。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 設為 ", slot("0")) +
                                  blk("basic", "顯示數字 ", slot("count"))))
             + note("✨ 這一課最重要的一件事",
                    "「<b>改變 1</b>」＝ 在原本的數字上<b>再加 1</b>（3 變 4）。<br>"
                    "「<b>設為 0</b>」＝ <b>整個換成</b> 0。")
             + look("數字亂跳之後，點 B → 回到 <b>0</b> 🎉")
             + adult("「改變」vs「設為」是這課唯一的觀念，其他都是操作。<br>"
                     "驗收方式：問他「如果我想一次加 5，要改哪裡？」"
                     "答得出來改「改變」後面那個數字，就是懂了。")) +

        tryit("把「改變 <code>1</code>」改成「改變 <code>2</code>」，看每按一下跳多少。",
              "做一個<b>比分板</b>：A 加 1 分，B 改成「改變 <code>-1</code>」變成減 1 分。") +

        final("l4", [
            "我知道變數是一個會記住數字的小盒子",
            "我會用「建立一個變數…」做一個 count",
            "我分得出「改變（加上去）」和「設為（整個換掉）」不一樣",
        ]) + nav_for("l4")
    )
    write("l4", body, "第 4 課：神奇計數器")

# ================= 第 5 課 =================
def build_l5():
    body = (
        top("l5", "第 5 課", "🔁 重複的力量") +
        goal("⭐", "讓星星<b>閃 4 次</b>，再讓 micro:bit <b>自己數數</b>。") +

        '<p>想讓星星閃 4 次，要拼 4 遍一樣的積木嗎？太累了 🥱</p>'
        '<p>只要拼<b>一次</b>，再跟 micro:bit 說「<b>做 4 遍</b>」就好。</p>'

        + step(1, "拿出「重複 4 次」",
               find("loop", "重複 4 次 執行")
               + '<p>拖進 <b>「當啟動時」</b> 裡面。</p>'
               + prog(blk("basic", slot("當啟動時"), hat=True,
                          nest_html=blk("loop", "重複 ", slot("4"), " 次 執行")))
               + look("裡面空空的，還沒事情發生。")) +

        step(2, "第一塊：放星星",
             find("basic", "顯示圖示", "（圖案選<b>星星</b>）")
             + '<p>拖進 <b>「重複 4 次」</b> 裡面。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("loop", "重複 ", slot("4"), " 次 執行",
                                      nest_html=blk("basic", "顯示圖示 ", slot("⭐")))))
             + look("星星亮著，<b>不會閃</b>。對的，還沒做完 👍")
             + leds(STAR, "亮 ✨")) +

        step(3, "第二塊：停一下",
             find("basic", "暫停 100 毫秒", "（把 <code>100</code> 改成 <code>300</code>）")
             + '<p>放在<b>星星的下面</b>。</p>'
             + prog(blk("loop", "重複 ", slot("4"), " 次 執行", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("⭐")) +
                                  blk("basic", "暫停 ", slot("300"), " 毫秒")))
             + look("看起來還是一樣。再兩塊就成功 👇")) +

        step(4, "第三塊：把燈關掉",
             find("basic", "清空畫面", "（燈<b>全部關掉</b>）")
             + '<p>放在「暫停」的<b>下面</b>。</p>'
             + prog(blk("loop", "重複 ", slot("4"), " 次 執行", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("⭐")) +
                                  blk("basic", "暫停 ", slot("300"), " 毫秒") +
                                  blk("basic", "清空畫面")))
             + look("星星開始<b>閃</b>了，但閃得很怪。最後一塊 👇")
             + leds(EMPTY, "暗 🌑")) +

        step(5, "第四塊：暗的時候也停一下",
             '<p>再拖一塊 <b>「暫停」</b>，放在最下面，也改成 <code>300</code>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("loop", "重複 ", slot("4"), " 次 執行",
                                      nest_html=blk("basic", "顯示圖示 ", slot("⭐")) +
                                                blk("basic", "暫停 ", slot("300"), " 毫秒") +
                                                blk("basic", "清空畫面") +
                                                blk("basic", "暫停 ", slot("300"), " 毫秒"))))
             + look("星星<b>亮、暗、亮、暗</b>⋯⋯閃完 <b>4 遍</b>就停下來 ✋")
             + adult("這四塊是一個完整的節奏：亮 → 等 → 暗 → 等。<br>"
                     "如果他覺得「為什麼要停兩次」，讓他把最後一塊拔掉再看一次，"
                     "自己發現「暗的時間太短，看起來就沒閃」。")) +

        step(6, "跟「重複無限次」比一比",
             '<p>這一步<b>不用動手</b>，看懂就好 😊</p>'
             + prog(blk("loop", "重複 ", slot("4"), " 次 執行", hat=True,
                        nest_html='<div class="plainrow">做完 4 遍就<b>停</b> ✋</div>'))
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html='<div class="plainrow"><b>一直做</b>，不會停 ♾️</div>'))
             + look("看得懂就打勾 ✅")
             + adult("什麼時候用哪一個：閃 3 下、跳 5 下這種<b>算得出次數</b>的，用「重複 N 次」；"
                     "心跳燈、時鐘這種<b>一直不停</b>的，用「重複無限次」。<br>"
                     "可以問他：「聖誕燈要用哪一個？」")) +

        step(7, "換個玩法：讓它自己數數",
             '<p>把第 4 課那個盒子 <code>count</code> 拿出來用。</p>'
             '<p>（盒子不見了就去 <b>變數</b> 抽屜再做一個。）</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("count"), " 設為 ", slot("0")) +
                                  blk("loop", "重複 ", slot("5"), " 次 執行",
                                      nest_html=blk("var", "變數 ", slot("count"), " 改變 ", slot("1")) +
                                                blk("basic", "顯示數字 ", slot("count")) +
                                                blk("basic", "暫停 ", slot("300"), " 毫秒"))))
             + look("螢幕自己跑出 <b>1、2、3、4、5</b>——你完全沒按按鈕 ✨")
             + adult("這一步是把第 4 課（盒子）和這一課（重複）接起來，"
                     "是後面第 9、11 課的地基。如果他做得很吃力，可以只做到第 6 步，"
                     "這一步下次上課再補。")) +

        tryit("把星星改成<b>閃 10 次</b>。",
              "把「暫停」改成 <code>100</code>，看它閃得多快。") +

        final("l5", [
            "我知道「重複」可以少拼很多積木",
            "我會用「重複 N 次 執行」做閃爍",
            "我分得出「重複 N 次（會停）」和「重複無限次（不停）」",
        ]) + nav_for("l5")
    )
    write("l5", body, "第 5 課：重複的力量")

# ================= 第 6 課 =================
def build_l6():
    rand = blk("math", "隨機取數 ", slot("1"), " 到 ", slot("6"))
    body = (
        top("l6", "第 6 課", "🎲 搖一搖骰子") +
        goal("🎲", "<b>搖一搖</b> micro:bit，它就跳出 <b>1～6</b> 的點數。") +

        '<p>骰子好玩，是因為<b>每次都不一定</b>。</p>'
        '<p>電腦也會這一招，叫做<b>抽籤</b> 🎰——你跟它要一個 1 到 6，它每次<b>隨便</b>給你一個。</p>'

        + step(1, "拿出抽籤積木",
               find("math", "隨機取數 0 到 10")
               + '<p>先拖到<b>空白的地方</b>放著。把 <code>0</code> 改成 <code>1</code>，'
                 '<code>10</code> 改成 <code>6</code>。</p>'
               + prog(rand)
               + look("積木上寫著「隨機取數 <b>1</b> 到 <b>6</b>」。")) +

        step(2, "拿一頂「搖一搖」的帽子",
             find("event", "當姿勢 晃動 發生")
             + '<p>拖到空白的地方，<b>什麼都不用改</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True))
             + look("畫面多了一頂紫紅色的帽子。")
             + adult("積木上的「姿勢」＝你怎麼拿它：搖、翻過來、歪一邊，它都分得出來。"
                     "下拉選單裡還有「正面朝上」「左側偏低」等等，第 7 課會玩到。")) +

        step(3, "帽子裡放「顯示數字」",
             find("basic", "顯示數字")
             + '<p>拖進帽子裡面。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示數字 ", slot("0"))))
             + look("搖一搖（假的那台按 <b>SHAKE</b>）→ 一直出現 <b>0</b>。")) +

        step(4, "把抽籤積木塞進白框框",
             '<p>把第 1 步那塊<b>紫色的「隨機取數」</b>，'
             '<b>拖進</b>「顯示數字」的白色框框裡。</p>'
             '<p>它們會<b>合體</b>變成一塊。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示數字 ", rand)))
             + look("搖一搖 → 跳出一個數字！再搖會<b>變別的</b> 🎲")
             + leds(THREE, "搖出 3")) +

        step(5, "做一個盒子記住點數",
             '<p>去 <b>變數</b> 抽屜，建立一個新盒子叫 <code>dice</code>。</p>'
             '<p>把 <b>「變數 dice 設為」</b> 放進帽子裡，'
             '再把<b>抽籤積木</b>搬進它的框框。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("var", "變數 ", slot("dice"), " 設為 ", rand) +
                                  blk("basic", "顯示數字 ", slot("dice"))))
             + '<p>再把「顯示數字」裡面換成圓圓的 <code>dice</code>。</p>'
             + look("搖一搖 → 一樣跳數字。看起來沒變，但它<b>記住</b>了 📦")
             + adult("為什麼要多一個盒子：等一下要「判斷是不是 6」，"
                     "必須先把搖到的數字存下來，不然抽一次就跑掉了。")) +

        step(6, "拿出「如果…那麼…否則」",
             find("logic", "如果 … 那麼 … 否則")
             + note("⚠️ 「否則」不是另外一塊",
                    "抽屜裡有<b>兩塊</b>長得很像的。<br>要挑<b>有「否則」</b>的那一塊。")
             + '<p>拖進帽子裡，放在「設為」的<b>下面</b>。</p>'
             + prog(ifelse(slot("（等一下放）"),
                           '<div class="plainrow">（等一下放）</div>',
                           '<div class="plainrow">（等一下放）</div>'))
             + look("架子搭好了，裡面還空空的。")) +

        step(7, "填上條件：dice = 6",
             '<p>去 <b>邏輯</b> 抽屜，拿那塊 <b class="bname">=</b> 積木。</p>'
             '<p>放進「如果」後面，左邊塞圓圓的 <code>dice</code>、右邊打 <code>6</code>。</p>'
             + prog(ifelse(slot("dice") + ' = ' + slot("6"),
                           '<div class="plainrow">（等一下放）</div>',
                           '<div class="plainrow">（等一下放）</div>'))
             + look("條件填好了，但兩條路還是空的。")) +

        step(8, "兩條路各放一樣東西",
             '<p><b>那麼</b> 裡面放 <b>「顯示圖示」</b>，選<b>愛心</b>。</p>'
             '<p><b>否則</b> 裡面放 <b>「顯示數字 dice」</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("var", "變數 ", slot("dice"), " 設為 ", rand) +
                                  ifelse(slot("dice") + ' = ' + slot("6"),
                                         blk("basic", "顯示圖示 ", slot("❤️")),
                                         blk("basic", "顯示數字 ", slot("dice")))))
             + tip("🛣️ 「如果／否則」是什麼",
                   "一個<b>岔路口</b>。搖到 6 走上面，其他走下面。每次<b>只走一條</b>。")
             + look("一直搖。搖到 <b>6</b> → 愛心 ❤️，其他 → 顯示點數。")
             + adult("「只走一條」是這一課的核心。可以問他：「搖到 3 的時候，"
                     "會不會也出現愛心？」讓他自己說出「不會，因為走另一條路」。")) +

        tryit("改成<b>抽籤機</b>：把「隨機取數」改成 <b>1 到 100</b>。",
              "用「顯示指示燈」畫出真的骰子點點（下面是 6 點的樣子）。" + leds(DICE6, "六點")) +

        final("l6", [
            "我知道電腦可以「抽籤」，每次給不一樣的數字",
            "我會用「當姿勢 晃動 發生」做搖一搖",
            "我知道「如果…那麼…否則」是同一塊積木",
        ]) + nav_for("l6")
    )
    write("l6", body, "第 6 課：搖一搖骰子")

# ================= 第 7 課 =================
def build_l7():
    temp = blk("event", "溫度感測值 (°C)")
    light = blk("event", "光線感測值")
    body = (
        top("l7", "第 7 課", "🦸 micro:bit 的超能力") +
        goal("🦸", "做一支<b>溫度計</b>，再做一個會自己亮的<b>小夜燈</b>。") +

        '<p>你有皮膚，感覺得到冷熱。</p>'
        '<p>你有眼睛，感覺得到亮暗。</p>'
        '<p>micro:bit 身上也有<b>會感覺的小零件</b> 👂</p>'
        '<div class="note">🌡️ 知道<b>幾度</b>　　💡 知道<b>亮不亮</b>　　🤸 知道<b>有沒有歪一邊</b></div>'
        '<p>它會把感覺到的東西，變成一個<b>數字</b>給你用。</p>'

        + step(1, "拉一頂 A 的帽子，放「顯示數字」",
               '<p>帽子跟「顯示數字」都學過了，先把它們拼好。</p>'
               + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                          nest_html=blk("basic", "顯示數字 ", slot("0"))))
               + look("點 A → 出現 <b>0</b>。")) +

        step(2, "換成「它感覺到的溫度」",
             find("event", "溫度感測值 (°C)", "（圓圓的那種積木，在<b>輸入</b>抽屜）")
             + '<p><b>拖進</b>「顯示數字」的白色框框裡。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("basic", "顯示數字 ", temp)))
             + look("點 A → 跳出<b>現在幾度</b> 🌡️")
             + tip("🔥 試試看",
                   "下載到真的板子，<b>手指壓住板子</b>暖一下再按 A——數字會變大！")
             + adult("積木上寫「溫度感測值」，講給孩子聽就說「它感覺到的溫度」。"
                     "圓形積木＝一個數字，可以塞進任何白框框，這個概念第 4 課已經鋪過。")) +

        step(3, "小夜燈：找到「重複無限次」",
             '<p>小夜燈要<b>一直</b>盯著房間亮不亮。</p>'
             '<p>畫面上那塊綠色的 <b>「重複無限次」</b> 就是拿來做這個的。</p>'
             + prog(blk("loop", "重複無限次", hat=True))
             + look("找到那塊綠色的就打勾 ✅")) +

        step(4, "裡面放「如果…那麼…否則」",
             find("logic", "如果 … 那麼 … 否則", "（要有「否則」的那塊）")
             + '<p>拖進「重複無限次」裡面。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=ifelse(slot("（等一下放）"),
                                         '<div class="plainrow">（等一下放）</div>',
                                         '<div class="plainrow">（等一下放）</div>')))
             + look("架子搭好了，裡面還空空的。")) +

        step(5, "填條件：比 50 還暗",
             find("logic", "<", "（念做「小於」，在邏輯抽屜）")
             + find("event", "光線感測值", "（<b>0</b> 是全黑，<b>255</b> 是很亮）")
             + '<p>把它們拼成 <b>「光線感測值 &lt; 50」</b>，放到「如果」後面。</p>'
             + prog(ifelse(light + ' &lt; ' + slot("50"),
                           '<div class="plainrow">（等一下放）</div>',
                           '<div class="plainrow">（等一下放）</div>'))
             + tip("🔍 「&lt;」念做「小於」", "整句是「現在<b>比 50 還暗</b>」。")
             + look("條件填好了，兩條路還是空的。")) +

        step(6, "暗就亮星星，亮就關掉",
             '<p><b>那麼</b> 裡面放「顯示圖示」，選<b>星星</b>。</p>'
             '<p><b>否則</b> 裡面放 <b>「清空畫面」</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=ifelse(light + ' &lt; ' + slot("50"),
                                         blk("basic", "顯示圖示 ", slot("⭐")),
                                         blk("basic", "清空畫面"))))
             + look("用手<b>蓋住</b>板子 → 星星亮 ✨；<b>放開</b> → 熄掉。")
             + leds(STAR, "變暗 → 夜燈亮")
             + adult("如果太晚亮或一直亮著，把 <code>50</code> 調大或調小。"
                     "室內光線差異很大，這個數字本來就要現場試——"
                     "讓孩子自己試出「他家的數字」，比給他標準答案好。")) +

        step(7, "拉一頂「往左歪」的帽子",
             find("event", "當姿勢 晃動 發生")
             + '<p>拖出來，點 <b>晃動</b> 的選單，改成 <b>「左側偏低」</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("左側偏低", True), " 發生", hat=True))
             + look("多了一頂帽子，上面寫著「左側偏低」。")
             + adult("「左側偏低」就是往左邊歪。選單裡還有右側偏低、正面朝上、背面朝上、"
                     "標誌朝上、自由掉落——都可以讓他玩玩看。")) +

        step(8, "裡面放向左的箭頭",
             '<p>放一塊「顯示圖示」，選<b>向左的箭頭</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("左側偏低", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("⬅️"))))
             + look("把板子<b>往左歪</b> → 箭頭指左 ⬅️")
             + leds(ARROW_L, "往左歪")) +

        step(9, "再做一頂「往右歪」的",
             '<p>做法一模一樣，選單改成 <b>「右側偏低」</b>，圖案選<b>向右的箭頭</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("右側偏低", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("➡️"))))
             + look("往左歪 → 指左；往右歪 → 指右。像方向盤 🚗")
             + leds(ARROW_R, "往右歪")) +

        tryit("把夜燈的 <code>50</code> 改成 <code>100</code> 或 <code>20</code>，找出最好用的數字。",
              "做一個<b>怕熱的臉</b>：溫度大於 30 就哭臉 😢，不然就笑臉 😀。") +

        final("l7", [
            "我知道 micro:bit 感覺得到冷熱、亮暗、有沒有歪",
            "我會把「溫度感測值」「光線感測值」塞進別的積木裡",
            "我做出了會自己亮的小夜燈",
        ]) + nav_for("l7")
    )
    write("l7", body, "第 7 課：micro:bit 的超能力")

# ================= 第 8 課 =================
def build_l8():
    body = (
        top("l8", "第 8 課", "🎵 音樂盒") +
        goal("🎹", "按按鈕就發出聲音，做一台自己的<b>小鋼琴</b>。") +

        '<p>前面都在玩「<b>看</b>」的。這一課換「<b>聽</b>」的 🎤</p>'
        + note("🔊 聽得到聲音嗎",
               "<b>假的那台</b>直接就有聲音 🔈<br>"
               "真的板子：<b>新款</b>有內建小喇叭；<b>舊款</b>要用鱷魚夾接耳機。") +

        step(1, "先拉一頂 A 的帽子",
             '<p>去 <b>輸入</b> 抽屜，拿 <b>「當按鈕 A 被按下」</b>（第 3 課學過）。</p>'
             '<p>放在空白的地方。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True))
             + look("畫面上多了一頂空空的帽子。")) +

        step(2, "找出會發出聲音的積木",
             '<p>去 <b>音效</b> 抽屜（紅色的）。</p>'
             + note("⚠️ 這塊積木上面是<b>英文字</b>",
                    "它長這樣，<b>不用看懂</b>，找<b>最長的那一塊</b>就對了：")
             + prog(playtone())
             + note("🚫 別拿錯成這一塊",
                    "旁邊有一塊比較短、寫中文的「演奏音階」。<br>"
                    "那塊的聲音<b>不會停</b>，會一直叫。")
             + prog(blk("music", "演奏 音階 ", slot("中音 C")))
             + look("找到最長的那塊就打勾 ✅")
             + adult("MakeCode 上游改過這塊積木的英文原文，繁體中文翻譯因此失效，"
                     "編輯器只好顯示英文 <code>play tone … until done</code>，我們改不了。<br>"
                     "短的那塊中文「演奏音階」是 ringTone，播了不會自己停，"
                     "小孩很容易照中文字挑到它。看到聲音停不下來，就是拿錯了。")) +

        step(3, "把它拖進帽子裡",
             '<p>什麼都<b>不用改</b>，直接放進去。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=playtone()))
             + look("點 A → 「叮」一聲！你的第一個琴鍵完成了 🎵")) +

        step(4, "做第二個琴鍵：B",
             '<p>再做一頂 <b>B</b> 的帽子，裡面一樣放那塊<b>長長的英文積木</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=playtone()))
             + look("點 A 和點 B，聲音<b>一模一樣</b>。下一步來換音 👇")) +

        step(5, "把 B 的音換掉",
             '<p>點積木上的 <b>中音 C</b>，選單會打開。</p>'
             '<p><b>一個一個點點看</b>，用<b>耳朵</b>挑一個你喜歡的 👂</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=playtone("你挑的音")))
             + note("👂 不用看懂那些字",
                    "選單上寫「中音 C」「中音 D」那些是<b>音的名字</b>。<br>"
                    "<b>不用管它</b>，點下去聽聽看，好聽就用。")
             + optional("🎼 想知道音的名字嗎？（可以不看）",
                        "中音 C＝<b>Do</b>、中音 D＝<b>Re</b>、中音 E＝<b>Mi</b>、"
                        "中音 F＝<b>Fa</b>、中音 G＝<b>So</b>。<br>"
                        "上面還有<b>高音</b>（比較尖），下面有<b>低音</b>（比較低沉）。")
             + look("點 A 一個音、點 B 另一個音——兩個琴鍵完成 🎹")) +

        step(6, "做一頂 A+B 的帽子",
             '<p>再拉一頂帽子，把按鈕改成 <b>A+B</b>。</p>'
             '<p>裡面先放<b>一塊</b>，音留 <b>中音 C</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A+B", True), " 被按下", hat=True,
                        nest_html=playtone()))
             + look("兩顆一起按 → 響一聲。")) +

        step(7, "再疊四塊，變成一小段曲子",
             '<p>在下面<b>一塊一塊</b>加上去，每一塊都<b>挑一個不一樣的音</b>。</p>'
             '<p>每加一塊就<b>按一次</b>聽聽看，自己排出好聽的順序 🎶</p>'
             + prog(blk("event", "當按鈕 ", slot("A+B", True), " 被按下", hat=True,
                        nest_html=playtone("中音 C") + playtone("中音 D") + playtone("中音 E") +
                                  playtone("中音 F") + playtone("中音 G")))
             + look("兩顆一起按 → <b>五個音一個接一個</b>唱出來 🎶")
             + leds(NOTE, "唱歌囉")
             + adult("一次疊五塊對孩子太多。請他每加一塊就按一次，"
                     "聽到多一個音再加下一塊——這樣他會自己發現「積木由上往下一個一個做」。")) +

        step(8, "把音變長或變短",
             '<p>點積木上的 <b>1 拍</b>，選單裡改成 <b>1/2 拍</b>。</p>'
             + prog(playtone("中音 C", "1/2 拍") + playtone("中音 D", "2 拍"))
             + tip("⏱️ 「拍」是聲音的長短",
                   "<b>1/2 拍</b>＝短短的，<b>1 拍</b>＝普通，<b>2 拍</b>＝長長的。")
             + look("同樣的音，聽起來變短或變長了。")) +

        tryit("把小鋼琴的音<b>換成你喜歡的</b>。",
              "一邊唱歌一邊<b>顯示圖示</b>，做一支 MV 🎬") +

        final("l8", [
            "我知道聲音的積木在「音效」抽屜（紅色）",
            "我找得到那塊長長的英文積木，也知道別拿錯短的那塊",
            "我把好幾個音排在一起，變成一小段曲子",
        ]) + nav_for("l8")
    )
    write("l8", body, "第 8 課：音樂盒")

# ================= 第 9 課（綜合專題）=================
def build_l9():
    body = (
        top("l9", "第 9 課 · 大魔王關", "🏆 電子寵物大挑戰") +
        goal("🐣", "養一隻<b>電子寵物</b>。它會<b>肚子餓</b>，你要<b>餵它、陪它玩</b>。") +

        '<div class="pill" style="justify-content:flex-start">'
        '<span>💡 圖示</span><span>🅰️ 按鈕</span><span>📦 變數</span>'
        '<span>🔁 重複無限次</span><span>🤔 如果／否則</span>'
        '<span>🤸 搖一搖</span><span>🎵 聲音</span></div>'
        '<p class="lead">這一關會用到<b>前面每一課</b>的本領。慢慢來，一塊一塊拼。</p>'

        + step(1, "做一個盒子裝寵物的心情",
               '<p>去 <b>變數</b> 抽屜，建立一個盒子叫 <code>happy</code>。</p>'
               '<p>裡面的數字<b>越大，牠越開心</b>。</p>'
               + look("抽屜裡多出寫著 <code>happy</code> 的新積木。")) +

        step(2, "開機先給牠 5 分心情",
             '<p>把 <b>「變數 happy 設為」</b> 拖進 <b>「當啟動時」</b>，數字改成 <code>5</code>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("happy"), " 設為 ", slot("5"))))
             + look("畫面沒變化，是正常的 👍")) +

        step(3, "開機露出笑臉",
             '<p>在下面加一塊「顯示圖示」，選<b>笑臉</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("happy"), " 設為 ", slot("5")) +
                                  blk("basic", "顯示圖示 ", slot("😀"))))
             + look("一開始就笑笑的 😀")) +

        step(4, "拉一頂 A 的帽子（餵牠吃東西）",
             '<p>去 <b>輸入</b> 抽屜拿 <b>「當按鈕 A 被按下」</b>，放空白處。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True))
             + look("多了一頂空帽子。")) +

        step(5, "吃東西 → 心情加 1",
             '<p>放一塊 <b>「變數 happy 改變 1」</b> 進帽子裡。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("happy"), " 改變 ", slot("1"))))
             + look("點 A 還沒反應。再加兩塊就有了 👇")) +

        step(6, "吃東西 → 露出好吃的表情",
             '<p>加一塊「顯示圖示」，挑一個<b>好吃的表情</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("happy"), " 改變 ", slot("1")) +
                                  blk("basic", "顯示圖示 ", slot("😋"))))
             + look("點 A → 換表情了 😋")) +

        step(7, "吃東西 → 加一聲「叮」",
             '<p>去 <b>音效</b> 抽屜，拿那塊<b>長長的英文積木</b>（第 8 課那塊）。</p>'
             '<p>放在最上面，拍數改成 <b>1/2 拍</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=playtone("中音 C", "1/2 拍") +
                                  blk("var", "變數 ", slot("happy"), " 改變 ", slot("1")) +
                                  blk("basic", "顯示圖示 ", slot("😋"))))
             + look("點 A → 「叮」一聲 ＋ 好吃的表情 😋")) +

        step(8, "拉一頂「搖一搖」的帽子（陪牠玩）",
             '<p>拿 <b>「當姿勢 晃動 發生」</b>，放空白處。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True))
             + look("現在有<b>三頂</b>帽子了。")) +

        step(9, "陪玩 → 加心情、換表情",
             '<p>裡面放 <b>「變數 happy 改變 1」</b> 和一張<b>很開心的臉</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("var", "變數 ", slot("happy"), " 改變 ", slot("1")) +
                                  blk("basic", "顯示圖示 ", slot("😆"))))
             + look("搖一搖 → 開心的表情 😆")) +

        step(10, "讓牠會肚子餓：先放「暫停」",
             '<p>用畫面上的 <b>「重複無限次」</b>。</p>'
             '<p>裡面放一塊「暫停」，數字改成 <code>5000</code>（五秒）。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "暫停 ", slot("5000"), " 毫秒")))
             + look("什麼都沒發生，是正常的 👍")) +

        step(11, "每五秒餓一點",
             '<p>下面加 <b>「變數 happy 改變」</b>，數字打 <code>-1</code>。</p>'
             + note("➖ 「改變 -1」是什麼", "就是<b>減 1</b>。前面加一個減號就好。")
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "暫停 ", slot("5000"), " 毫秒") +
                                  blk("var", "變數 ", slot("happy"), " 改變 ", slot("-1"))))
             + look("表情還沒變，因為還沒叫它看心情。最後一步 👇")) +

        step(12, "心情低就變難過",
             '<p>下面加一塊 <b>「如果…那麼…否則」</b>。</p>'
             '<p>條件是 <b>happy &gt; 3</b>：<b>那麼</b> 放笑臉，<b>否則</b> 放哭臉。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "暫停 ", slot("5000"), " 毫秒") +
                                  blk("var", "變數 ", slot("happy"), " 改變 ", slot("-1")) +
                                  ifelse(slot("happy") + ' &gt; ' + slot("3"),
                                         blk("basic", "顯示圖示 ", slot("😀")),
                                         blk("basic", "顯示圖示 ", slot("😢")))))
             + look("放著不管 → 牠會變<b>難過</b> 😢。餵牠或搖牠 → 又<b>開心</b> 😀")
             + leds(SMILE, "有照顧") + leds(SAD, "太久沒理")
             + adult("這一課的重點不是新積木，是<b>四塊帽子同時在跑</b>："
                     "開機、按 A、搖一搖、重複無限次。<br>"
                     "孩子最常卡在「為什麼不用把它們接在一起」——"
                     "可以指著畫面說：每一頂帽子都是一個獨立的規則，"
                     "就像寵物同時會被餵、會肚子餓、會有表情。<br>"
                     "12 步很長，分兩次上完完全可以，做到第 9 步就是一隻能餵能玩的寵物了。")) +

        tryit("<b>會生病</b>：happy 太低（小於 2）就顯示骷髏 💀。",
              "<b>幫牠取名字</b>：開機時先用「顯示文字」跑出寵物的名字。") +

        final("l9", [
            "我用一個變數（happy）當寵物的心情",
            "我用按鈕和搖一搖照顧牠",
            "我用「重複無限次」讓牠會肚子餓",
            "我用「如果…那麼…否則」讓牠換表情",
        ]) +

        '<div class="goal win"><div class="big">🎉</div><div>'
        '<h3>基礎篇完成，太厲害了！</h3>'
        '<p>從讓一顆燈亮起來，到養出一隻會撒嬌的電子寵物。<br>'
        '燈、按鈕、盒子、重複、抽籤、判斷、感覺、聲音——<b>這些都是真的程式設計本領</b>！<br>'
        '休息一下，準備好就進<b>進階篇</b>：隔空連線、小遊戲，還有香蕉鋼琴 🍌</p></div></div>'

        + nav_for("l9")
    )
    write("l9", body, "第 9 課：電子寵物大挑戰")

# ================= 第 10 課 =================
def build_l10():
    body = (
        top("l10", "第 10 課 · 進階篇", "📡 廣播雙人連線") +
        goal("📡", "讓<b>兩台</b> micro:bit <b>隔空聊天</b>，不用任何電線。") +

        '<p>廣播就像<b>對講機</b> 📻：一台<b>喊</b>，另一台<b>聽到</b>。</p>'
        '<p>兩台要先講好<b>同一個暗號</b> 🔑，才聽得到對方。</p>'
        + note("💻 只有一台也能玩",
               "只要用到<b>廣播</b>積木，假的那台會自動<b>變成兩台</b>，可以看它們互傳訊息！") +

        step(1, "先講好暗號",
             find("radio", "廣播群組設為 1")
             + note("⚠️ 抽屜叫「廣播」，不是「無線電」", "粉紅色的那個抽屜。")
             + '<p>拖進 <b>「當啟動時」</b> 裡面，數字保持 <code>1</code>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("radio", "廣播群組設為 ", slot("1"))))
             + tip("🔑 暗號是什麼",
                   "只有<b>同一個號碼</b>的 micro:bit 聽得到彼此。"
                   "想跟朋友玩不被別人吵，就約好一個祕密號碼。")
             + look("畫面上出現<b>兩台</b>假的 micro:bit 了！")) +

        step(2, "拉一頂 A 的帽子",
             '<p>去 <b>輸入</b> 抽屜拿 <b>「當按鈕 A 被按下」</b>，放空白處。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True))
             + look("多了一頂空帽子。")) +

        step(3, "按 A 就喊一聲",
             find("radio", "廣播發送數字 0")
             + '<p>放進帽子裡，把 <code>0</code> 改成 <code>7</code>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("radio", "廣播發送數字 ", slot("7"))))
             + look("點 A 還沒反應——因為<b>還沒人在聽</b>。下一步 👇")) +

        step(4, "拉一頂「聽到了」的帽子",
             find("radio", "當收到廣播數字 receivedNumber", "（這是一頂<b>帽子</b>）")
             + '<p>拖到空白的地方，<b>什麼都不用改</b>。</p>'
             + prog(blk("radio", "當收到廣播數字 ", slot("receivedNumber", True), hat=True))
             + look("多了一頂粉紅色的帽子。")) +

        step(5, "聽到就跳出愛心",
             '<p>裡面放一塊「顯示圖示」，選<b>愛心</b>。</p>'
             + prog(blk("radio", "當收到廣播數字 ", slot("receivedNumber", True), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("❤️"))))
             + look("在<b>其中一台</b>點 A → <b>另一台</b>跳出愛心 ❤️ 隔空傳情 💌")
             + leds(HEART, "收到訊息")) +

        step(6, "再加一聲「叮」",
             '<p>愛心下面加一塊<b>長長的英文音效積木</b>（第 8 課那塊）。</p>'
             + prog(blk("radio", "當收到廣播數字 ", slot("receivedNumber", True), hat=True,
                        nest_html=blk("basic", "顯示圖示 ", slot("❤️")) +
                                  playtone("中音 C")))
             + look("收到訊息 → 愛心 ＋ 「叮」一聲 🔔")
             + adult("兩台都要下載<b>同一個程式</b>，因為每一台都同時是「喊的人」和「聽的人」。<br>"
                     "孩子常問「為什麼自己按 A 自己沒反應」——因為喊的那台只負責喊，"
                     "接收的帽子是給<b>對方</b>觸發的。")) +

        tryit("用<b>不同數字</b>代表不同意思：收到 1 顯示笑臉、收到 2 顯示星星（用「如果／否則」）。",
              "有兩塊真板子的話，兩台都<b>下載同一個程式</b>，就能互相傳訊息了 📡") +

        final("l10", [
            "我知道兩台 micro:bit 要用同一個「暗號」（群組）",
            "我會用「廣播發送數字」喊話",
            "我會用「當收到廣播數字」接話",
        ]) + nav_for("l10")
    )
    write("l10", body, "第 10 課：廣播雙人連線")

# ================= 第 11 課 =================
def build_l11():
    body = (
        top("l11", "第 11 課 · 進階篇", "🎮 LED 小遊戲：燈光快停") +
        goal("🎯", "一顆燈<b>來回跑</b>，你要抓準時機按 A，讓它停在<b>正中間</b>。") +

        '<p>25 顆燈，每一顆都有自己的<b>位置</b>，用兩個數字說：</p>'
        '<div class="note"><b>x</b>＝左右<b>第幾個</b>（0～4）　　<b>y</b>＝上下<b>第幾排</b>（0～4）</div>'

        + step(1, "先點亮正中間那一顆",
               find("led", "點亮 x 0 y 0")
               + '<p>拖進「當啟動時」，兩個數字都改成 <code>2</code>。</p>'
               + prog(blk("basic", slot("當啟動時"), hat=True,
                          nest_html=blk("led", "點亮 x ", slot("2"), " y ", slot("2"))))
               + look("<b>正中央</b>那一顆燈亮起來。")
               + leds(CENTER, "x=2, y=2 → 正中央")) +

        step(2, "做兩個盒子",
             '<p>去 <b>變數</b> 抽屜，建立<b>兩個</b>盒子：</p>'
             '<p>📦 <code>x</code>＝燈現在在<b>左右第幾個</b></p>'
             '<p>📦 <code>dir</code>＝<b>往哪邊跑</b>（<code>1</code> 往右、<code>-1</code> 往左）</p>'
             + look("抽屜裡多出 <code>x</code> 和 <code>dir</code> 的積木。")) +

        step(3, "開機時先設定好",
             '<p>在 <b>「當啟動時」</b> 裡放兩塊「設為」：<code>x</code> 設為 <code>0</code>、'
             '<code>dir</code> 設為 <code>1</code>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("x"), " 設為 ", slot("0")) +
                                  blk("var", "變數 ", slot("dir"), " 設為 ", slot("1"))))
             + look("畫面沒變化，是正常的 👍")) +

        step(4, "讓燈畫出來、再擦掉",
             '<p>在 <b>「重複無限次」</b> 裡放兩塊：先 <b>「清空畫面」</b>，'
             '再 <b>「點亮 x y」</b>。</p>'
             '<p>x 的框框塞圓圓的 <code>x</code>，y 打 <code>2</code>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "清空畫面") +
                                  blk("led", "點亮 x ", slot("x"), " y ", slot("2"))))
             + look("最<b>左邊</b>中間那顆燈亮著，還不會動。")) +

        step(5, "讓它動起來",
             '<p>下面再加兩塊：<b>「暫停 200 毫秒」</b>，'
             '然後 <b>「變數 x 改變」</b>，框框裡塞圓圓的 <code>dir</code>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "清空畫面") +
                                  blk("led", "點亮 x ", slot("x"), " y ", slot("2")) +
                                  blk("basic", "暫停 ", slot("200"), " 毫秒") +
                                  blk("var", "變數 ", slot("x"), " 改變 ", slot("dir"))))
             + look("燈往右邊跑⋯⋯然後<b>跑出畫面不見了</b> 😅 下一步修好它 👇")) +

        step(6, "跑到最右邊就轉頭",
             '<p>加一塊 <b>「如果…那麼」</b>——這次用<b>沒有</b>「否則」的那塊。</p>'
             '<p>條件 <b>x &gt; 3</b>，裡面放 <b>「變數 dir 設為 -1」</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("var", "變數 ", slot("x"), " 改變 ", slot("dir")) +
                                  ifelse(slot("x") + ' &gt; ' + slot("3"),
                                         blk("var", "變數 ", slot("dir"), " 設為 ", slot("-1")))))
             + look("燈跑到右邊會<b>轉頭往回跑</b>，但跑到左邊又不見了。")) +

        step(7, "跑到最左邊也轉頭",
             '<p>再加一塊一樣的，條件改成 <b>x &lt; 1</b>，裡面放 '
             '<b>「變數 dir 設為 1」</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "清空畫面") +
                                  blk("led", "點亮 x ", slot("x"), " y ", slot("2")) +
                                  blk("basic", "暫停 ", slot("200"), " 毫秒") +
                                  blk("var", "變數 ", slot("x"), " 改變 ", slot("dir")) +
                                  ifelse(slot("x") + ' &gt; ' + slot("3"),
                                         blk("var", "變數 ", slot("dir"), " 設為 ", slot("-1"))) +
                                  ifelse(slot("x") + ' &lt; ' + slot("1"),
                                         blk("var", "變數 ", slot("dir"), " 設為 ", slot("1")))))
             + look("燈像乒乓球一樣<b>左右彈來彈去</b> 🏓")
             + adult("這是這套教材最難的一步。<code>dir</code> 存的是「方向」，"
                     "碰到邊就把方向反過來——這個想法比積木本身難。<br>"
                     "可以用手在桌上來回走給他看，走到桌邊就轉身，"
                     "邊走邊說「現在 dir 是往右／現在改成往左」。")) +

        step(8, "拉一頂 A 的帽子，加上判斷",
             '<p>做一頂 <b>A</b> 的帽子，裡面放 <b>有「否則」</b> 的那塊。</p>'
             '<p>條件是 <b>x = 2</b>（正中間）。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=ifelse(slot("x") + ' = ' + slot("2"),
                                         '<div class="plainrow">（等一下放）</div>',
                                         '<div class="plainrow">（等一下放）</div>')))
             + look("架子好了，兩條路還空著。")) +

        step(9, "贏了笑臉，輸了哭臉",
             '<p><b>那麼</b> 放<b>笑臉</b> ＋ 一個<b>音</b>（音效抽屜那塊長長的英文積木）。</p>'
             '<p><b>否則</b> 放<b>哭臉</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=ifelse(slot("x") + ' = ' + slot("2"),
                                         blk("basic", "顯示圖示 ", slot("😀")) +
                                         playtone("中音 G"),
                                         blk("basic", "顯示圖示 ", slot("😢")))))
             + look("燈跑到正中間<b>那一瞬間</b>按 A → 笑臉＋歡呼 🎉 按錯 → 哭臉 😢")) +

        tryit("把「暫停 <code>200</code>」改小，燈跑更快、更難抓。",
              "加<b>分數</b>：贏了就 <code>score</code> 改變 1，再用「顯示數字」秀出來。") +

        final("l11", [
            "我知道每顆燈有 x（左右第幾個）和 y（上下第幾排）",
            "我用變數＋重複無限次讓燈自己跑，碰邊就轉頭",
            "我做出了有輸有贏的小遊戲",
        ]) + nav_for("l11")
    )
    write("l11", body, "第 11 課：LED 小遊戲")

# ================= 第 12 課（最終關）=================
def build_l12():
    def touch(pin, n, num):
        return blk("event", "當引腳 ", slot(pin, True), " 被按下", hat=True,
                   nest_html=playtone(n, "1/2 拍") +
                             blk("basic", "顯示數字 ", slot(num)))
    body = (
        top("l12", "第 12 課 · 最終關", "🍌 觸摸香蕉鋼琴") +
        goal("🎹", "用<b>香蕉</b>當琴鍵！手一碰就發出聲音 🍌🎵") +

        '<p>看 micro:bit 最下面那一排<b>金色的大孔</b>，上面寫著 <b>0、1、2、3V、GND</b>。</p>'
        '<p>其中 <b>P0、P1、P2</b> 很特別——它們知道<b>有沒有被碰到</b>。</p>'

        + step(1, "拉一頂「碰到 P0」的帽子",
               find("event", "當引腳 P0 被按下", "（在<b>輸入</b>抽屜裡）")
               + note("⚠️ 積木上寫「被<b>按下</b>」", "不是「被觸碰」，別找錯了。")
               + '<p>拖到空白的地方。</p>'
               + prog(blk("event", "當引腳 ", slot("P0", True), " 被按下", hat=True))
               + look("多了一頂帽子，上面寫著 <b>P0</b>。")) +

        step(2, "第一個琴鍵：放一個音",
             '<p>裡面放<b>音效抽屜那塊長長的英文積木</b>，拍數改 <b>1/2 拍</b>。</p>'
             '<p>再放一塊「顯示數字」，打 <code>1</code>。</p>'
             + prog(touch("P0", "中音 C", "1"))
             + look("在假的那台上，<b>點一下 P0 那個金色的孔</b> → 響一聲 🎵")) +

        step(3, "第二個琴鍵：P1",
             '<p>再拖一頂一樣的帽子，點 <b>P0</b> 的選單改成 <b>P1</b>。</p>'
             '<p>裡面的音改成 <b>中音 E</b>，數字打 <code>3</code>。</p>'
             + prog(touch("P1", "中音 E", "3"))
             + look("點 P1 那個孔 → <b>不一樣</b>的音 🎵")) +

        step(4, "第三個琴鍵：P2",
             '<p>做法一樣，選單改 <b>P2</b>，音改 <b>中音 G</b>，數字打 <code>5</code>。</p>'
             + prog(touch("P2", "中音 G", "5"))
             + look("三個孔各一個音——三個琴鍵完成 🎹")
             + leds(NOTE, "碰一下就唱歌")) +

        step(5, "夾上香蕉",
             '<p>用<b>鱷魚夾</b>，一端夾 <b>P0</b>，另一端夾一根<b>香蕉</b> 🍌</p>'
             + look("線接好了，但還不會響。下一步是關鍵 👇")) +

        step(6, "手要捏住 GND",
             '<p>再用一條線夾住 <b>GND</b>。</p>'
             '<p>你的手<b>捏住它不要放</b>，另一隻手去<b>碰香蕉</b>。</p>'
             + tip("💡 沒有香蕉也行",
                   "鋁箔紙、金屬湯匙、濕海綿、朋友的手⋯⋯只要<b>會導電</b>都行。")
             + look("碰香蕉 → 發出聲音 🍌🎵")
             + adult("最常見的失敗原因就是<b>手放掉了 GND</b>。<br>"
                     "電要繞一圈才會通：板子 → 香蕉 → 手 → GND → 回到板子。"
                     "手鬆開，圈就斷了。<br>"
                     "另外香蕉太乾也可能不靈，換一根或改用濕海綿。")) +

        tryit("三個音<b>換成你喜歡的</b>，彈一小段旋律。",
              "用不同<b>水果</b>當琴鍵，看哪一種最好彈。") +

        final("l12", [
            "我知道 P0、P1、P2 這三個金色的孔感覺得到被碰",
            "我會用「當引腳 被按下」讓碰觸發出聲音",
            "我知道手要一直捏著 GND，才彈得出聲音",
        ]) +

        '<div class="goal win final-win"><div class="big">🏆</div><div>'
        '<h3>全部闖關成功！你是 micro:bit 大師 🎓</h3>'
        '<p>從第一顆亮起來的燈，一路到會連線、會玩遊戲、還會彈香蕉鋼琴。<br>'
        '你已經學會了<b>真正的程式設計</b>。<br><br>'
        '最棒的還在後面：現在換你<b>發明自己的作品</b>——想做什麼，就用積木把它拼出來吧！🌟</p></div></div>'

        + nav_for("l12")
    )
    write("l12", body, "第 12 課：觸摸香蕉鋼琴")

# ================= 101 遊戲區 =================
# 每個遊戲宣告自己用到哪幾塊積木（BLOCKS 的 id）。build 時會檢查 id 都存在，
# 並算出所有遊戲合起來的涵蓋率——「用盡可能多的積木」才是可驗證的，不是喊口號。
GAMES = [
    # tier="easy"：完全不用變數、不用 x/y 座標、不用音名。給還沒準備好的孩子先玩。
    dict(id="e1", em="✌️", title="猜拳機", sub="搖一搖，隨機出石頭、剪刀或布", tier="easy",
         uses=[
             # 基本關
             "event.onGesture", "basic.showLeds", "math.random", "logic.eq", "logic.ifElse",
             # 加料關
             "basic.showIcon", "basic.pause", "basic.clearScreen", "music.playTone",
             "basic.onStart", "var.set", "var.change", "var.get", "basic.showNumber",
         ]),
    dict(id="e2", em="⚡", title="反應王", sub="燈在左邊按 A、右邊按 B，看你多快", tier="easy",
         uses=[
             # 基本關
             "basic.onStart", "basic.showString", "basic.forever", "math.random",
             "logic.eq", "logic.ifElse", "basic.showLeds", "basic.pause",
             "event.buttonIsPressed", "basic.showIcon", "basic.clearScreen",
             # 加料關
             "music.playTone", "event.onGesture", "var.set", "var.change", "var.get",
             "basic.showNumber",
         ]),
    dict(id="g1", em="⭐", title="接星星", sub="星星掉下來，左右跑去接住它", tier="main",
         uses=[
             # 基本關
             "basic.onStart", "basic.forever", "basic.clearScreen", "basic.pause",
             "basic.showNumber", "led.plot", "var.set", "var.change", "var.get",
             "math.random", "event.onButton", "logic.if", "logic.ifElse",
             "logic.eq", "logic.lt", "music.playTone",
             # 加料關
             "event.onGesture", "basic.showIcon", "basic.showString", "basic.showLeds",
             "basic.showArrow", "loop.repeat", "loop.forIndex", "event.lightLevel",
             "math.sub", "math.mul",
         ]),
    dict(id="g2", em="🔨", title="打地鼠", sub="地鼠冒出來，在左邊按 A、右邊按 B", tier="main",
         uses=[
             "basic.onStart", "basic.forever", "basic.clearScreen", "basic.pause",
             "basic.showNumber", "led.plot", "led.unplot", "var.set", "var.change",
             "var.get", "math.random", "logic.ifElse", "logic.lt", "music.playTone",
             "event.buttonIsPressed",
             # 加料關
             "loop.while", "logic.true", "logic.or", "led.toggle", "music.rest",
             "event.onPin", "event.pinIsPressed", "led.brightness", "math.add",
         ]),
    dict(id="g3", em="🪨", title="躲石頭", sub="石頭一直掉，左右閃開，活越久分越高", tier="main",
         uses=[
             "basic.onStart", "basic.clearScreen", "basic.pause", "basic.showNumber",
             "basic.showIcon", "led.plot", "led.point", "var.set", "var.change",
             "var.get", "math.random", "event.onButton", "logic.if", "logic.and",
             "logic.eq", "loop.while", "music.ringTone", "music.stopAll",
             # 加料關
             "radio.setGroup", "radio.sendNumber", "radio.onNumber",
             "radio.sendString", "radio.onString", "event.temperature", "loop.repeat",
         ]),
]

def _block_by_id(bid):
    for b in BLOCKS:
        if b["id"] == bid:
            return b
    raise KeyError(f"GAMES 裡的 uses 用到不存在的積木 id：{bid}")

def game_by_id(gid):
    return [g for g in GAMES if g["id"] == gid][0]

def covered_ids():
    out = set()
    for g in GAMES:
        out |= set(g["uses"])
    return out

def game_top(gid, label, title):
    G = game_by_id(gid)
    return (f'<div class="crumb"><a href="index.html">課程地圖</a> / '
            f'<a href="101.html">101 遊戲區</a> / {esc(G["title"])}</div>'
            f'<span class="eyebrow">{esc(label)}</span>' + done_badge() + f'<h1>{title}</h1>')

def stage(emoji, title, text):
    """基本關／加料關 的分隔標題。"""
    return (f'<div class="stage"><span class="em">{emoji}</span>'
            f'<span class="t">{esc(title)}</span><span class="d">{text}</span></div>')

def uses_section(gid):
    """自動列出這個遊戲用到的積木，重用圖鑑的渲染。"""
    G = game_by_id(gid)
    seen, cards = set(), []
    for bid in G["uses"]:
        if bid in seen:
            continue
        seen.add(bid)
        b = _block_by_id(bid)
        cards.append(f'<div class="ucard">{render_block(b)}<p>{esc(b["desc"])}</p></div>')
    return ('<h2>🧱 這個遊戲用到的積木</h2>'
            f'<p class="lead" style="margin-top:0">一共 <b>{len(seen)}</b> 塊。'
            '看不懂哪一塊，就回 <a href="blocks.html">積木圖鑑</a> 翻一翻。</p>'
            '<div class="uses">' + "".join(cards) + '</div>')

def game_nav(gid):
    ids = [g["id"] for g in GAMES]
    i = ids.index(gid)
    left = '<a class="btn ghost" href="101.html">← 回遊戲區</a>'
    right = ''
    if i < len(GAMES) - 1:
        n = GAMES[i + 1]
        right = f'<a class="btn g" href="{n["id"]}.html">{n["em"]} {esc(n["title"])} →</a>'
    return f'<div class="nav">{left}<span class="sp"></span>{right}</div>'

def write_game(gid, body, title):
    open(os.path.join(REPO, f"{gid}.html"), "w").write(
        page(gid, body, title, f' data-lesson="{gid}"'))

# ---- 遊戲區首頁 ----
def build_games_hub():
    cov = covered_ids()
    missing = [b for b in BLOCKS if b["id"] not in cov]

    def cards_for(tier):
        out = []
        for g in [x for x in GAMES if x["tier"] == tier]:
            out.append(f'<a class="gcard" href="{g["id"]}.html"><span class="em">{g["em"]}</span>'
                       f'<h3>{esc(g["title"])}</h3><p>{esc(g["sub"])}</p>'
                       f'<span class="n">用到 {len(set(g["uses"]))} 塊積木</span></a>')
        return '<div class="gcards">' + "".join(out) + '</div>'

    n_easy = len([g for g in GAMES if g["tier"] == "easy"])
    n_main = len([g for g in GAMES if g["tier"] == "main"])

    miss_html = ''
    if missing:
        items = "".join(f'<div class="ucard">{render_block(b)}<p>{esc(b["desc"])}</p></div>'
                        for b in missing)
        miss_html = ('<h2>🕳️ 這些遊戲沒用到的積木</h2>'
                     f'<p class="lead" style="margin-top:0">還有 <b>{len(missing)}</b> 塊沒派上用場。'
                     '想挑戰的話，看看能不能把它塞進你的遊戲裡 💪</p>'
                     '<div class="uses">' + items + '</div>')

    body = (
        '<div class="crumb"><a href="index.html">課程地圖</a> / 101 遊戲區</div>'
        '<span class="eyebrow">動手做遊戲</span>'
        '<h1>🎮 101 遊戲區</h1>'

        + goal("🕹️", f"用積木做出 <b>{len(GAMES)} 個真的能玩</b>的小遊戲。")

        + '<p><a href="blocks.html">積木圖鑑</a>是<b>認字</b>，這裡是<b>造句</b> ✍️</p>'
        '<p>每個遊戲玩法都不一樣，所以會用到<b>不同抽屜</b>的積木。</p>'

        + '<div class="bar101"><div class="fill" style="width:'
        + f'{len(cov) / len(BLOCKS) * 100:.0f}%"></div>'
        + f'<span class="txt">這些遊戲一共用到 {len(cov)} / {len(BLOCKS)} 塊積木</span></div>'

        + note("🧩 每個遊戲都分兩段",
               "<b>🎮 基本關</b>：做完就<b>能玩了</b>。<br>"
               "<b>🍬 加料關</b>：一關一個小點子，<b>做幾關都可以</b>，隨時停下來都算完成。")

        + f'<h2>🌱 先玩這個（{n_easy} 個）</h2>'
        + '<p class="lead" style="margin-top:0">'
        '<b>不用盒子（變數）</b>、<b>不用數格子（座標）</b>，'
        '學過前面幾課就做得完 👍</p>'
        + cards_for("easy")

        + f'<h2>🔥 想挑戰再玩（{n_main} 個）</h2>'
        + '<p class="lead" style="margin-top:0">'
        '這幾個會用到<b>變數</b>和<b>座標（x、y）</b>，比較難。<br>'
        '先把上面兩個玩熟再來，不急 🙂</p>'
        + cards_for("main")

        + adult("上面兩個入門遊戲<b>完全不用變數，也不用 x/y 座標</b>——"
                "這兩個概念對小一升小二是最大的門檻，所以先繞過去，"
                "讓他先嘗到「我做出一個遊戲」的成就感。<br>"
                "兩個入門遊戲的<b>最後一關加料</b>才引入變數，而且明講可以跳過。"
                "等他自己說「我想記分數」，再教變數會好吸收很多。<br>"
                "下面三個是進階的，什麼時候做都可以，做不動就先放著。")

        + miss_html
        + '<div class="nav"><a class="btn ghost" href="index.html">← 回地圖</a>'
        '<span class="sp"></span>'
        + f'<a class="btn g" href="{GAMES[0]["id"]}.html">'
        + f'{GAMES[0]["em"]} {esc(GAMES[0]["title"])} →</a></div>'
    )
    open(os.path.join(REPO, "101.html"), "w").write(
        page("101", body, "101 遊戲區：用積木做三個小遊戲", ' data-lesson="101"'))

# ---- ✌️ 猜拳機（入門：不用變數、不用座標、不用音名）----
def build_e1():
    rand3 = blk("math", "隨機取數 ", slot("0"), " 到 ", slot("2"))
    rand2 = blk("math", "隨機取數 ", slot("0"), " 到 ", slot("1"))

    body = (
        game_top("e1", "入門遊戲 · 第一個", "✌️ 猜拳機") +
        goal("✌️", "搖一搖，micro:bit 幫你出<b>石頭、剪刀或布</b>。") +

        '<p>這個遊戲<b>不用盒子（變數）</b>，也<b>不用數格子</b>。</p>'
        '<p>三張圖你自己畫，搖一搖就隨機出一張 🎲</p>'

        + stage("🎮", "基本關", "做完這 7 步，遊戲就<b>可以玩了</b>。")

        + step(1, "拉一頂「搖一搖」的帽子",
               find("event", "當姿勢 晃動 發生")
               + '<p>拖到空白的地方，<b>什麼都不用改</b>。</p>'
               + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True))
               + look("畫面多了一頂紫紅色的帽子。")) +

        step(2, "先畫一個石頭",
             find("basic", "顯示指示燈", "（在<b>基本</b>抽屜，藍色的）")
             + '<p>拖進帽子裡，照下面這樣點格子：</p>'
             + leds(ROCK, "石頭 ✊")
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示指示燈 ", slot("✊ 石頭"))))
             + look("<b>搖一搖</b>（假的那台按 SHAKE）→ 出現石頭 ✊")) +

        step(3, "拿出抽籤積木",
             find("math", "隨機取數 0 到 10")
             + '<p>先拖到<b>空白的地方</b>放著。</p>'
             '<p>把 <code>10</code> 改成 <code>2</code>——這樣它會抽出 <b>0、1、2</b> 三個數字之一。</p>'
             + prog(rand3)
             + look("積木上寫著「隨機取數 <b>0</b> 到 <b>2</b>」。")) +

        step(4, "問它「抽到 0 嗎？」",
             find("logic", "如果 … 那麼 … 否則", "（要有<b>「否則」</b>的那塊）")
             + '<p>拖進帽子裡。條件用 <b>邏輯</b> 抽屜的 <b class="bname">=</b>，'
             '左邊塞<b>抽籤積木</b>、右邊打 <code>0</code>。</p>'
             '<p>再把<b>石頭</b>那塊搬進 <b>那麼</b> 裡面。</p>'
             + prog(ifelse(rand3 + ' = ' + slot("0"),
                           blk("basic", "顯示指示燈 ", slot("✊ 石頭")),
                           '<div class="plainrow">（等一下放）</div>'))
             + look("搖一搖：<b>有時候</b>出石頭，有時候<b>什麼都沒有</b>。快好了 👇")) +

        step(5, "在「否則」裡再問一次",
             '<p>再拖<b>一塊</b>「如果…那麼…否則」，放進 <b>否則</b> 裡面。</p>'
             '<p>條件是<b>另一塊</b>抽籤積木（這次改成 <b>0 到 1</b>）<b class="bname">=</b> <code>0</code>。</p>'
             + prog(ifelse(rand2 + ' = ' + slot("0"),
                           '<div class="plainrow">（等一下放剪刀）</div>',
                           '<div class="plainrow">（等一下放布）</div>'))
             + look("架子搭好了，兩格還空空的。")
             + adult("為什麼要<b>再抽一次</b>、而且範圍是 0 到 1：<br>"
                     "第一次抽 0～2，抽中 0 的機率是 <b>1/3</b> → 石頭。<br>"
                     "剩下的 <b>2/3</b> 再抽 0～1，各一半 → 剪刀 <b>1/3</b>、布 <b>1/3</b>。<br>"
                     "三種剛好各 1/3，很公平。<br>"
                     "如果改成「否則如果 抽籤 0～2 = 1」再抽一次，機率就會跑掉——"
                     "因為那是<b>重新抽</b>，不是接續前面的結果。")) +

        step(6, "畫剪刀",
             '<p>拖一塊「顯示指示燈」放進<b>那麼</b>，照這樣點：</p>'
             + leds(SCISS, "剪刀 ✌️")
             + prog(blk("basic", "顯示指示燈 ", slot("✌️ 剪刀")))
             + look("搖一搖：石頭跟剪刀<b>輪流</b>出現了。最後一張 👇")) +

        step(7, "畫布",
             '<p>再拖一塊放進<b>否則</b>，這次<b>整片點滿</b>：</p>'
             + leds(PAPER, "布 🖐️")
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=ifelse(rand3 + ' = ' + slot("0"),
                                         blk("basic", "顯示指示燈 ", slot("✊ 石頭")),
                                         ifelse(rand2 + ' = ' + slot("0"),
                                                blk("basic", "顯示指示燈 ", slot("✌️ 剪刀")),
                                                blk("basic", "顯示指示燈 ", slot("🖐️ 布"))))))
             + look("<b>可以玩了！</b> 搖一搖 → 石頭、剪刀、布<b>隨機出一個</b> ✌️")
             + adult("到這裡就是一個完整的遊戲了，可以先讓他跟你猜個十盤。<br>"
                     "他很可能會發現「怎麼一直出布」——那正好，"
                     "讓他數一數十次裡各出幾次，這是機率的第一課。")) +

        stage("🍬", "加料關", "一關一個小點子，<b>做幾關都可以</b>。")

        + step(8, "加料 ①：出拳前先「預備」",
               '<p>在「如果」的<b>上面</b>加兩塊：<b>顯示圖示</b>（挑一個你喜歡的）'
               '和 <b>暫停 500 毫秒</b>。</p>'
               + prog(blk("basic", "顯示圖示 ", slot("👀")) +
                      blk("basic", "暫停 ", slot("500"), " 毫秒"))
               + look("搖一搖 → 先閃一下，<b>才</b>出拳，比較有儀式感 🥁")
               + '<p class="usedhint">這一關多用到：<b>顯示圖示</b>、<b>暫停</b></p>') +

        step(9, "加料 ②：出拳的時候「叮」一聲",
             '<p>去 <b>音效</b> 抽屜，拿那塊<b>長長的英文積木</b>（第 8 課那塊）。</p>'
             '<p>放在「顯示圖示」的下面，<b>什麼都不用改</b>。</p>'
             + prog(playtone())
             + look("出拳前會「叮」一聲 🔔")
             + adult("這裡刻意不改音名——用預設的就好。"
                     "想換音的話，第 8 課教過：點選單用耳朵挑。")
             + '<p class="usedhint">這一關多用到：<b>play tone</b></p>') +

        step(10, "加料 ③：過幾秒自己擦掉",
             '<p>在帽子的<b>最下面</b>加 <b>暫停 3000 毫秒</b> 和 <b>清空畫面</b>。</p>'
             + prog(blk("basic", "暫停 ", slot("3000"), " 毫秒") +
                    blk("basic", "清空畫面"))
             + look("出拳三秒後畫面<b>自己清乾淨</b>，準備下一局 🔄")
             + '<p class="usedhint">這一關多用到：<b>清空畫面</b></p>') +

        step(11, "加料 ④：想知道玩了幾次嗎？",
             note("📦 這一關會用到<b>變數</b>",
                  "變數就是第 4 課那個<b>記數字的小盒子</b>。<br>"
                  "覺得難就<b>直接跳過</b>——前面十步已經是一個完整的遊戲了 👍")
             + '<p>建立一個盒子叫 <code>n</code>，在 <b>「當啟動時」</b> 裡設為 <code>0</code>。</p>'
             '<p>帽子最上面加 <b>「變數 n 改變 1」</b>，最下面加 <b>「顯示數字 n」</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("n"), " 設為 ", slot("0"))) +
                    blk("var", "變數 ", slot("n"), " 改變 ", slot("1")) +
                    blk("basic", "顯示數字 ", slot("n")))
             + look("每搖一次，數字就<b>多 1</b> 🔢")
             + '<p class="usedhint">這一關多用到：<b>變數</b>、<b>顯示數字</b></p>') +

        tryit("把石頭、剪刀、布<b>換成你自己畫的圖</b>。",
              "跟家人玩十盤，數數看各出了幾次。") +

        uses_section("e1") +

        final("e1", [
            "我做出了一台會出拳的猜拳機",
            "我知道「抽籤」每次給的數字都不一定",
            "我會用「如果…那麼…否則」分出三條路",
        ]) + game_nav("e1")
    )
    write_game("e1", body, "入門遊戲：猜拳機")

# ---- ⚡ 反應王（入門：不用變數、不用座標、不用音名）----
def build_e2():
    rand2 = blk("math", "隨機取數 ", slot("0"), " 到 ", slot("1"))
    yes_i = blk("basic", "顯示圖示 ", slot("✓ 打勾"))
    no_i = blk("basic", "顯示圖示 ", slot("✗ 打叉"))

    body = (
        game_top("e2", "入門遊戲 · 第二個", "⚡ 反應王") +
        goal("⚡", "燈跑到<b>左邊按 A</b>、跑到<b>右邊按 B</b>。看你多快 👀") +

        '<p>這個遊戲也<b>不用盒子（變數）</b>，也<b>不用數格子</b>。</p>'
        + note("👆 玩法：看到燈就<b>按住不放</b>",
               "不是按一下就好，是<b>按著等它給你打勾</b>。<br>"
               "這樣比較好中，手指壓著就對了。") +

        stage("🎮", "基本關", "做完這 10 步，遊戲就<b>可以玩了</b>。")

        + step(1, "開機先說「GO」",
               '<p><b>「當啟動時」</b> 裡放一塊 <b>「顯示文字」</b>，打上 <code>GO</code>。</p>'
               + prog(blk("basic", slot("當啟動時"), hat=True,
                          nest_html=blk("basic", "顯示文字 ", slot("GO"))))
               + look("開機時 <b>GO</b> 跑過畫面 🏁")) +

        step(2, "找到綠色的「重複無限次」",
             '<p>它<b>一開始就在畫面上</b>了，不用去抽屜找。</p>'
             + prog(blk("loop", "重複無限次", hat=True))
             + look("找到那塊綠色的就打勾 ✅")) +

        step(3, "拿出抽籤積木",
             find("math", "隨機取數 0 到 10")
             + '<p>先放在空白處，把 <code>10</code> 改成 <code>1</code>。</p>'
             '<p>這樣它只會抽出 <b>0</b> 或 <b>1</b>——剛好一邊一個。</p>'
             + prog(rand2)
             + look("積木上寫著「隨機取數 <b>0</b> 到 <b>1</b>」。")) +

        step(4, "決定燈要出現在哪一邊",
             find("logic", "如果 … 那麼 … 否則", "（要有<b>「否則」</b>的那塊）")
             + '<p>拖進「重複無限次」裡面。</p>'
             '<p>條件用 <b class="bname">=</b>：左邊塞<b>抽籤積木</b>、右邊打 <code>0</code>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=ifelse(rand2 + ' = ' + slot("0"),
                                         '<div class="plainrow">抽到 0 → 左邊</div>',
                                         '<div class="plainrow">抽到 1 → 右邊</div>')))
             + look("架子搭好了，兩邊都還空空的。")) +

        step(5, "左邊亮起來",
             find("basic", "顯示指示燈")
             + '<p>放進 <b>那麼</b> 裡面，把<b>左邊兩排</b>點亮：</p>'
             + leds(LEFT, "左邊 ⬅️")
             + prog(blk("basic", "顯示指示燈 ", slot("⬅️ 左邊")))
             + look("燈<b>一直</b>在左邊閃，快到看不清楚。下一步修好 👇")) +

        step(6, "讓它停久一點",
             '<p>在「顯示指示燈」的下面加 <b>「暫停 800 毫秒」</b>。</p>'
             + prog(blk("basic", "顯示指示燈 ", slot("⬅️ 左邊")) +
                    blk("basic", "暫停 ", slot("800"), " 毫秒"))
             + look("燈<b>停一下</b>才換，看得清楚了 👀")) +

        step(7, "認識新積木：「按鈕 A 被按下？」",
             find("event", "按鈕 A 被按下？", "（圓圓的那塊，在<b>輸入</b>抽屜）")
             + note("🤔 它跟帽子不一樣",
                    "<b>「當按鈕 A 被按下」</b>是<b>帽子</b>，你一按它就跳出來做事。<br>"
                    "<b>「按鈕 A 被按下？」</b>是<b>問句</b>，它只回答「<b>現在</b>有沒有在按」。")
             + '<p>先拖到空白處，下一步要用。</p>'
             + prog(blk("event", "按鈕 ", slot("A", True), " 被按下？"))
             + look("認得這塊就打勾 ✅")) +

        step(8, "按對了打勾，沒按到打叉",
             '<p>在「暫停」的下面放一塊<b>有「否則」</b>的判斷，'
             '條件就是 <b>「按鈕 A 被按下？」</b>。</p>'
             '<p><b>那麼</b> 放<b>打勾</b>的圖，<b>否則</b> 放<b>打叉</b>的圖。</p>'
             + note("🔍 圖案在選單的哪裡",
                    "打勾那個選單上寫 <code>yes</code>，打叉寫 <code>no</code>。<br>"
                    "看圖挑就好，<b>不用管英文</b>。")
             + prog(ifelse(blk("event", "按鈕 ", slot("A", True), " 被按下？"),
                           yes_i, no_i))
             + look("燈在左邊時<b>按住 A</b> → 打勾 ✓ 沒按 → 打叉 ✗")) +

        step(9, "右邊照做一次",
             '<p><b>否則</b> 那一格做<b>一模一樣</b>的事，只是：</p>'
             '<p>圖案畫<b>右邊兩排</b>、按鈕改成 <b>B</b>。</p>'
             + leds(RIGHT, "右邊 ➡️")
             + prog(blk("basic", "顯示指示燈 ", slot("➡️ 右邊")) +
                    blk("basic", "暫停 ", slot("800"), " 毫秒") +
                    ifelse(blk("event", "按鈕 ", slot("B", True), " 被按下？"),
                           yes_i, no_i))
             + look("燈<b>左右隨機</b>出現，按對的那顆就打勾 ⚡")
             + adult("這一格是把上面三步<b>照抄一遍</b>。<br>"
                     "在 MakeCode 裡可以在積木上<b>按右鍵 → 複製</b>，"
                     "整串一起複製過來再改，比重拖一次快很多。")) +

        step(10, "打完勾就擦掉，準備下一輪",
             '<p>在「重複無限次」的<b>最下面</b>（兩個分支的外面）加：'
             '<b>暫停 600 毫秒</b> 和 <b>清空畫面</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=ifelse(rand2 + ' = ' + slot("0"),
                                         '<div class="plainrow">左邊那一整段</div>',
                                         '<div class="plainrow">右邊那一整段</div>') +
                                  blk("basic", "暫停 ", slot("600"), " 毫秒") +
                                  blk("basic", "清空畫面")))
             + look("<b>可以玩了！</b> 打勾閃一下就換下一題 ⚡")
             + adult("到這裡就是完整的遊戲了。<br>"
                     "如果他老是打叉，把 <code>800</code> 調大一點（例如 1500），"
                     "先讓他有成功經驗，再慢慢調回來。")) +

        stage("🍬", "加料關", "一關一個小點子，<b>做幾關都可以</b>。")

        + step(11, "加料 ①：出現時間不固定，比較刺激",
               '<p>把最後那塊 <b>「暫停 600」</b> 的數字，換成一塊'
               '<b>抽籤積木</b>，範圍改成 <b>300 到 1500</b>。</p>'
               + prog(blk("basic", "暫停 ",
                          blk("math", "隨機取數 ", slot("300"), " 到 ", slot("1500")),
                          " 毫秒"))
               + look("下一題<b>什麼時候來不知道</b>，更緊張了 😆")
               + '<p class="usedhint">這一關多用到：<b>隨機取數</b>（放進別的積木裡）</p>') +

        step(12, "加料 ②：打勾配一聲「叮」",
             '<p>在<b>打勾</b>的圖下面，加一塊<b>音效抽屜那塊長長的英文積木</b>。</p>'
             '<p>音<b>不用改</b>。</p>'
             + prog(yes_i + playtone())
             + look("按對就「叮」🔔 按錯沒聲音，手感差很多")
             + '<p class="usedhint">這一關多用到：<b>play tone</b></p>') +

        step(13, "加料 ③：搖一搖重新開始",
             '<p>拉一頂 <b>「當姿勢 晃動 發生」</b>，裡面放 <b>「顯示文字 GO」</b>。</p>'
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示文字 ", slot("GO"))))
             + look("搖一搖 → 跑出 <b>GO</b>，重新來過 🔄")
             + '<p class="usedhint">這一關多用到：<b>當姿勢 晃動 發生</b></p>') +

        step(14, "加料 ④：想記分數嗎？",
             note("📦 這一關會用到<b>變數</b>",
                  "變數就是第 4 課那個<b>記數字的小盒子</b>。<br>"
                  "覺得難就<b>直接跳過</b>——前面十三步已經是完整的遊戲了 👍")
             + '<p>建立一個盒子叫 <code>score</code>，在 <b>「當啟動時」</b> 裡設為 <code>0</code>。</p>'
             '<p><b>兩個</b>「打勾」的下面都加 <b>「變數 score 改變 1」</b>。</p>'
             '<p>再把「搖一搖」那頂帽子裡加一塊 <b>「顯示數字 score」</b>。</p>'
             + prog(yes_i + blk("var", "變數 ", slot("score"), " 改變 ", slot("1")))
             + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                        nest_html=blk("basic", "顯示數字 ", slot("score")) +
                                  blk("var", "變數 ", slot("score"), " 設為 ", slot("0")) +
                                  blk("basic", "顯示文字 ", slot("GO"))))
             + look("搖一搖 → 先看到<b>這局幾分</b>，再重新開始 🏆")
             + adult("這是變數第一次真的「有用」：不記下來就看不到分數。<br>"
                     "動機出來了再教概念，比第 4 課乾講「盒子」好吸收。")
             + '<p class="usedhint">這一關多用到：<b>變數</b>、<b>顯示數字</b></p>') +

        tryit("把 <code>800</code> 改小，變成超難模式。",
              "左右改成<b>上下</b>（燈畫在最上面一排／最下面一排）。") +

        uses_section("e2") +

        final("e2", [
            "我做出了一個考反應的遊戲",
            "我分得出「當按鈕被按下」（帽子）和「按鈕被按下？」（問句）",
            "我會用「抽籤」讓每次出現的位置都不一樣",
        ]) + game_nav("e2")
    )
    write_game("e2", body, "入門遊戲：反應王")

# ---- ⭐ 接星星 ----
def build_g1():
    star = blk("led", "點亮 x ", slot("sx"), " y ", slot("sy"))
    me = blk("led", "點亮 x ", slot("px"), " y ", slot("4"))

    body = (
        game_top("g1", "101 遊戲 · 第一個", "⭐ 接星星") +
        goal("⭐", "星星從上面掉下來，你在<b>最下面一排</b>左右跑，把它<b>接住</b>。") +

        '<p>畫面最下面那一排是<b>你</b>。</p>'
        '<p>上面掉下來的是<b>星星</b>。</p>'
        '<p>接到 → 加分 ＋「叮」；漏接 → 少一條命 ＋「嗚」。</p>'

        + stage("🎮", "基本關", "做完這 10 步，遊戲就<b>可以玩了</b>。")

        + step(1, "做一個盒子記住你在哪",
               '<p>去 <b>變數</b> 抽屜，建立一個盒子叫 <code>px</code>。</p>'
               '<p>它記的是「你在<b>左右第幾個</b>」。</p>'
               + look("抽屜裡多出寫著 <code>px</code> 的積木。")) +

        step(2, "開機時站在正中間",
             '<p><b>「當啟動時」</b> 裡放 <b>「變數 px 設為 2」</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("px"), " 設為 ", slot("2"))))
             + look("畫面沒變化，是正常的 👍")) +

        step(3, "把你畫出來",
             '<p><b>「重複無限次」</b> 裡放兩塊：先 <b>「清空畫面」</b>，'
             '再 <b>「點亮 x y」</b>。</p>'
             '<p>x 的框框塞圓圓的 <code>px</code>，y 打 <code>4</code>（最下面那排）。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "清空畫面") + me))
             + look("<b>最下面</b>中間有一顆燈亮著，就是你 🔆")
             + leds("....." "\n" "....." "\n" "....." "\n" "....." "\n" "..#..", "這就是你")) +

        step(4, "按 A 往左走",
             '<p>拉一頂 <b>「當按鈕 A 被按下」</b>，裡面放 '
             '<b>「變數 px 改變 -1」</b>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("px"), " 改變 ", slot("-1"))))
             + look("點 A → 那顆燈往<b>左</b>移一格 ⬅️")) +

        step(5, "按 B 往右走",
             '<p>做法一樣，按鈕改成 <b>B</b>，數字改成 <code>1</code>。</p>'
             + prog(blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("px"), " 改變 ", slot("1"))))
             + look("A 往左、B 往右。但一直按會<b>跑出畫面</b> 😅 下一步修好 👇")) +

        step(6, "別讓自己跑出去",
             '<p>在 <b>「重複無限次」</b> 的<b>最上面</b>加兩塊 <b>「如果…那麼」</b>'
             '（<b>沒有</b>「否則」的那塊）。</p>'
             + find("logic", "<", "（第二塊要點選單改成 <b>&gt;</b>）")
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=ifelse(slot("px") + ' &lt; ' + slot("0"),
                                         blk("var", "變數 ", slot("px"), " 設為 ", slot("0"))) +
                                  ifelse(slot("px") + ' &gt; ' + slot("4"),
                                         blk("var", "變數 ", slot("px"), " 設為 ", slot("4")))))
             + look("走到<b>邊邊就停住</b>，不會再不見了 ✋")
             + adult("<code>&lt;</code> 和 <code>&gt;</code> 是<b>同一塊</b>積木，"
                     "點積木上的符號用選單換。孩子常以為要找兩塊不同的。")) +

        step(7, "做星星的兩個盒子",
             '<p>再建立兩個盒子：<code>sx</code>（星星在左右第幾個）、'
             '<code>sy</code>（星星掉到第幾排）。</p>'
             '<p>在 <b>「當啟動時」</b> 裡設定：<code>sy</code> 設為 <code>0</code>，'
             '<code>sx</code> 設為 <b>隨機取數 0 到 4</b>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("var", "變數 ", slot("px"), " 設為 ", slot("2")) +
                                  blk("var", "變數 ", slot("sy"), " 設為 ", slot("0")) +
                                  blk("var", "變數 ", slot("sx"), " 設為 ",
                                      blk("math", "隨機取數 ", slot("0"), " 到 ", slot("4")))))
             + look("還是只看得到你自己。下一步星星才會出現 👇")) +

        step(8, "把星星畫出來，讓它掉下來",
             '<p>在「重複無限次」裡，<b>你的下面</b>再加三塊：</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=me + star +
                                  blk("basic", "暫停 ", slot("400"), " 毫秒") +
                                  blk("var", "變數 ", slot("sy"), " 改變 ", slot("1"))))
             + look("星星從<b>最上面</b>一格一格<b>往下掉</b> ⭐ 掉出去就不見了。")) +

        step(9, "接到了嗎？",
             '<p>在「sy 改變 1」的<b>下面</b>加一塊 <b>「如果…那麼」</b>，'
             '條件是 <b>sy &gt; 4</b>（星星掉出去了，該算帳）。</p>'
             '<p>裡面再放一塊<b>有「否則」</b>的，條件是 <b>sx = px</b>。</p>'
             + prog(ifelse(slot("sy") + ' &gt; ' + slot("4"),
                           ifelse(slot("sx") + ' = ' + slot("px"),
                                  '<div class="plainrow">接到了 → 等一下放</div>',
                                  '<div class="plainrow">漏接了 → 等一下放</div>')))
             + look("架子搭好了，還沒放東西進去。")) +

        step(10, "接到加分，漏接扣命",
             '<p>先再建立兩個盒子：<code>score</code>（分數）和 <code>life</code>（命）。</p>'
             '<p>在「當啟動時」裡 <code>score</code> 設為 <code>0</code>、'
             '<code>life</code> 設為 <code>3</code>。</p>'
             '<p>然後把兩條路填滿：</p>'
             + prog(ifelse(slot("sy") + ' &gt; ' + slot("4"),
                           ifelse(slot("sx") + ' = ' + slot("px"),
                                  blk("var", "變數 ", slot("score"), " 改變 ", slot("1")) +
                                  playtone("高音 C", "1/4 拍"),
                                  blk("var", "變數 ", slot("life"), " 改變 ", slot("-1")) +
                                  playtone("低音 C", "1/4 拍")) +
                           blk("var", "變數 ", slot("sy"), " 設為 ", slot("0")) +
                           blk("var", "變數 ", slot("sx"), " 設為 ",
                               blk("math", "隨機取數 ", slot("0"), " 到 ", slot("4")))))
             + note("⚠️ 最後兩塊要放在<b>外面</b>",
                    "「sy 設為 0」和「sx 設為 隨機」要放在<b>「如果 sy &gt; 4」的裡面</b>、"
                    "但在<b>「否則」的外面</b>——不管接到沒接到，都要放一顆新星星。")
             + look("<b>可以玩了！</b> 接到「叮」⭐ 漏接「嗚」😵")
             + adult("到這裡就是一個完整的遊戲了，可以先停在這裡讓他玩個過癮。<br>"
                     "後面的加料關是「還想加什麼」才做，做幾關都可以。")) +

        stage("🍬", "加料關", "一關一個小點子，<b>做幾關都可以</b>，隨時停下來都算完成。")

        + step(11, "加料 ①：看得到分數",
               '<p>拉一頂 <b>「當姿勢 晃動 發生」</b>，裡面放 '
               '<b>「顯示數字 score」</b>。</p>'
               + prog(blk("event", "當姿勢 ", slot("晃動", True), " 發生", hat=True,
                          nest_html=blk("basic", "顯示數字 ", slot("score"))))
               + look("<b>搖一搖</b> → 跳出現在幾分 🔢")
               + '<p class="usedhint">這一關多用到：<b>當姿勢 晃動 發生</b>、<b>顯示數字</b></p>') +

        step(12, "加料 ②：沒命就結束",
             '<p>在「重複無限次」<b>最下面</b>加一塊 <b>「如果 life &lt; 1 那麼」</b>。</p>'
             '<p>裡面放<b>哭臉</b>、<b>顯示數字 score</b>，再放一塊 '
             '<b>「暫停 2000 毫秒」</b>。</p>'
             + prog(ifelse(slot("life") + ' &lt; ' + slot("1"),
                           blk("basic", "顯示圖示 ", slot("😢")) +
                           blk("basic", "顯示數字 ", slot("score")) +
                           blk("basic", "暫停 ", slot("2000"), " 毫秒")))
             + look("三條命用完 → 哭臉 ＋ 你的分數 😢")
             + '<p class="usedhint">這一關多用到：<b>顯示圖示</b></p>') +

        step(13, "加料 ③：開場說「GO」",
             '<p>在 <b>「當啟動時」</b> 的<b>最上面</b>加一塊 <b>「顯示文字」</b>，'
             '打上 <code>GO</code>。</p>'
             + prog(blk("basic", slot("當啟動時"), hat=True,
                        nest_html=blk("basic", "顯示文字 ", slot("GO"))))
             + look("開機先跑過 <b>GO</b>，再開始掉星星 🏁")
             + '<p class="usedhint">這一關多用到：<b>顯示文字</b></p>') +

        step(14, "加料 ④：開場來個掃描動畫",
             '<p>在 <code>GO</code> 的下面加一塊 '
             '<b>「計次 index 從 0 到 4 執行」</b>（<b>迴圈</b>抽屜）。</p>'
             '<p>裡面放 <b>「點亮 x index y 2」</b> 和 <b>「暫停 100 毫秒」</b>。</p>'
             + prog(blk("loop", "計次 ", slot("index", True), " 從 0 到 ", slot("4"), " 執行",
                        hat=True,
                        nest_html=blk("led", "點亮 x ", slot("index"), " y ", slot("2")) +
                                  blk("basic", "暫停 ", slot("100"), " 毫秒")))
             + look("開機時中間那排燈<b>一顆一顆亮過去</b> ➡️")
             + adult("「計次」就是「從 0 數到 4，每數一次做一遍」。"
                     "它跟第 5 課的「重複 N 次」差別是：計次<b>知道自己數到幾</b>，"
                     "那個數字就放在 <code>index</code> 裡，可以直接拿來用。")
             + '<p class="usedhint">這一關多用到：<b>計次 index 從 0 到 4 執行</b></p>') +

        step(15, "加料 ⑤：畫一張自己的開場圖",
             '<p>在掃描動畫下面加一塊 <b>「顯示指示燈」</b>，點格子畫一顆星星。</p>'
             + prog(blk("basic", "顯示指示燈 ", slot("⭐ 星星")))
             + leds(STAR, "照這樣點")
             + look("開機：星星圖 → 掃描 → GO → 開始玩 ✨")
             + '<p class="usedhint">這一關多用到：<b>顯示指示燈</b></p>') +

        step(16, "加料 ⑥：星星在哪邊？給個提示",
             '<p>覺得太難的話，讓它先<b>用箭頭告訴你</b>星星在左邊還右邊。</p>'
             '<p>在「重複無限次」裡加 <b>「如果 sx &lt; px 那麼」</b> → '
             '<b>顯示箭頭</b> 選<b>西</b>（左）；<b>否則</b> → 選<b>東</b>（右）。</p>'
             + prog(ifelse(slot("sx") + ' &lt; ' + slot("px"),
                           blk("basic", "顯示箭頭 ",
                               '<div class="block b-math">箭頭數字 ' + slot("西") + '</div>'),
                           blk("basic", "顯示箭頭 ",
                               '<div class="block b-math">箭頭數字 ' + slot("東") + '</div>')))
             + note("🧭 箭頭用的是<b>方位</b>", "<b>西</b> 是左邊、<b>東</b> 是右邊。")
             + look("箭頭一直指著星星的方向 🧭（會蓋住畫面，玩過癮就可以拿掉）")
             + '<p class="usedhint">這一關多用到：<b>顯示箭頭</b></p>') +

        step(17, "加料 ⑦：越玩越快",
             '<p>把 <b>「暫停 400 毫秒」</b> 裡的 <code>400</code> 換成一個<b>算式</b>：</p>'
             '<p>去 <b>數學</b> 抽屜拿 <b>減法</b> 和 <b>乘法</b>，拼成 '
             '<b>400 - score × 20</b>。</p>'
             + prog(blk("basic", "暫停 ",
                        blk("math", slot("400"), " - ",
                            blk("math", slot("score"), " × ", slot("20"))),
                        " 毫秒"))
             + look("分數越高，星星掉得<b>越快</b> 🔥")
             + adult("分數很高時這個算式會變成負數，micro:bit 會當成 0（全速）。"
                     "對玩起來沒問題，但如果他問「為什麼不會更快了」，這就是答案。")
             + '<p class="usedhint">這一關多用到：<b>減法</b>、<b>乘法</b></p>') +

        step(18, "加料 ⑧：蓋住就變慢動作",
             '<p>用 <b>光線感測值</b> 做一個「作弊鍵」：手一蓋住板子，星星就掉得慢。</p>'
             '<p>在「重複無限次」裡加 <b>「如果 光線感測值 &lt; 50 那麼」</b> → '
             '<b>暫停 300 毫秒</b>。</p>'
             + prog(ifelse(blk("event", "光線感測值") + ' &lt; ' + slot("50"),
                           blk("basic", "暫停 ", slot("300"), " 毫秒")))
             + look("用手<b>蓋住</b>板子 → 星星慢下來 🐢 放開 → 恢復。")
             + '<p class="usedhint">這一關多用到：<b>光線感測值</b></p>') +

        step(19, "加料 ⑨：破 10 分放煙火",
             '<p>在「接到了」那一條路裡，加 <b>「如果 score = 10 那麼」</b>。</p>'
             '<p>裡面放 <b>「重複 5 次 執行」</b>，'
             '裡面再放<b>笑臉</b>、<b>暫停 100</b>、<b>清空畫面</b>、<b>暫停 100</b>。</p>'
             + prog(ifelse(slot("score") + ' = ' + slot("10"),
                           blk("loop", "重複 ", slot("5"), " 次 執行",
                               nest_html=blk("basic", "顯示圖示 ", slot("😀")) +
                                         blk("basic", "暫停 ", slot("100"), " 毫秒") +
                                         blk("basic", "清空畫面") +
                                         blk("basic", "暫停 ", slot("100"), " 毫秒"))))
             + look("接到第 10 顆星星 → 笑臉<b>閃五下</b>慶祝 🎉")
             + '<p class="usedhint">這一關多用到：<b>重複 N 次 執行</b></p>') +

        tryit("把 <code>life</code> 從 <b>3</b> 改成 <b>1</b>，變成超難模式。",
              "把星星改成<b>兩顆</b>（再做一組 <code>sx2</code>、<code>sy2</code>）。") +

        uses_section("g1") +

        final("g1", [
            "我做出了一個真的能玩的遊戲",
            "我知道 px、sx、sy 各自記住什麼",
            "我會用「如果…那麼…否則」判斷接到沒接到",
        ]) + game_nav("g1")
    )
    write_game("g1", body, "101 遊戲：接星星")

# ---- 🔨 打地鼠 ----
def build_g2():
    body = (
        game_top("g2", "101 遊戲 · 第二個", "🔨 打地鼠") +
        goal("🔨", "地鼠隨機冒出來。在<b>左邊</b>就按 <b>A</b>，在<b>右邊</b>就按 <b>B</b>。") +

        '<p>這個遊戲跟接星星<b>寫法不一樣</b>。</p>'
        '<p>接星星是「一直畫、一直動」；打地鼠是「<b>等你按</b>，時間到就算了」。</p>'

        + stage("🎮", "基本關", "做完這 8 步，遊戲就<b>可以玩了</b>。")

        + step(1, "做地鼠的盒子",
               '<p>建立兩個盒子：<code>mx</code>（地鼠在左右第幾個）、'
               '<code>score</code>（分數）。</p>'
               '<p>在 <b>「當啟動時」</b> 裡把 <code>score</code> 設為 <code>0</code>。</p>'
               + look("抽屜裡多出 <code>mx</code> 和 <code>score</code>。")) +

        step(2, "讓地鼠隨機冒出來",
             '<p>在 <b>「重複無限次」</b> 裡放：<b>清空畫面</b>，'
             '再把 <code>mx</code> 設為 <b>隨機取數 0 到 4</b>。</p>'
             + prog(blk("loop", "重複無限次", hat=True,
                        nest_html=blk("basic", "清空畫面") +
                                  blk("var", "變數 ", slot("mx"), " 設為 ",
                                      blk("math", "隨機取數 ", slot("0"), " 到 ", slot("4")))))
             + look("畫面還是黑的——盒子換了數字，但還沒畫出來。")) +

        step(3, "把地鼠點亮",
             find("led", "點亮 x 0 y 0")
             + '<p>x 塞圓圓的 <code>mx</code>，y 打 <code>2</code>（中間那排）。</p>'
             + prog(blk("led", "點亮 x ", slot("mx"), " y ", slot("2")))
             + look("中間那排<b>一直有一顆燈在亂跳</b> 🐹")) +

        step(4, "讓它停久一點",
             '<p>下面加一塊 <b>「暫停 800 毫秒」</b>，給你時間反應。</p>'
             + prog(blk("basic", "暫停 ", slot("800"), " 毫秒"))
             + look("地鼠<b>停一下</b>才換位置，看得清楚了 👀")) +

        step(5, "問問看你有沒有在按 A",
             find("event", "按鈕 A 被按下？", "（圓圓的那塊，在<b>輸入</b>抽屜）")
             + note("🤔 這塊跟帽子不一樣",
                    "<b>「當按鈕 A 被按下」</b>是帽子，你一按它就跳出來做事。<br>"
                    "<b>「按鈕 A 被按下？」</b>是<b>問句</b>，它只回答「現在有沒有在按」。")
             + '<p>先拖到空白處放著，下一步要用。</p>'
             + prog(blk("event", "按鈕 ", slot("A", True), " 被按下？"))
             + look("認得這塊就打勾 ✅")
             + adult("這是這個遊戲的重點：<b>事件</b>（等你按）和<b>詢問</b>（現在按著嗎）"
                     "是兩種不同的做法。<br>"
                     "打地鼠要在「地鼠出現的那段時間內」檢查，所以用問句比較順。")) +

        step(6, "地鼠在左邊還是右邊？",
             '<p>在「暫停」<b>上面</b>加一塊<b>有「否則」</b>的判斷，'
             '條件是 <b>mx &lt; 2</b>（左半邊）。</p>'
             + prog(ifelse(slot("mx") + ' &lt; ' + slot("2"),
                           '<div class="plainrow">地鼠在左邊 → 要按 A</div>',
                           '<div class="plainrow">地鼠在右邊 → 要按 B</div>'))
             + look("架子搭好了，還沒放東西。")) +

        step(7, "按對了就加分",
             '<p><b>那麼</b>（左邊）裡面放 <b>「如果 按鈕 A 被按下？ 那麼」</b> → '
             '<code>score</code> 改變 1 ＋ 一個<b>高音</b>。</p>'
             '<p><b>否則</b>（右邊）一樣，但改成 <b>按鈕 B 被按下？</b>。</p>'
             + prog(ifelse(slot("mx") + ' &lt; ' + slot("2"),
                           ifelse(blk("event", "按鈕 ", slot("A", True), " 被按下？"),
                                  blk("var", "變數 ", slot("score"), " 改變 ", slot("1")) +
                                  playtone("高音 C", "1/4 拍")),
                           ifelse(blk("event", "按鈕 ", slot("B", True), " 被按下？"),
                                  blk("var", "變數 ", slot("score"), " 改變 ", slot("1")) +
                                  playtone("高音 C", "1/4 拍"))))
             + note("👆 要<b>按著不放</b>",
                    "地鼠出現的<b>那一瞬間</b>要正在按著，它才數得到。<br>"
                    "所以玩的時候手指<b>壓著</b>比較好中。")
             + look("<b>可以玩了！</b> 按對 → 「叮」🔨")) +

        step(8, "看分數",
             '<p>在「重複無限次」<b>最下面</b>加一塊 <b>「顯示數字 score」</b>，'
             '再加 <b>「暫停 300 毫秒」</b>。</p>'
             + prog(blk("basic", "顯示數字 ", slot("score")) +
                    blk("basic", "暫停 ", slot("300"), " 毫秒"))
             + look("每打完一隻，畫面會<b>閃一下分數</b> 🔢")
             + adult("到這裡遊戲就完整了。後面的加料關可做可不做。")) +

        stage("🍬", "加料關", "一關一個小點子，<b>做幾關都可以</b>。")

        + step(9, "加料 ①：地鼠會閃，比較好認",
               find("led", "點的狀態切換 x 0 y 0")
               + '<p>用它做「亮 → 暗 → 亮」，地鼠就會<b>閃</b>。</p>'
               '<p>在「點亮」下面放：<b>暫停 200</b>、<b>點的狀態切換 x mx y 2</b>、'
               '<b>暫停 200</b>、再一塊<b>點的狀態切換</b>。</p>'
               + prog(blk("led", "點亮 x ", slot("mx"), " y ", slot("2")) +
                      blk("basic", "暫停 ", slot("200"), " 毫秒") +
                      blk("led", "點的狀態切換 x ", slot("mx"), " y ", slot("2")) +
                      blk("basic", "暫停 ", slot("200"), " 毫秒") +
                      blk("led", "點的狀態切換 x ", slot("mx"), " y ", slot("2")))
               + look("地鼠會<b>一閃一閃</b> ✨")
               + '<p class="usedhint">這一關多用到：<b>點的狀態切換 x y</b></p>') +

        step(10, "加料 ②：打完就把它熄掉",
             find("led", "不點亮 x 0 y 0")
             + '<p>在「按對了加分」的裡面，加一塊 <b>「不點亮 x mx y 2」</b>。</p>'
             + prog(blk("led", "不點亮 x ", slot("mx"), " y ", slot("2")))
             + look("打中的<b>那一瞬間</b>地鼠就消失了，手感好很多 🔨")
             + '<p class="usedhint">這一關多用到：<b>不點亮 x y</b></p>') +

        step(11, "加料 ③：沒按到就「嗚」一聲",
             '<p>給「如果 按鈕 A 被按下？」加上 <b>否則</b>，裡面放一個<b>低音</b>。</p>'
             '<p>再放一塊 <b>「rest for 1/4 拍」</b>（音效抽屜），讓聲音之間有空隙。</p>'
             + prog(ifelse(blk("event", "按鈕 ", slot("A", True), " 被按下？"),
                           blk("var", "變數 ", slot("score"), " 改變 ", slot("1")),
                           playtone("低音 C", "1/4 拍") +
                           blk("music", "rest for ", slot("1/4 拍"))))
             + look("沒打到會「嗚」一聲，知道自己漏掉了 😵")
             + '<p class="usedhint">這一關多用到：<b>rest for</b></p>') +

        step(12, "加料 ④：兩顆都沒按才算漏",
             '<p>用 <b>「或」</b>（邏輯抽屜）把兩個問句串起來：</p>'
             '<p><b>「如果 (按鈕 A 被按下？ 或 按鈕 B 被按下？) 那麼」</b> → '
             '表示「你有在按其中一顆」。</p>'
             + prog(ifelse(blk("event", "按鈕 ", slot("A", True), " 被按下？") + ' 或 ' +
                           blk("event", "按鈕 ", slot("B", True), " 被按下？"),
                           '<div class="plainrow">你有按（不管哪一顆）</div>'))
             + tip("🔀 「或」是什麼", "<b>兩邊只要有一邊成立</b>，整句就成立。")
             + look("看得懂就打勾 ✅")
             + '<p class="usedhint">這一關多用到：<b>或</b></p>') +

        step(13, "加料 ⑤：換一種迴圈寫法",
             find("loop", "重複 判斷 false 執行")
             + '<p>把 <b>false</b> 換成 <b>true</b>（邏輯抽屜那塊）。</p>'
             + note("😲 這樣就跟「重複無限次」一樣了",
                    "<b>「重複 判斷 true 執行」</b>＝ 只要條件成立就一直做，"
                    "而 <code>true</code> 永遠成立，所以它<b>永遠不會停</b>。")
             + prog(blk("loop", "重複 判斷 ", slot("true"), " 執行", hat=True,
                        nest_html='<div class="plainrow">跟「重複無限次」做一樣的事</div>'))
             + look("看得懂就打勾 ✅（不用真的換掉，知道有這種寫法就好）")
             + adult("之後要做「命還沒用完就一直玩」這種條件迴圈，用的就是這塊。"
                     "「躲石頭」那個遊戲會真的派上用場。")
             + '<p class="usedhint">這一關多用到：<b>重複 判斷 執行</b>、<b>true</b></p>') +

        step(14, "加料 ⑥：碰金色的孔加分",
             find("event", "當引腳 P0 被按下", "（<b>輸入</b>抽屜）")
             + '<p>拉出來，裡面放 <b>「變數 score 改變 5」</b>。</p>'
             '<p>手捏著 <b>GND</b>，另一手碰 <b>P0</b> → 偷偷加 5 分 😈</p>'
             + prog(blk("event", "當引腳 ", slot("P0", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("score"), " 改變 ", slot("5"))))
             + look("碰一下金色的孔 → 分數<b>跳 5 分</b> 🪙")
             + '<p class="usedhint">這一關多用到：<b>當引腳 P0 被按下</b></p>') +

        step(15, "加料 ⑦：按著金色孔才算數",
             find("event", "引腳 P0 被按下？", "（圓圓的問句）")
             + '<p>跟「按鈕 A 被按下？」一樣是<b>問句</b>。</p>'
             '<p>試試看：<b>「如果 引腳 P0 被按下？ 那麼」</b> → '
             '用 <b>加法</b> 把分數變兩倍：<code>score</code> 設為 <b>score + score</b>。</p>'
             + prog(ifelse(blk("event", "引腳 ", slot("P0", True), " 被按下？"),
                           blk("var", "變數 ", slot("score"), " 設為 ",
                               blk("math", slot("score"), " + ", slot("score")))))
             + look("按著金孔的時候，分數會<b>翻倍</b> 💰")
             + '<p class="usedhint">這一關多用到：<b>引腳 P0 被按下？</b>、<b>加法</b></p>') +

        step(16, "加料 ⑧：把燈調暗一點",
             find("led", "燈光 亮度設為 255")
             + '<p>放進 <b>「當啟動時」</b>，數字改成 <code>80</code>。</p>'
             + prog(blk("led", "燈光 亮度設為 ", slot("80")))
             + look("整片燈變<b>柔和</b>了，晚上玩不刺眼 🌙")
             + '<p class="usedhint">這一關多用到：<b>燈光 亮度設為</b></p>') +

        tryit("把 <code>800</code> 改小，地鼠換得更快、更難打。",
              "改成<b>三個區域</b>：左邊按 A、右邊按 B、正中間<b>兩顆一起按</b>。") +

        uses_section("g2") +

        final("g2", [
            "我做出了打地鼠，按對會加分",
            "我分得出「當按鈕被按下」（帽子）和「按鈕被按下？」（問句）",
            "我知道「重複 判斷 true 執行」跟「重複無限次」是一樣的意思",
        ]) + game_nav("g2")
    )
    write_game("g2", body, "101 遊戲：打地鼠")

# ---- 🪨 躲石頭 ----
def build_g3():
    body = (
        game_top("g3", "101 遊戲 · 第三個", "🪨 躲石頭") +
        goal("🪨", "石頭一直掉下來，左右<b>閃開</b>。活越久，分越高。") +

        '<p>這個遊戲用一招<b>新的</b>：不用比座標，直接問 micro:bit——</p>'
        '<p>「<b>我站的那一格，燈是不是亮著？</b>」亮著就代表<b>撞到</b>了 💥</p>'

        + stage("🎮", "基本關", "做完這 9 步，遊戲就<b>可以玩了</b>。")

        + step(1, "做四個盒子",
               '<p>建立：<code>px</code>（你在哪）、<code>rx</code>（石頭在哪）、'
               '<code>ry</code>（石頭掉到第幾排）、<code>score</code>（分數）。</p>'
               '<p>在 <b>「當啟動時」</b> 裡：<code>px</code> 設 <code>2</code>、'
               '<code>ry</code> 設 <code>0</code>、<code>score</code> 設 <code>0</code>，'
               '<code>rx</code> 設 <b>隨機取數 0 到 4</b>。</p>'
               + look("畫面沒變化，是正常的 👍")) +

        step(2, "用「重複 判斷」當主迴圈",
             find("loop", "重複 判斷 false 執行")
             + '<p>把 <b>false</b> 換成一個判斷：<b>score &lt; 999</b>。</p>'
             + note("🤔 為什麼不用「重複無限次」",
                    "因為等一下<b>撞到石頭時要讓它停下來</b>。<br>"
                    "只要把 <code>score</code> 設成 <code>999</code>，這個迴圈就會自己結束。")
             + prog(blk("loop", "重複 判斷 ", slot("score") + ' &lt; ' + slot("999"),
                        " 執行", hat=True))
             + look("架子搭好了，裡面還空空的。")
             + adult("這是「用一個變數當開關」的入門。<br>"
                     "比起「重複無限次 ＋ 一個 playing 旗標」，"
                     "直接把條件寫在迴圈上，孩子比較看得出「什麼時候會停」。")) +

        step(3, "把石頭畫出來、讓它掉",
             '<p>迴圈裡放：<b>清空畫面</b> → <b>點亮 x rx y ry</b> → '
             '<b>暫停 400 毫秒</b> → <b>ry 改變 1</b>。</p>'
             + prog(blk("loop", "重複 判斷 ", slot("score") + ' &lt; ' + slot("999"),
                        " 執行", hat=True,
                        nest_html=blk("basic", "清空畫面") +
                                  blk("led", "點亮 x ", slot("rx"), " y ", slot("ry")) +
                                  blk("basic", "暫停 ", slot("400"), " 毫秒") +
                                  blk("var", "變數 ", slot("ry"), " 改變 ", slot("1"))))
             + look("一顆石頭從上面<b>掉下來</b> 🪨 掉出去就不見了。")) +

        step(4, "石頭掉完就換一顆新的",
             '<p>加一塊 <b>「如果 ry &gt; 4 那麼」</b>：</p>'
             '<p>裡面 <code>ry</code> 設 <code>0</code>、'
             '<code>rx</code> 設 <b>隨機取數 0 到 4</b>、<code>score</code> 改變 <code>1</code>。</p>'
             + prog(ifelse(slot("ry") + ' &gt; ' + slot("4"),
                           blk("var", "變數 ", slot("ry"), " 設為 ", slot("0")) +
                           blk("var", "變數 ", slot("rx"), " 設為 ",
                               blk("math", "隨機取數 ", slot("0"), " 到 ", slot("4"))) +
                           blk("var", "變數 ", slot("score"), " 改變 ", slot("1"))))
             + look("石頭一顆接一顆<b>不停</b>掉下來 🪨🪨🪨")) +

        step(5, "把你自己畫出來",
             '<p>在「點亮石頭」的<b>下面</b>加 <b>「點亮 x px y 4」</b>。</p>'
             + prog(blk("led", "點亮 x ", slot("px"), " y ", slot("4")))
             + look("最下面多了一顆燈，那是<b>你</b> 🔆")) +

        step(6, "A 往左、B 往右",
             '<p>跟接星星一樣，做兩頂帽子改 <code>px</code>。</p>'
             + prog(blk("event", "當按鈕 ", slot("A", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("px"), " 改變 ", slot("-1"))) +
                    blk("event", "當按鈕 ", slot("B", True), " 被按下", hat=True,
                        nest_html=blk("var", "變數 ", slot("px"), " 改變 ", slot("1"))))
             + look("你可以左右移動了 ⬅️➡️")) +

        step(7, "新招：問它「我這格亮著嗎」",
             find("led", "點的狀態 x 0 y 0", "（圓圓的<b>問句</b>）")
             + note("💥 這就是撞到判定",
                    "石頭先畫、你後畫。<br>"
                    "如果<b>畫你之前</b>那一格<b>已經亮著</b>，就表示石頭在你身上——撞到了。")
             + '<p>先拖到空白處，下一步要用。</p>'
             + prog(blk("led", "點的狀態 x ", slot("px"), " y ", slot("4")))
             + look("認得這塊就打勾 ✅")) +

        step(8, "撞到就停下來",
             '<p>把它放在 <b>「點亮 x px y 4」的上面</b>，配一塊 <b>「如果…那麼」</b>：</p>'
             + prog(ifelse(blk("led", "點的狀態 x ", slot("px"), " y ", slot("4")),
                           blk("basic", "顯示圖示 ", slot("😢")) +
                           blk("var", "變數 ", slot("score"), " 設為 ", slot("999"))))
             + note("⚠️ 順序很重要",
                    "一定要放在<b>「點亮 x px y 4」的上面</b>。<br>"
                    "先問「亮著嗎」，才輪到你把自己畫上去，不然永遠都是亮的。")
             + look("撞到石頭 → 哭臉 😢 遊戲<b>停住</b>了。")
             + adult("這一步最容易錯位。孩子把判斷放到「點亮自己」下面的話，"
                     "遊戲會<b>一開始就結束</b>——因為他自己把那格點亮了。<br>"
                     "看到一開機就哭臉，就是這個原因。")) +

        step(9, "撞到之前活了幾秒？",
             '<p>在「如果撞到」裡，<b>哭臉的上面</b>先放一塊 <b>「顯示數字 score」</b>。</p>'
             + note("💡 用 999 當結束訊號的副作用",
                    "<code>score</code> 被設成 <code>999</code> 之後就不是分數了。<br>"
                    "所以要<b>先秀出來</b>，再設 999。")
             + prog(ifelse(blk("led", "點的狀態 x ", slot("px"), " y ", slot("4")),
                           blk("basic", "顯示數字 ", slot("score")) +
                           blk("basic", "顯示圖示 ", slot("😢")) +
                           blk("var", "變數 ", slot("score"), " 設為 ", slot("999"))))
             + look("<b>可以玩了！</b> 撞到 → 先看到分數，再看到哭臉 😢")) +

        stage("🍬", "加料關", "一關一個小點子，<b>做幾關都可以</b>。")

        + step(10, "加料 ①：撞到的時候長長「嗚——」一聲",
               find("music", "演奏 音階 中音 C", "（<b>短的</b>那塊，中文的）")
               + note("🔊 這次故意用它",
                      "第 8 課說過這塊<b>聲音不會停</b>。<br>"
                      "這裡剛好利用這一點——撞到就一直叫，直到你叫它停。")
               + '<p>音改成 <b>低音 C</b>，放在哭臉<b>前面</b>。</p>'
               + prog(blk("music", "演奏 音階 ", slot("低音 C")))
               + look("撞到 → <b>一直「嗚——」</b>不停 😱 下一關來關掉它。")
               + '<p class="usedhint">這一關多用到：<b>演奏 音階</b></p>') +

        step(11, "加料 ②：兩秒後讓它閉嘴",
             find("music", "停止播放所有音效")
             + '<p>在「演奏 音階」後面放 <b>「暫停 2000 毫秒」</b>，再放這一塊。</p>'
             + prog(blk("music", "演奏 音階 ", slot("低音 C")) +
                    blk("basic", "暫停 ", slot("2000"), " 毫秒") +
                    blk("music", "停止播放所有音效"))
             + look("「嗚——」響兩秒就<b>安靜</b>了 🤫")
             + '<p class="usedhint">這一關多用到：<b>停止播放所有音效</b></p>') +

        step(12, "加料 ③：兩顆石頭一起掉",
             '<p>再做兩個盒子 <code>rx2</code>、<code>ry2</code>，'
             '照第 3、4 步再來一次。</p>'
             '<p>撞到判定不用改——<b>點的狀態</b>本來就不管是哪一顆石頭 😎</p>'
             + prog(blk("led", "點亮 x ", slot("rx"), " y ", slot("ry")) +
                    blk("led", "點亮 x ", slot("rx2"), " y ", slot("ry2")))
             + look("<b>兩顆</b>石頭一起掉，難度直接翻倍 🪨🪨")
             + adult("這一關是在讓他體會「用燈的狀態判定碰撞」的好處："
                     "石頭再多，判斷都只有一塊積木。<br>"
                     "如果是比座標的寫法，每多一顆石頭就要多一組條件。")) +

        step(13, "加料 ④：越熱掉越快",
             find("event", "溫度感測值 (°C)")
             + '<p>把 <b>「暫停 400」</b> 的數字換成 <b>400 - 溫度感測值 × 5</b>。</p>'
             + prog(blk("basic", "暫停 ",
                        blk("math", slot("400"), " - ",
                            blk("math", blk("event", "溫度感測值 (°C)"), " × ", slot("5"))),
                        " 毫秒"))
             + look("<b>手握住板子</b>暖一下 → 石頭掉得更快 🔥")
             + adult("室溫大概 25 度，所以暫停約 275 毫秒。手握住會升到 30 度以上，"
                     "掉得明顯更快。這是把感測器接上遊戲難度的第一步。")
             + '<p class="usedhint">這一關多用到：<b>溫度感測值</b></p>') +

        step(14, "加料 ⑤：兩台連線，比誰活得久（先講暗號）",
             find("radio", "廣播群組設為 1")
             + '<p>放進 <b>「當啟動時」</b>，數字保持 <code>1</code>。</p>'
             + prog(blk("radio", "廣播群組設為 ", slot("1")))
             + look("畫面上出現<b>兩台</b>假的 micro:bit 了！")
             + '<p class="usedhint">這一關多用到：<b>廣播群組設為</b></p>') +

        step(15, "加料 ⑥：死掉就把分數喊出去",
             find("radio", "廣播發送數字 0")
             + '<p>放在「如果撞到」裡面，數字框塞圓圓的 <code>score</code>。</p>'
             + note("⏰ 要放在設成 999 <b>之前</b>", "不然傳出去的會是 999。")
             + prog(blk("radio", "廣播發送數字 ", slot("score")))
             + look("其中一台撞到 → 另一台<b>收到</b>了（下一關才看得到）📡")
             + '<p class="usedhint">這一關多用到：<b>廣播發送數字</b></p>') +

        step(16, "加料 ⑦：收到對手的分數就比一比",
             find("radio", "當收到廣播數字 receivedNumber", "（一頂<b>帽子</b>）")
             + '<p>裡面放 <b>「如果 score &gt; receivedNumber 那麼」</b> → '
             '<b>顯示文字 WIN</b>，<b>否則</b> → <b>顯示文字 LOSE</b>。</p>'
             + prog(blk("radio", "當收到廣播數字 ", slot("receivedNumber", True), hat=True,
                        nest_html=ifelse(slot("score") + ' &gt; ' + slot("receivedNumber"),
                                         blk("basic", "顯示文字 ", slot("WIN")),
                                         blk("basic", "顯示文字 ", slot("LOSE")))))
             + look("兩台比分數，贏的那台跑出 <b>WIN</b> 🏆")
             + '<p class="usedhint">這一關多用到：<b>當收到廣播數字</b></p>') +

        step(17, "加料 ⑧：用文字喊話",
             find("radio", "廣播發送文字")
             + '<p>撞到的時候，除了送分數，再送一句 <code>DEAD</code>。</p>'
             + prog(blk("radio", "廣播發送文字 ", slot("DEAD")))
             + look("送出去了，但還沒人在聽。下一關 👇")
             + '<p class="usedhint">這一關多用到：<b>廣播發送文字</b></p>') +

        step(18, "加料 ⑨：聽到對手掛了就慶祝",
             find("radio", "當收到廣播文字 receivedString", "（一頂<b>帽子</b>）")
             + '<p>裡面放 <b>「重複 3 次 執行」</b>，'
             '裡面放<b>笑臉</b>、<b>暫停 200</b>、<b>清空畫面</b>、<b>暫停 200</b>。</p>'
             + prog(blk("radio", "當收到廣播文字 ", slot("receivedString", True), hat=True,
                        nest_html=blk("loop", "重複 ", slot("3"), " 次 執行",
                                      nest_html=blk("basic", "顯示圖示 ", slot("😀")) +
                                                blk("basic", "暫停 ", slot("200"), " 毫秒") +
                                                blk("basic", "清空畫面") +
                                                blk("basic", "暫停 ", slot("200"), " 毫秒"))))
             + look("對手一撞到，你這台就<b>笑臉閃三下</b> 😀🎉")
             + '<p class="usedhint">這一關多用到：<b>當收到廣播文字</b>、<b>重複 N 次 執行</b></p>') +

        step(19, "加料 ⑩：石頭剛好砸在你頭上才算",
             '<p>用 <b>「且」</b>（邏輯抽屜）寫另一種撞到判定：</p>'
             '<p><b>「如果 (ry = 4 且 rx = px) 那麼」</b> → 撞到。</p>'
             + prog(ifelse(slot("ry") + ' = ' + slot("4") + ' 且 ' +
                           slot("rx") + ' = ' + slot("px"),
                           blk("basic", "顯示圖示 ", slot("😢"))))
             + tip("🔗 「且」是什麼", "<b>兩邊都要成立</b>，整句才成立。")
             + look("看得懂就打勾 ✅")
             + adult("這是跟第 7 步「點的狀態」<b>完全不同</b>的解法，結果一樣。<br>"
                     "值得問他：「兩顆石頭的時候，哪一種寫起來比較短？」"
                     "答案是「點的狀態」——這就是選對工具的價值。")
             + '<p class="usedhint">這一關多用到：<b>且</b></p>') +

        tryit("把石頭改成<b>三顆</b>。",
              "讓石頭<b>每掉一顆就加快一點</b>（用第一個遊戲的算式）。") +

        uses_section("g3") +

        final("g3", [
            "我會用「點的狀態」問某一格燈亮不亮，拿來判斷撞到",
            "我知道「重複 判斷 執行」可以自己停下來",
            "我讓兩台 micro:bit 比了分數",
        ]) +

        '<div class="goal win final-win"><div class="big">🏆</div><div>'
        '<h3>進階的三個都做完了，你真的會做遊戲了！</h3>'
        '<p>接星星、打地鼠、躲石頭——三種完全不一樣的玩法，'
        '你都用同一盒積木拼出來了。<br>'
        '接下來最好玩的是：<b>想一個沒有人做過的遊戲</b>，然後把它拼出來 🌟</p></div></div>'

        + game_nav("g3")
    )
    write_game("g3", body, "101 遊戲：躲石頭")

def main():
    # 先檢查遊戲宣告的 uses 都對得上 BLOCKS，對不上就直接失敗，
    # 免得教材寫「用了某塊」但實際沒有那塊積木。
    ids = {b["id"] for b in BLOCKS}
    for g in GAMES:
        bad = [u for u in g["uses"] if u not in ids]
        assert not bad, f"{g['id']} 的 uses 有不存在的積木 id：{bad}"
    build_index()
    build_blocks()
    build_games_hub()
    build_e1(); build_e2()
    build_g1(); build_g2(); build_g3()
    build_l0(); build_l1(); build_l2(); build_l3(); build_l4(); build_l5(); build_l6()
    build_l7(); build_l8(); build_l9(); build_l10(); build_l11(); build_l12()
    opened = [L['id'] for L in LESSONS if L['status'] == 'open']
    print("已生成：index.html, blocks.html, 101.html, "
          + "/".join(g["id"] for g in GAMES) + ".html, "
          + ", ".join(f"{i}.html" for i in opened))
    print(f"開放課程（{len(opened)}）：{opened}")
    per = {c: sum(1 for b in BLOCKS if b['cat'] == c) for c in DEX_CATS}
    print(f"積木圖鑑（{len(BLOCKS)} 塊）：" + "、".join(f"{DRAWER[c][0]} {n}" for c, n in per.items()))
    cov = covered_ids()
    miss = [b["id"] for b in BLOCKS if b["id"] not in cov]
    print(f"遊戲積木涵蓋率：{len(cov)} / {len(BLOCKS)}"
          + ("（未使用：" + "、".join(miss) + "）" if miss else "（全數用到）"))
    for g in GAMES:
        print(f"  {g['id']} {g['title']}：{len(set(g['uses']))} 塊")

if __name__ == "__main__":
    main()
