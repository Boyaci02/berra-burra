#!/usr/bin/env python3
"""Dripp'n Burgers menyskärmar: en liggande (1920x1080, alla burgare) och en stående
(1080x1920, snacks, sides, efterrätter). Skriver webb/skarm.html och allt spelaren behöver.

    python3 bygg.py 2026-09-21-1

Samma upplägg som Berlin Kebab och Fluffy House: all rörelse styrs av EN tid via
window.sattTid(T), så varje bildruta går att rendera exakt och skärmarna går i takt.
Priser och rätter kommer från Qoplas meny för "äta här" (qopla/raw.json, hämtad 21/9 2026).

Tizen-regler (Samsung QM-skärmarnas webbläsare): bara transform och opacity i rörelse,
inget inset, ingen fristående translate, ingen clip-path, inget aspect-ratio, ingen flex-gap.
Därför är allt absolut placerat med mått som räknas ut här.
"""
import html
import json
import os
import shutil
import sys

VERSION = sys.argv[1] if len(sys.argv) > 1 else "lokal"
HAR = os.path.dirname(os.path.abspath(__file__))
WEBB = os.path.join(HAR, "webb")

GULD, SVART, KRAM, ROD = "#ECCC74", "#0A0A0A", "#FEFCF2", "#591202"

# (bild, namn, pris, innehåll, märke). ai=True betyder platshållarbild som ska bytas mot riktigt foto.
BURGARE = [
    ("special", "Special", 125, "Cheddar, auberginemajo, silverlök, rostad lök och rostad aubergine", "Årets specialburgare 2025", False),
    ("original", "Original", 125, "Cheddar, originaldressing, silverlök, saltgurka och krispsallad", "", False),
    ("cheese", "Cheese", 125, "Trippel cheddar, ketchup, senap och krispsallad", "", False),
    ("tryffel", "Tryffel", 130, "Cheddar, tryffelmajo, karamelliserad lök, bacon och krispsallad", "", False),
    ("bbq", "BBQ", 130, "Cheddar, smokey bbq-sås, majonnäs, saltgurka, karamelliserad lök och bacon", "", False),
    ("hot-chilli", "Hot Chilli", 125, "Pepper jack, jalapeñodressing, färsk chili, lök och krispsallad", "Stark", False),
    ("chipotle", "Chipotle", 125, "Cheddar, chipotledressing, saltgurka, silverlök och krispsallad", "", False),
    ("tropical", "Tropical", 130, "Cheddar, majonnäs, picklad rödlök, jalapeño, saltgurka och tortillachips", "", True),
    ("combo", "Combo", 125, "En köttpuck och halloumi, cheddar, garlicdressing, silverlök och saltgurka", "", True),
    ("crispy-chicken", "Crispy Chicken", 130, "Parmesan, chipotledressing, tomat, silverlök och krispsallad", "Kyckling", False),
    ("halloumi", "Halloumi", 125, "Chipotledressing, picklad rödlök, saltgurka, tomat och krispsallad", "Vegetarisk", False),
    ("vegan", "Vegan", 129, "Vegansk ost, ajvarmajo, saltgurka, silverlök och krispsallad", "Vegansk", False),
]
SNACKS = [
    ("dirty-fries", "Dirty Fries", 85, "Smält cheddar, färsk chili, lök och jalapeño", False),
    ("hot-wings", "Hot Wings", 79, "I tigersås, med blue cheese-dip och selleri", False),
    ("halloumi-sticks", "Halloumi Sticks", 69, "Serveras med tahiniyoghurt", True),
    ("nachos", "Nachos", 75, "Med gräddfil och salsa", True),
]
SIDES = [
    ("pommes", "Pommes", 39, "", False),
    ("sotpotatis", "Sötpotatis", 69, "", False),
    ("lokringar", "Lökringar", 49, "4 st", False),
    ("mozzarella", "Mozzarella Sticks", 49, "4 st", False),
    ("nuggets", "Chicken Nuggets", 49, "4 st", False),
    ("chilli-cheese", "Chilli Cheese", 49, "4 st", True),
]
SIDES_TEXT = [("Chicken Sticks, 4 st", 59), ("Sallad", 59)]
DIPPAR = "Auberginemajo · Garlicmajo · Bearnaise · Original · Jalapeño · Chipotle · Tryffel · Cheddar · Salsa"
EFTER = [
    ("vaffla", "Nutella Våffla", 85, "Jordgubbar eller banan", True),
    ("pistage", "Pistage Baklawaglass", 69, "Pistagekräm, krossad pistage", True),
    ("glass", "Glass", 49, "3 kulor, choklad eller vanilj", True),
    ("milkshake", "Milkshake", 69, "", True),
]
EFTER_TEXT = [("Husets dessert, med pistagekräm", 85), ("Pistage baklawaglass i bröd", 99)]

e = html.escape


MATT = json.load(open(os.path.join(HAR, "assets", "a-matt.json")))
BEIGE, BLACK, PRISROD = "#EFE4CF", "#15110C", "#9A1B0C"

# Hjältar: tre gånger per varv glider en guldpanel ner över hela skärmen med EN rätt i jätteformat.
HJALTAR_1 = [("special", "Special", 125, "Årets specialburgare 2025"), ("tryffel", "Tryffel", 130, "Tryffelmajo, bacon, karamelliserad lök"), ("crispy-chicken", "Crispy Chicken", 130, "Krispig kyckling, parmesan, chipotle")]
HJALTAR_2 = [("dirty-fries", "Dirty Fries", 85, "Smält cheddar, chili och jalapeño"), ("hot-wings", "Hot Wings", 79, "I tigersås med blue cheese-dip"), ("vaffla", "Nutella Våffla", 85, "Med jordgubbar eller banan")]


def stjarna(d, fyll, klass="stj"):
    """Taggig prisbricka som SVG-polygon (ingen clip-path, Tizen tål den inte)."""
    import math
    n, r1, r2, c = 14, d / 2, d / 2 * 0.86, d / 2
    p = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / n
        p.append(f"{c + r * math.sin(a):.1f},{c - r * math.cos(a):.1f}")
    return f'<svg class="{klass}" width="{d}" height="{d}" viewBox="0 0 {d} {d}"><polygon points="{" ".join(p)}" fill="{fyll}"/></svg>'


def bildruta(bild, bx, by, bw, bh, klass="bild"):
    """Placerar bilden så att SJÄLVA RÄTTEN fyller rutan och står centrerad. Skuggan får sticka ut utanför."""
    m = MATT[bild]; W, H = m["w"], m["h"]; x0, y0, x1, y1 = m["ratt"]
    k = min(bw / ((x1 - x0) * W), bh / ((y1 - y0) * H))
    iw, ih = W * k, H * k
    left = bx + (bw - (x1 - x0) * iw) / 2 - x0 * iw
    top = by + (bh - (y1 - y0) * ih) / 2 - y0 * ih
    ox = (x0 + x1) / 2 * 100; oy = (y0 + y1) / 2 * 100
    return (f'<div class="{klass}" style="left:{left:.1f}px;top:{top:.1f}px;width:{iw:.1f}px;height:{ih:.1f}px;transform-origin:{ox:.1f}% {oy:.1f}%">'
            f'<img src="/assets/a-{bild}.webp" alt=""></div>')


def ratt(i, grupp, bild, namn, pris, text, x, y, w, h, bildw, vanster, namnpx, textpx, bricka, marke=""):
    """En rätt i sicksack: bilden till vänster eller höger, texten på andra sidan, prisbrickan i bildens ytterhörn."""
    tw = w - bildw - 18
    bx = 0 if vanster else w - bildw
    tx = bildw + 18 if vanster else 0
    just = "left" if vanster else "right"
    brx = (bx + bildw - bricka + 6) if vanster else (bx - 6)
    m = f'<b class="marke">{e(marke)}</b>' if marke else ""
    return (f'<div class="ratt {grupp}" data-i="{i}" data-v="{1 if vanster else 0}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            + bildruta(bild, bx, 4, bildw, h - 8)
            + f'<div class="bricka" style="left:{brx}px;top:-4px;width:{bricka}px;height:{bricka}px">{stjarna(bricka, BLACK)}'
              f'<span style="font-size:{int(bricka * .40)}px;line-height:{bricka}px">{pris}<small>kr</small></span></div>'
            + f'<div class="txt" style="left:{tx}px;top:0;width:{tw}px;height:{h}px;text-align:{just}">'
              f'<div class="mitt">{m}<h3 style="font-size:{namnpx}px">{e(namn)}</h3>'
            + (f'<p style="font-size:{textpx}px">{e(text)}</p>' if text else "")
            + "</div></div></div>")


def hjalte(nr, grupp, lista, W, H, stor):
    ut = []
    for k, (bild, namn, pris, rad) in enumerate(lista):
        bw = int(W * (.50 if W > H else .86)); bh = int(H * (.62 if W > H else .40))
        bx = int(W * .46) if W > H else int((W - bw) / 2); by = int(H * .16) if W > H else int(H * .34)
        tx = int(W * .06); ty = int(H * .28) if W > H else int(H * .08)
        d = int(stor * 1.5)
        brx = (bx + bw - d + 20) if W > H else (W - d - 60); bry = (by - 30) if W > H else int(H * .30)
        ut.append(f'<div class="hj {grupp}" data-k="{k}" style="width:{W}px;height:{H}px">'
                  f'<div class="hjpanel" style="width:{W}px;height:{H}px"></div>' + droppar(W, H, 5 + k)
                  + f'<div class="hjtxt" style="left:{tx}px;top:{ty}px;width:{int(W * (.44 if W > H else .88))}px">'
                    f'<b class="hjrad">Dripp\'n</b><h2 style="font-size:{stor}px">{e(namn)}</h2><p style="font-size:{int(stor * .17)}px">{e(rad)}</p></div>'
                  + bildruta(bild, bx, by, bw, bh, "hjbild")
                  + f'<div class="hjbricka" style="left:{brx}px;top:{bry}px;width:{d}px;height:{d}px">{stjarna(d, BLACK)}'
                    f'<span style="font-size:{int(d * .40)}px;line-height:{d}px">{pris}<small>kr</small></span></div></div>')
    return "".join(ut)


def droppar(W, H, seed):
    """Guldpanelens underkant droppar: egna divar under panelen, skalas i höjdled."""
    ut, x, i = [], 10, 0
    while x < W - 30:
        r = (seed * 9301 + i * 49297) % 233280 / 233280.0
        r2 = (seed * 7919 + i * 104729) % 199933 / 199933.0
        w = 30 + int(r * 44); h = 40 + int(r2 * 150)
        ut.append(f'<i class="hjdr" data-f="{r:.3f}" style="left:{x}px;top:{H - 4}px;width:{w}px;height:{h}px;border-radius:0 0 {w // 2}px {w // 2}px"></i>')
        x += w + 30 + int(r2 * 120); i += 1
    return "".join(ut)


def liggande():
    ut = ['<section class="skarm" id="s1" style="left:0;top:0;width:1920px;height:1080px">',
          '<h1 class="rubrik r1" style="left:60px;top:30px;font-size:118px">Burgare</h1>',
          '<div class="under u1" style="left:548px;top:60px"><b class="piller">Pommes ingår</b><span>2 × 80 g smashat kött · glutenfritt bröd finns</span></div>',
          '<img class="logga l1" src="/assets/logga-svart.png" alt="Dripp\'n Burgers" style="left:1590px;top:34px;width:270px">',
          '<i class="linje" style="left:650px;top:190px;height:850px"></i><i class="linje" style="left:1269px;top:190px;height:850px"></i>']
    kolx, w, h, y0 = [60, 680, 1299], 561, 210, 186
    for i, (bild, namn, pris, text, marke, ai) in enumerate(BURGARE):
        kol, rad = i // 4, i % 4                      # fyll spalt för spalt, som förlagan
        ut.append(ratt(i, "g1", bild, namn, pris, text, kolx[kol], y0 + rad * 218, w, h, 262, (rad + kol) % 2 == 0, 35, 16, 96, marke))
    ut.append(hjalte(1, "h1", HJALTAR_1, 1920, 1080, 230))
    ut.append("</section>")
    return "".join(ut)


SCENFARG = [(253, 237, 212), (253, 235, 207), (247, 229, 202)]

SCENER = [
    ("scen-1", "Dripp'n", ["Snacks"], [
        [("Dirty Fries", 85, "Smält cheddar, chili, lök och jalapeño"), ("Hot Wings", 79, "I tigersås, med blue cheese-dip"), ("Halloumi Sticks", 69, "Med tahiniyoghurt"), ("Nachos", 75, "Med gräddfil och salsa")]], ""),
    ("scen-2", "Dripp'n", ["Sides"], [
        [("Pommes", 39, ""), ("Sötpotatis", 69, ""), ("Lökringar", 49, "4 st"), ("Mozzarella Sticks", 49, "4 st")],
        [("Chicken Nuggets", 49, "4 st"), ("Chilli Cheese", 49, "4 st"), ("Chicken Sticks", 59, "4 st"), ("Sallad", 59, "")]],
        "Dipsåser 15 kr · " + DIPPAR),
    ("scen-3", "Dripp'n", ["Efterrätt", "& shakes"], [
        [("Nutella Våffla", 85, "Jordgubbar eller banan"), ("Pistage Baklawaglass", 69, "Pistagekräm, krossad pistage"), ("Baklawaglass i bröd", 99, "Pistagekräm, krossad baklawa")],
        [("Husets Dessert", 85, "Med pistagekräm"), ("Glass", 49, "3 kulor, choklad eller vanilj"), ("Milkshake", 69, "")]], ""),
]


def staende():
    X = 1920
    ut = [f'<section class="skarm" id="s2" style="left:{X}px;top:0;width:1080px;height:1920px">']
    for k, (bild, kick, rubrik, spalter, fot) in enumerate(SCENER):
        ut.append(f'<div class="scen" data-k="{k}" style="width:1080px;height:1920px">'
                  f'<div class="scenbild" style="width:1080px;height:1920px"><img src="/assets/{bild}.webp" alt=""></div>')
        stor = 190 if len(rubrik) == 1 else 150
        ut.append(f'<div class="scenrub" style="left:60px;top:70px;width:960px"><b class="hjrad">{e(kick)}</b>'
                  + "".join(f'<h2 class="srad" style="font-size:{stor if ri == 0 else 84}px">{e(r)}</h2>' for ri, r in enumerate(rubrik)) + "</div>")
        ut.append('<img class="logga sl" src="/assets/logga-svart.png" alt="" style="left:790px;top:78px;width:230px">')
        n = max(len(s) for s in spalter); radh = 116 if len(spalter) == 1 else 106
        y0 = 1920 - 70 - (40 if fot else 0) - n * radh
        # mjuk platta i scenens egen bottenfärg bakom listan, så ingen rad hamnar på papper eller mat
        r_, g_, b_ = SCENFARG[k]
        by = y0 - 150
        ut.append(f'<i class="sband" style="top:{by}px;width:1080px;height:{1920 - by}px;background:linear-gradient(to bottom,rgba({r_},{g_},{b_},0) 0px,rgba({r_},{g_},{b_},.93) 120px,rgb({r_},{g_},{b_}) 170px)"></i>')
        bredd = 960 if len(spalter) == 1 else 462
        for si, spalt in enumerate(spalter):
            for ri, (namn, pris, text) in enumerate(spalt):
                x = 60 + si * 498; y = y0 + ri * radh
                px = 66 if len(spalter) == 1 else 42
                ut.append(f'<div class="prad" style="left:{x}px;top:{y}px;width:{bredd}px;height:{radh}px">'
                          f'<h3 style="font-size:{px}px">{e(namn)}</h3><span class="ppris" style="font-size:{px}px">{pris}<small>kr</small></span>'
                          + (f'<p style="top:{int(px * 1.12)}px;font-size:{22 if len(spalter) == 1 else 17}px">{e(text)}</p>' if text else "")
                          + f'<i class="pstreck" style="top:{radh - 8}px;width:{bredd}px"></i></div>')
        if fot:
            ut.append(f'<div class="sfot" style="left:60px;top:{1920 - 92}px;width:960px">{e(fot)}</div>')
        ut.append("</div>")
    ut.append('<div class="byte" style="width:1080px;height:1920px"><div class="hjpanel" style="width:1080px;height:1920px"></div>' + droppar(1080, 1920, 23)
              + '<img class="bytlogga" src="/assets/logga-svart.png" alt="" style="left:240px;top:840px;width:600px"></div>')
    ut.append("</section>")
    return "".join(ut)


CSS = """
:root{--guld:%(GULD)s;--svart:%(BLACK)s;--beige:%(BEIGE)s;--rod:%(PRISROD)s}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:3000px;height:1920px;overflow:hidden;background:#000}
body{font-family:"Inter","Helvetica Neue",Arial,sans-serif;color:var(--svart)}
#yta{position:absolute;left:0;top:0;width:3000px;height:1920px;transform-origin:0 0}
.skarm{position:absolute;overflow:hidden;background:var(--beige);background-image:radial-gradient(ellipse at 50%% 45%%,#F8F0DF 0%%,#EFE4CF 58%%,#E6D8BE 100%%)}
h1,h2,h3,.piller,.marke,.bricka span,.hjbricka span,.hjrad{font-family:"Anton","Impact",sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:.01em}
.rubrik{position:absolute;color:var(--svart);line-height:1;white-space:nowrap;transform-origin:0 50%%;will-change:transform}
.under{position:absolute;white-space:nowrap;will-change:transform,opacity}
.under span{display:block;margin-top:10px;font-size:19px;opacity:.72}
.piller{display:inline-block;background:var(--svart);color:var(--guld);font-size:30px;line-height:1;padding:8px 18px 10px;border-radius:40px}
.logga{position:absolute;display:block;will-change:transform,opacity}
.linje{position:absolute;display:block;width:3px;background:var(--svart);opacity:.13;transform-origin:50%% 0;will-change:transform}
.sek{position:absolute;color:var(--rod);font-size:44px;line-height:1;white-space:nowrap;will-change:transform,opacity}
.ratt{position:absolute;will-change:transform,opacity}
.bild,.hjbild{position:absolute;will-change:transform}
.bild img,.hjbild img{position:absolute;left:0;top:0;width:100%%;height:100%%;display:block}
.bricka,.hjbricka{position:absolute;will-change:transform}
.bricka svg,.hjbricka svg{position:absolute;left:0;top:0;display:block}
.bricka span,.hjbricka span{position:absolute;left:0;top:0;width:100%%;text-align:center;color:var(--guld);white-space:nowrap}
.bricka small,.hjbricka small{font-size:.42em;margin-left:2px;letter-spacing:.04em}
.txt{position:absolute;display:table}
.mitt{display:table-cell;vertical-align:middle}
.txt h3{line-height:1.05;color:var(--svart)}
.txt p{margin-top:7px;line-height:1.3;color:var(--svart);opacity:.72}
.marke{display:inline-block;background:var(--rod);color:#FFF4DC;font-size:15px;line-height:1;padding:5px 9px 6px;border-radius:4px;letter-spacing:.06em;margin-bottom:7px}
.lista{position:absolute;font-size:24px;line-height:1.2;color:var(--svart);will-change:opacity}
.lista span{display:inline-block;margin-right:44px}.lista b{text-transform:uppercase;color:var(--rod);font-family:"Anton","Impact",sans-serif;font-weight:400;font-size:26px;margin-left:6px}
.lista.liten{font-size:20px}.lista.liten b{font-size:22px}
.dipp{position:absolute;font-size:19px;line-height:1.35;color:var(--svart);opacity:.85}
.dipp b{color:var(--svart);font-family:"Anton","Impact",sans-serif;font-weight:400;font-size:24px;text-transform:uppercase;margin-right:12px;letter-spacing:.02em}
.hj{position:absolute;left:0;top:0;will-change:transform;transform:translate3d(0,-130%%,0)}
.hjpanel{position:absolute;left:0;top:0;background:var(--guld);background-image:radial-gradient(ellipse at 62%% 48%%,#F7E29A 0%%,#ECCC74 55%%,#DDB652 100%%)}
.hjdr{position:absolute;display:block;background:#DDB652;transform-origin:50%% 0;will-change:transform}
.hjtxt{position:absolute;will-change:transform,opacity}
.hjtxt h2{line-height:.95;color:var(--svart)}
.hjtxt p{margin-top:18px;line-height:1.25;color:var(--svart);opacity:.8;font-weight:600}
.hjrad{display:block;font-size:44px;color:var(--rod);letter-spacing:.06em;margin-bottom:6px}

.scen{position:absolute;left:0;top:0;opacity:0;will-change:opacity}
.scenbild{position:absolute;left:0;top:0;overflow:hidden}
.scenbild img{position:absolute;left:0;top:0;width:100%%;height:100%%;display:block;transform-origin:50%% 78%%;will-change:transform}
.scenrub{position:absolute;will-change:transform,opacity}
.srad{line-height:.96;color:var(--svart);white-space:nowrap;will-change:transform,opacity}
.prad{position:absolute;will-change:transform,opacity}
.prad h3{position:absolute;left:0;top:0;line-height:1.05;color:var(--svart);white-space:nowrap}
.ppris{position:absolute;right:0;top:0;line-height:1.05;color:var(--rod);white-space:nowrap;font-family:"Anton","Impact",sans-serif;text-transform:uppercase;transform-origin:100%% 50%%;will-change:transform}
.ppris small{font-size:.5em;margin-left:4px}
.prad p{position:absolute;left:0;line-height:1.25;color:var(--svart);opacity:.72}
.pstreck{position:absolute;left:0;display:block;height:3px;background:var(--svart);opacity:.14;transform-origin:0 50%%;will-change:transform}
.sband{position:absolute;left:0;display:block}
.sfot{position:absolute;font-size:18px;line-height:1.3;color:var(--svart);opacity:.8;will-change:opacity}
.byte{position:absolute;left:0;top:0;will-change:transform;transform:translate3d(0,-130%%,0)}
.bytlogga{position:absolute;display:block}
""" % dict(GULD=GULD, BLACK=BLACK, BEIGE=BEIGE, PRISROD=PRISROD)

JS_RORELSE = r"""
(function () {
  var $ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function kl(x) { return Math.max(0, Math.min(1, x)); }
  function ease(x) { x = kl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  function ut4(x) { x = kl(x); return 1 - Math.pow(1 - x, 4); }
  function studs(x) { x = kl(x); var c = 1.70158 * 1.3; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }
  var VARV = 60, HJ = 6, IN = .8, UT = .8, STARTER = [17, 37, 57];   /* tre hjältar per varv, den sista går över skarven */
  var MENYTID = VARV - STARTER.length * HJ;

  function skarm(id, g, h) {
    var rot = document.getElementById(id);
    return {
      ratter: $('.ratt.' + g, rot).map(function (r) { return { el: r, bild: r.querySelector('.bild'), bricka: r.querySelector('.bricka'), v: r.getAttribute('data-v') === '1' }; }),
      hj: $('.hj.' + h, rot).map(function (el) { return { el: el, txt: el.querySelector('.hjtxt'), bild: el.querySelector('.hjbild'), bricka: el.querySelector('.hjbricka'), dr: $('.hjdr', el).map(function (d) { return { el: d, f: parseFloat(d.getAttribute('data-f')) }; }) }; }),
      rubrik: rot.querySelector('.rubrik'), under: rot.querySelector('.under'), logga: rot.querySelector('.logga'),
      linjer: $('.linje', rot), sek: $('.sek', rot), listor: $('.lista, .dipp', rot), H: parseInt(rot.style.height, 10)
    };
  }
  var S = [skarm('s1', 'g1', 'h1')];
  /* stående skärmen: tre hela scener som byts med en guldpanel som rinner ner över skärmen */
  var SCENTID = VARV / 3, BYT = .9;
  var scener = $('#s2 .scen').map(function (el) { return { el: el, img: el.querySelector('.scenbild img'), rub: el.querySelector('.scenrub'), rader: $('.srad', el), logga: el.querySelector('.sl'),
    prad: $('.prad', el).map(function (r) { return { el: r, pris: r.querySelector('.ppris'), streck: r.querySelector('.pstreck') }; }), fot: el.querySelector('.sfot') }; });
  var byte = document.querySelector('#s2 .byte'), bytdr = $('#s2 .byte .hjdr').map(function (d) { return { el: d, f: parseFloat(d.getAttribute('data-f')) }; });

  window.sattTid = function (T) {
    T = ((T % VARV) + VARV) % VARV;
    /* var i hjältecykeln är vi? sedan = sekunder sedan menyn senast blev fri, synlig = hur mycket menytid som gått i varvet */
    var aktiv = -1, fas = 0, sedan = 1e9, synlig = 0, k;
    for (k = 0; k < STARTER.length; k++) { var d = ((T - STARTER[k]) % VARV + VARV) % VARV; if (d < HJ) { aktiv = k; fas = d; } var e = ((T - (STARTER[k] + HJ - UT)) % VARV + VARV) % VARV; if (e < sedan) sedan = e; }
    for (k = 0; k < STARTER.length; k++) { var slut = (STARTER[k] + HJ) % VARV; }
    /* synlig menytid: räkna sekunder av varvet som inte täcks av en hjälte, fram till T (varvet börjar mitt i hjälte tre) */
    var forsta = (STARTER[STARTER.length - 1] + HJ) % VARV;        /* här blir menyn fri första gången i varvet */
    var rel = ((T - forsta) % VARV + VARV) % VARV, r0 = 0;
    for (k = 0; k < STARTER.length; k++) { var st = ((STARTER[k] - forsta) % VARV + VARV) % VARV; if (rel > st) r0 += Math.min(HJ, rel - st); }
    synlig = rel - r0;

    S.forEach(function (s) {
      var n = s.ratter.length, per = MENYTID / n;
      s.ratter.forEach(function (r, i) {
        /* intåg: rätterna glider in från sin sida och studsar på plats, en i taget */
        var p = kl((sedan - .15 - i * .07) / .7), inn = studs(p), op = kl((sedan - .15 - i * .07) / .25);
        var fran = (r.v ? -1 : 1) * 140 * (1 - inn);
        /* strålkastare: varje rätt får sin stund en gång per varv */
        var lage = (synlig / per - i), m = (lage >= 0 && lage < 1) ? ease(lage / .2) * (1 - ease((lage - .8) / .2)) : 0;
        var gung = Math.sin((T / VARV * 8 + i * .31) * 2 * Math.PI), vag = Math.sin((T / VARV * 5 + i * .47) * 2 * Math.PI);
        r.el.style.opacity = op.toFixed(3);
        r.el.style.transform = 'translate3d(' + fran.toFixed(1) + 'px,0,0)';
        r.bild.style.transform = 'translate3d(0,' + (gung * 4 - 10 * m).toFixed(2) + 'px,0) rotate(' + (vag * 1.6 + (r.v ? -3 : 3) * m).toFixed(2) + 'deg) scale(' + (1 + .16 * m).toFixed(4) + ')';
        var bp = studs(kl((sedan - .55 - i * .07) / .45));
        r.bricka.style.transform = 'rotate(' + (-10 + vag * 5 + 360 * ease(lage >= 0 && lage < 1 ? lage / .35 : 0)).toFixed(2) + 'deg) scale(' + (bp * (1 + .22 * m)).toFixed(4) + ')';
      });
      var rp = ut4((sedan - .05) / .7);
      s.rubrik.style.transform = 'translate3d(' + (-90 * (1 - rp)).toFixed(1) + 'px,0,0) scale(' + (1 + .025 * Math.sin(T / VARV * 10 * 2 * Math.PI)).toFixed(4) + ')';
      s.rubrik.style.opacity = kl(sedan / .3).toFixed(3);
      if (s.under) { s.under.style.opacity = kl((sedan - .4) / .4).toFixed(3); s.under.style.transform = 'translate3d(0,' + (20 * (1 - ut4((sedan - .4) / .6))).toFixed(1) + 'px,0)'; }
      s.logga.style.opacity = kl((sedan - .3) / .4).toFixed(3);
      s.logga.style.transform = 'translate3d(0,' + (-30 * (1 - ut4((sedan - .3) / .6)) + 3 * Math.sin(T / VARV * 6 * 2 * Math.PI)).toFixed(1) + 'px,0)';
      s.linjer.forEach(function (l) { l.style.transform = 'scaleY(' + ut4((sedan - .2) / .9).toFixed(4) + ')'; });
      s.sek.forEach(function (h, i) { h.style.opacity = kl((sedan - .2 - i * .15) / .35).toFixed(3); h.style.transform = 'translate3d(' + (-50 * (1 - ut4((sedan - .2 - i * .15) / .6))).toFixed(1) + 'px,0,0)'; });
      s.listor.forEach(function (l) { l.style.opacity = (kl((sedan - 1.1) / .5) * (l.className.indexOf('dipp') >= 0 ? .85 : 1)).toFixed(3); });

      /* hjältarna: guldpanelen glider ner uppifrån, håller, och fortsätter ner och ut. Alltid lodrätt, aldrig i sidled. */
      s.hj.forEach(function (h, k) {
        if (k !== aktiv) { h.el.style.transform = 'translate3d(0,-130%,0)'; return; }
        var y = fas < IN ? -118 * (1 - ut4(fas / IN)) : (fas > HJ - UT ? 128 * ease((fas - (HJ - UT)) / UT) : 0);
        h.el.style.transform = 'translate3d(0,' + y.toFixed(2) + '%,0)';
        var a = fas - IN * .6;
        h.txt.style.opacity = kl(a / .4).toFixed(3);
        h.txt.style.transform = 'translate3d(' + (-120 * (1 - ut4(a / .7))).toFixed(1) + 'px,0,0)';
        h.bild.style.transform = 'translate3d(0,' + (Math.sin(fas * 1.3) * 10).toFixed(2) + 'px,0) rotate(' + (Math.sin(fas * .9) * 2.5 - 4 + 4 * ut4(a / .9)).toFixed(2) + 'deg) scale(' + (.55 + .45 * studs(a / .8) + .03 * fas / HJ).toFixed(4) + ')';
        h.bricka.style.transform = 'rotate(' + (-14 + Math.sin(fas * 2.2) * 6).toFixed(2) + 'deg) scale(' + studs((a - .5) / .5).toFixed(4) + ')';
        h.dr.forEach(function (d) { d.el.style.transform = 'scaleY(' + (.35 + .9 * ut4(fas / 2.2) + .12 * Math.sin((fas * .9 + d.f * 6))).toFixed(4) + ')'; });
      });
    });

    var nu = Math.floor(T / SCENTID) % scener.length, lok = T - nu * SCENTID;      /* sekunder in i scenen */
    scener.forEach(function (s, k) {
      if (k !== nu) { s.el.style.opacity = '0'; return; }
      s.el.style.opacity = '1';
      s.img.style.transform = 'scale(' + (1.01 + .05 * lok / SCENTID).toFixed(4) + ') translate3d(0,' + (-14 - 16 * lok / SCENTID).toFixed(2) + 'px,0)';   /* långsam inzoomning */
      s.rub.style.transform = 'translate3d(0,0,0)';
      s.rader.forEach(function (r, i) { var a = lok - .55 - i * .16; r.style.opacity = kl(a / .3).toFixed(3); r.style.transform = 'translate3d(' + (-160 * (1 - ut4(a / .7))).toFixed(1) + 'px,0,0) scale(' + (1 + .02 * Math.sin((lok * .5 + i) * 1.7)).toFixed(4) + ')'; });
      s.logga.style.opacity = kl((lok - .9) / .4).toFixed(3);
      s.logga.style.transform = 'translate3d(0,' + (3 * Math.sin(lok * .8)).toFixed(2) + 'px,0)';
      var n = s.prad.length;
      s.prad.forEach(function (r, i) {
        var a = lok - 1.0 - i * .11; r.el.style.opacity = kl(a / .3).toFixed(3);
        r.el.style.transform = 'translate3d(0,' + (46 * (1 - ut4(a / .6))).toFixed(1) + 'px,0)';
        r.streck.style.transform = 'scaleX(' + ut4((a - .15) / .7).toFixed(4) + ')';
        /* priserna pulserar en i taget genom hela scenen */
        var per = (SCENTID - 4) / n, lage = (lok - 3) / per - i, m = (lage >= 0 && lage < 1) ? Math.sin(Math.PI * lage) : 0;
        r.pris.style.transform = 'scale(' + (studs((a - .2) / .45) * (1 + .22 * m)).toFixed(4) + ') rotate(' + (-4 * m).toFixed(2) + 'deg)';
      });
      if (s.fot) s.fot.style.opacity = (kl((lok - 2.2) / .5) * .8).toFixed(3);
    });
    /* bytet: panelen är mitt över skärmen exakt när scenen växlar */
    var till = SCENTID - lok, f = lok < BYT ? BYT + lok : (till < BYT ? BYT - till : -1);
    if (f < 0) byte.style.transform = 'translate3d(0,-130%,0)';
    else { var yy = f < BYT ? -118 * (1 - ut4(f / BYT)) : 128 * ease((f - BYT) / BYT); byte.style.transform = 'translate3d(0,' + yy.toFixed(2) + '%,0)';
      bytdr.forEach(function (d) { d.el.style.transform = 'scaleY(' + (.5 + .8 * kl(f / BYT) + .1 * Math.sin(f * 5 + d.f * 6)).toFixed(4) + ')'; }); }
  };
  window.satt = function (t) { window.sattTid(t * VARV); };
  window.PROGRAM = { varv: VARV, total: VARV };
"""

JS = JS_RORELSE + r"""
  /* ---- spelaren ----
     ?skarm=1  liggande burgarskärmen (1920x1080)
     ?skarm=2  stående skärmen med sides och efterrätter (1080x1920)
     ?rotera=90 eller 270  om skärmen hänger stående men webbläsaren ritar liggande
     ?just=80  finjustering i millisekunder
     Utan parameter visas båda skärmarna inpassade, för förhandsvisning. */
  var Q = function (n) { var m = new RegExp('[?&]' + n + '=([^&]*)').exec(location.search); return m ? m[1] : null; };
  var skarm = parseInt(Q('skarm'), 10), rotera = parseInt(Q('rotera'), 10) || 0, yta = document.getElementById('yta');
  var RUTA = { 1: [0, 0, 1920, 1080], 2: [1920, 0, 1080, 1920] };
  function passa() {
    var w = window.innerWidth, h = window.innerHeight;
    if (rotera === 90 || rotera === 270) { var x = w; w = h; h = x; }
    var r = RUTA[skarm] || [0, 0, 3000, 1920], k = Math.min(w / r[2], h / r[3]);
    var dx = (w - r[2] * k) / 2 - r[0] * k, dy = (h - r[3] * k) / 2 - r[1] * k;
    document.documentElement.style.width = document.body.style.width = window.innerWidth + 'px';
    document.documentElement.style.height = document.body.style.height = window.innerHeight + 'px';
    yta.style.transform = (rotera ? 'translate(' + (rotera === 90 ? window.innerWidth : 0) + 'px,' + (rotera === 270 ? window.innerHeight : 0) + 'px) rotate(' + rotera + 'deg) ' : '') + 'translate(' + dx.toFixed(2) + 'px,' + dy.toFixed(2) + 'px) scale(' + k + ')';
    if (RUTA[skarm]) { var andra = document.getElementById(skarm === 1 ? 's2' : 's1'); andra.style.display = 'none'; }
  }
  if (location.search.indexOf('stilla') >= 0) { window.RENDER = true; return; }   /* renderaren styr tiden själv */
  passa(); window.addEventListener('resize', passa);

  /* ---- helskärm ----
     Vanliga tv-apparater har ingen URL Launcher, där ritar webbläsaren sitt fält över sidan.
     Ett tryck på OK eller ett klick ber webbläsaren om helskärm. Kräver en knapptryckning,
     det går inte att göra automatiskt. */
  var rot = document.documentElement;
  var begar = rot.requestFullscreen || rot.webkitRequestFullscreen || rot.webkitRequestFullScreen || rot.mozRequestFullScreen || rot.msRequestFullscreen;
  var iHel = function () { return !!(document.fullscreenElement || document.webkitFullscreenElement || document.webkitIsFullScreen || document.mozFullScreenElement || document.msFullscreenElement); };
  if (begar && RUTA[skarm]) {
    var tips = document.createElement('div');
    tips.id = 'heltips';
    tips.appendChild(document.createTextNode('Tryck OK för helskärm'));
    tips.style.cssText = 'position:fixed;left:50%;top:50%;z-index:99;padding:22px 34px;border-radius:12px;background:#15110C;color:#EFE4CF;font:600 34px/1 Inter,Arial,sans-serif;white-space:nowrap;opacity:1;transition:opacity .6s;pointer-events:none';
    tips.style.transform = 'translate(-50%,-50%) rotate(' + rotera + 'deg)';
    tips.style.webkitTransform = tips.style.transform;
    document.body.appendChild(tips);
    var dolj = setTimeout(function () { tips.style.opacity = '0'; }, 12000);
    var hel = function () {
      if (iHel()) return;
      try { var l = begar.call(rot); if (l && l['catch']) l['catch'](function () {}); } catch (fel) {}
    };
    var andrad = function () { tips.style.opacity = iHel() ? '0' : '1'; clearTimeout(dolj); if (!iHel()) dolj = setTimeout(function () { tips.style.opacity = '0'; }, 12000); setTimeout(passa, 60); setTimeout(passa, 600); };
    document.addEventListener('click', hel);
    document.addEventListener('keydown', function (e) { var k = e.keyCode; if (k === 13 || k === 32 || k === 70) hel(); });
    document.addEventListener('fullscreenchange', andrad);
    document.addEventListener('webkitfullscreenchange', andrad);
  }

  var just = parseInt(Q('just'), 10) || 0, forskjut = 0, mal = 0, forsta = true;
  function enMatning() { var t0 = Date.now(); return fetch('/api/tid?' + t0, { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) { var t1 = Date.now(); return { rtt: t1 - t0, f: d.nu + (t1 - t0) / 2 - t1 }; }); }
  function synka() { var basta = null, n = 0; (function nasta() { enMatning().then(function (m) { if (!basta || m.rtt < basta.rtt) basta = m; }).catch(function () {}).then(function () { if (++n < 7) setTimeout(nasta, 150); else if (basta) { mal = basta.f; if (forsta || Math.abs(mal - forskjut) > 500) { forskjut = mal; forsta = false; } } }); })(); }
  synka(); setInterval(synka, 5 * 60 * 1000);
  setInterval(function () { var d = mal - forskjut; if (d) forskjut += Math.abs(d) < 2 ? d : d * 0.1; }, 200);

  /* ny version utlagd? ladda om i skarven mellan två varv så bilden inte hackar mitt i */
  var version = null, vantar = false;
  function kolla() { fetch('/version.json?' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) { if (version === null) version = d.v; else if (d.v !== version) vantar = true; }).catch(function () {}); }
  kolla(); setInterval(kolla, 2 * 60 * 1000);
  var senast = 0, forraT = 0, tot = window.PROGRAM.total;
  (function snurra(nu) { requestAnimationFrame(snurra); if (nu - senast < 30) return; senast = nu;
    var T = ((Date.now() + forskjut + just) / 1000) % tot; if (vantar && T < forraT) { location.reload(); return; } forraT = T; window.sattTid(T); })(0);
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(function () {});
})();
"""

SIDA = f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8"><title>Dripp'n Burgers – menyskärmar</title>
<meta name="robots" content="noindex, nofollow"><meta name="viewport" content="width=device-width, initial-scale=1">
<link href="/typsnitt/typsnitt.css" rel="stylesheet"><style>{CSS}</style></head>
<body><div id="yta">{liggande()}{staende()}</div><script>{JS}</script></body></html>
"""

FORBJUDET = ["inset:", " translate:", "clip-path:", "clipPath =", "aspect-ratio", ":has(", "color-mix", "?.", "??", "gap:"]
for f in FORBJUDET:
    assert f not in SIDA, f"Tizen tål inte: {f}"

os.makedirs(os.path.join(WEBB, "assets"), exist_ok=True)
open(os.path.join(WEBB, "skarm.html"), "w", encoding="utf8").write(SIDA)
for fil in os.listdir(os.path.join(HAR, "assets")):
    if fil.startswith("o-"): continue   # v1-bilderna används inte längre
    shutil.copy2(os.path.join(HAR, "assets", fil), os.path.join(WEBB, "assets", fil))
filer = ["/skarm"] + sorted("/assets/" + f for f in os.listdir(os.path.join(WEBB, "assets"))) + sorted("/typsnitt/" + f for f in os.listdir(os.path.join(WEBB, "typsnitt")))
open(os.path.join(WEBB, "sw.js"), "w", encoding="utf8").write("""// Håller sidan och bilderna i skärmens minne så att menyn visas även om nätet går ner eller skärmen startar om utan nät.
const LAGER = 'drippn-skarm-%s';
const FORLADDA = %s;
self.addEventListener('install', e => { e.waitUntil(caches.open(LAGER).then(c => Promise.all(FORLADDA.map(u => c.add(u).catch(() => {})))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== LAGER).map(n => caches.delete(n)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.pathname.startsWith('/api/') || u.pathname === '/version.json') return;
  const sida = u.origin === location.origin && u.pathname === '/skarm';
  e.respondWith(fetch(e.request).then(r => { if (r.ok || r.type === 'opaque') { const k = r.clone(); caches.open(LAGER).then(c => c.put(sida ? '/skarm' : e.request, k)); } return r; })
    .catch(() => caches.match(sida ? '/skarm' : e.request)));
});
""" % (VERSION, json.dumps(filer)))
open(os.path.join(WEBB, "version.json"), "w").write(json.dumps({"v": VERSION}))
os.makedirs(os.path.join(WEBB, "api"), exist_ok=True)
open(os.path.join(WEBB, "api", "tid.js"), "w", encoding="utf8").write("""// Gemensam klocka för skärmarna. Svarar med serverns tid i millisekunder.
export default function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.status(200).json({ nu: Date.now() });
}
""")
open(os.path.join(WEBB, "vercel.json"), "w").write("""{ "cleanUrls": true,
  "headers": [
    { "source": "/(.*)", "headers": [ { "key": "X-Robots-Tag", "value": "noindex, nofollow" } ] },
    { "source": "/version.json", "headers": [ { "key": "Cache-Control", "value": "no-store" } ] },
    { "source": "/sw.js", "headers": [ { "key": "Cache-Control", "value": "no-cache" } ] }
  ] }
""")
open(os.path.join(WEBB, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
open(os.path.join(WEBB, "index.html"), "w", encoding="utf8").write("""<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Dripp'n Burgers – skärmar</title>
<style>body{margin:0;background:#0a0a0a;color:#fefcf2;font:16px/1.5 -apple-system,Helvetica,Arial,sans-serif;padding:32px 20px}h1{font-size:22px;margin:0 0 6px}p{margin:0 0 20px;color:#c9bda8;max-width:62ch}
.rad{display:grid;grid-template-columns:1920fr 1080fr;column-gap:10px;max-width:1200px;align-items:start}.rad a{display:block;color:inherit;text-decoration:none}.rad iframe{width:100%;border:0;background:#000;pointer-events:none;display:block}
.a{height:0;padding-bottom:56.25%;position:relative}.b{height:0;padding-bottom:177.78%;position:relative}.a iframe,.b iframe{position:absolute;left:0;top:0;height:100%}
.rad span{display:block;padding:8px 2px;font-size:14px}code{color:#eccc74}</style></head><body>
<h1>Dripp'n Burgers, menyskärmar</h1>
<p>En adress per skärm. Skriv in adressen i skärmens webbläsare eller URL Launcher. Båda går efter samma klocka och laddar om sig själva när en ny version läggs ut.</p>
<div class="rad">
<a href="/skarm?skarm=1"><div class="a"><iframe src="/skarm?skarm=1" loading="lazy" title="Liggande"></iframe></div><span>Skärm 1, liggande, burgare <code>/skarm?skarm=1</code></span></a>
<a href="/skarm?skarm=2"><div class="b"><iframe src="/skarm?skarm=2" loading="lazy" title="Stående"></iframe></div><span>Skärm 2, stående, sides och efterrätt <code>/skarm?skarm=2</code></span></a>
</div></body></html>
""")
print("skrev webb/ version", VERSION, "|", len(SIDA), "tecken |", len(filer), "filer i förladdningen")
