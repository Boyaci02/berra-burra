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


def dropp(x0, bredd, seed):
    """Gulddropp längs överkanten: varje dropp är en egen div som skalas i höjdled."""
    ut, x, i = [], x0 + 30, 0
    while x < x0 + bredd - 40:
        r = (seed * 9301 + i * 49297) % 233280 / 233280.0
        r2 = (seed * 7919 + i * 104729) % 199933 / 199933.0
        w = 22 + int(r * 26)
        h = 16 + int(r2 * 34)
        ut.append(f'<i class="dr" data-f="{r:.3f}" style="left:{x}px;width:{w}px;height:{h}px;border-radius:0 0 {w // 2}px {w // 2}px"></i>')
        x += w + 40 + int(r2 * 150)
        i += 1
    return "".join(ut)


def kort(i, bild, namn, pris, text, x, y, w, bildh, grupp, marke="", namnpx=40, textpx=19, ai=False, skiva=False):
    """En rätt: frilagd bild överst, namn och pris på en rad, innehåll under."""
    bw = w - 30
    m = f'<b class="marke">{e(marke)}</b>' if marke else ""
    s = f'<i class="skiva" style="left:{(w - bildh) // 2}px;top:0;width:{bildh}px;height:{bildh}px"></i>' if skiva else ""
    return (f'<div class="kort {grupp}" data-i="{i}" style="left:{x}px;top:{y}px;width:{w}px">'
            f'<i class="glod" style="left:{w // 2 - 210}px;top:{bildh // 2 - 170}px"></i>{s}'
            f'<div class="bild" style="left:15px;top:0;width:{bw}px;height:{bildh}px"><img src="/assets/o-{bild}.webp" alt=""></div>{m}'
            f'<div class="rad" style="top:{bildh + 8}px;width:{w}px"><h3 style="font-size:{namnpx}px">{e(namn)}</h3><span class="pris" style="font-size:{namnpx}px">{pris}<small>kr</small></span></div>'
            + (f'<p style="top:{bildh + 8 + int(namnpx * 1.18)}px;width:{w}px;font-size:{textpx}px">{e(text)}</p>' if text else "")
            + "</div>")


def sidokort(i, bild, namn, pris, text, x, y, w, bildw, bildh, grupp, skiva=False):
    tx = bildw + 18
    s = f'<i class="skiva" style="left:{(bildw - bildh) // 2}px;top:0;width:{bildh}px;height:{bildh}px"></i>' if skiva else ""
    return (f'<div class="kort {grupp}" data-i="{i}" style="left:{x}px;top:{y}px;width:{w}px">'
            f'<i class="glod" style="left:{bildw // 2 - 210}px;top:{bildh // 2 - 170}px"></i>{s}'
            f'<div class="bild" style="left:0;top:0;width:{bildw}px;height:{bildh}px"><img src="/assets/o-{bild}.webp" alt=""></div>'
            f'<div class="rad" style="left:{tx}px;top:14px;width:{w - tx}px"><h3 style="font-size:30px">{e(namn)}</h3></div>'
            f'<div class="rad" style="left:{tx}px;top:52px;width:{w - tx}px"><span class="pris" style="font-size:34px;right:auto;left:0;transform-origin:0 60%">{pris}<small>kr</small></span></div>'
            + (f'<p style="left:{tx}px;top:96px;width:{w - tx}px;font-size:16px">{e(text)}</p>' if text else "")
            + "</div>")


def liggande():
    ut = ['<section class="skarm" id="s1" style="left:0;top:0;width:1920px;height:1080px">',
          '<div class="topp" style="width:1920px"></div>', dropp(0, 1920, 3),
          '<img class="logga" src="/assets/logga.png" alt="Dripp\'n Burgers" style="left:56px;top:54px;width:330px">',
          '<h1 style="left:440px;top:58px;font-size:132px">Burgare</h1>',
          '<div class="info" style="left:1180px;top:72px;width:690px">'
          '<b class="piller">Pommes ingår</b>'
          '<span>2 × 80 g smashat kött i varje burgare.<br>Glutenfritt eller laktosfritt bröd finns, eller i sallad.</span></div>']
    kol, radh, x0, y0, w = 4, 292, 50, 214, 440
    for i, (bild, namn, pris, text, marke, ai) in enumerate(BURGARE):
        x = x0 + (i % kol) * (w + 20)
        y = y0 + (i // kol) * radh
        ut.append(kort(i, bild, namn, pris, text, x, y, w, 156, "g1", marke, 38, 18, ai))
    ut.append("</section>")
    return "".join(ut)


def staende():
    X = 1920
    ut = [f'<section class="skarm" id="s2" style="left:{X}px;top:0;width:1080px;height:1920px">',
          '<div class="topp" style="width:1080px"></div>', dropp(0, 1080, 11),
          '<img class="logga" src="/assets/logga.png" alt="Dripp\'n Burgers" style="left:50px;top:70px;width:300px">',
          '<h1 style="left:400px;top:62px;font-size:104px;line-height:.92">Sides<br>&amp; snacks</h1>']
    n = 0
    ut.append('<h2 style="left:50px;top:290px">Snacks</h2>')
    for i, (bild, namn, pris, text, ai) in enumerate(SNACKS):
        ut.append(kort(n, bild, namn, pris, text, 50 + (i % 2) * 500, 350 + (i // 2) * 282, 480, 178, "g2", "", 40, 19, ai)); n += 1
    ut.append('<h2 style="left:50px;top:926px">Sides</h2>')
    for i, (bild, namn, pris, text, ai) in enumerate(SIDES):
        ut.append(kort(n, bild, namn, pris, text, 50 + (i % 3) * 334, 984 + (i // 3) * 226, 312, 140, "g2", "", 30, 17, ai)); n += 1
    rad = "".join(f'<span>{e(t)} <b>{p} kr</b></span>' for t, p in SIDES_TEXT)
    ut.append(f'<div class="lista" style="left:50px;top:1446px;width:980px">{rad}</div>')
    ut.append(f'<div class="dipp" style="left:50px;top:1490px;width:980px"><b>Dipsåser 15 kr</b> {e(DIPPAR)}</div>')
    ut.append('<h2 style="left:50px;top:1566px">Efterrätt &amp; shakes</h2>')
    for i, (bild, namn, pris, text, ai) in enumerate(EFTER):
        ut.append(sidokort(n, bild, namn, pris, text, 50 + (i % 2) * 500, 1626 + (i // 2) * 132, 480, 150, 122, "g2", skiva=bild in ("vaffla", "pistage", "glass"))); n += 1
    rad = "".join(f'<span>{e(t)} <b>{p} kr</b></span>' for t, p in EFTER_TEXT)
    ut.append(f'<div class="lista liten" style="left:50px;top:1886px;width:980px">{rad}</div>')
    ut.append("</section>")
    return "".join(ut)


CSS = """
:root{--guld:%(GULD)s;--svart:%(SVART)s;--kram:%(KRAM)s;--rod:%(ROD)s}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:3000px;height:1920px;overflow:hidden;background:#000}
body{font-family:"Inter","Helvetica Neue",Arial,sans-serif;color:var(--kram)}
#yta{position:absolute;left:0;top:0;width:3000px;height:1920px;transform-origin:0 0}
.skarm{position:absolute;overflow:hidden;background:var(--svart);background-image:radial-gradient(ellipse at 50%% 0%%,#1c1710 0%%,#0A0A0A 62%%)}
.topp{position:absolute;left:0;top:0;height:22px;background:var(--guld)}
.dr{position:absolute;top:20px;display:block;background:var(--guld);transform-origin:50%% 0;will-change:transform}
.logga{position:absolute;display:block}
h1,h2,h3,.pris,.piller,.marke{font-family:"Anton","Impact",sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:.01em}
h1{position:absolute;color:var(--guld);line-height:1;white-space:nowrap}
h2{position:absolute;color:var(--guld);font-size:46px;line-height:1;white-space:nowrap}
h2:after{content:"";position:absolute;left:100%%;top:24px;margin-left:20px;width:1400px;height:3px;background:var(--guld);opacity:.35}
.info{position:absolute;color:var(--kram);font-size:21px;line-height:1.35}
.info span{display:block;margin-top:14px;opacity:.78}
.piller{display:inline-block;background:var(--guld);color:var(--svart);font-size:34px;line-height:1;padding:9px 20px 11px;border-radius:40px}
.kort{position:absolute;height:10px}
.bild{position:absolute;will-change:transform;transform-origin:50%% 70%%}
.bild img{position:absolute;left:0;top:0;width:100%%;height:100%%;object-fit:contain;object-position:50%% 100%%;display:block}
.glod{position:absolute;display:block;width:420px;height:340px;opacity:0;will-change:opacity;background:radial-gradient(ellipse at 50%% 55%%,rgba(236,204,116,.50) 0%%,rgba(236,204,116,.16) 38%%,rgba(236,204,116,0) 68%%)}
.skiva{position:absolute;display:block;border-radius:50%%;background:radial-gradient(circle at 50%% 50%%,#2a251b 0%%,#17140f 60%%,rgba(10,10,10,0) 72%%)}
.rad{position:absolute;left:0;height:50px}
.rad h3{position:absolute;left:0;top:0;line-height:1.1;color:var(--kram);white-space:nowrap}
.pris{position:absolute;right:0;top:0;line-height:1.1;color:var(--guld);white-space:nowrap;transform-origin:100%% 60%%;will-change:transform}
.pris small{font-size:.5em;margin-left:4px;letter-spacing:.04em}
.kort p{position:absolute;left:0;line-height:1.32;color:var(--kram);opacity:.72}
.marke{position:absolute;left:0;top:0;background:var(--rod);color:var(--kram);font-size:17px;line-height:1;padding:6px 10px 7px;border-radius:4px;letter-spacing:.05em;border:1px solid rgba(236,204,116,.45)}
.lista{position:absolute;font-size:24px;line-height:1.2;color:var(--kram)}
.lista span{display:inline-block;margin-right:44px}.lista b{text-transform:uppercase;color:var(--guld);font-family:"Anton","Impact",sans-serif;font-weight:400;font-size:26px;margin-left:6px}
.lista.liten{font-size:20px}.lista.liten b{font-size:22px}
.dipp{position:absolute;font-size:19px;line-height:1.35;color:var(--kram);opacity:.85}
.dipp b{color:var(--guld);font-family:"Anton","Impact",sans-serif;font-weight:400;font-size:24px;text-transform:uppercase;margin-right:12px;letter-spacing:.02em}
""" % dict(GULD=GULD, SVART=SVART, KRAM=KRAM, ROD=ROD)

JS = r"""
(function () {
  var $ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
  function ease(x) { x = Math.max(0, Math.min(1, x)); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  var VARV = 60;
  var grupper = ['g1', 'g2'].map(function (g) {
    return $('.kort.' + g).map(function (k) { return { bild: k.querySelector('.bild'), glod: k.querySelector('.glod'), pris: k.querySelector('.pris') }; });
  });
  var dr = $('.dr').map(function (d) { return { el: d, f: parseFloat(d.getAttribute('data-f')) }; });

  /* t går 0..1 över ett varv. Strålkastaren vandrar genom rätterna, en i taget, och varvet går jämnt ut. */
  window.satt = function (t) {
    grupper.forEach(function (lista) {
      var n = lista.length;
      lista.forEach(function (k, i) {
        var lage = ((t * n - i) % n + n) % n;                    /* 0..1 = den här rättens tur */
        var m = lage < 1 ? ease(lage / .22) * (1 - ease((lage - .78) / .22)) : 0;
        var gung = Math.sin((t * 6 + i * .37) * 2 * Math.PI) * 3;   /* 6 hela svängar per varv = sömlös slinga */
        k.bild.style.transform = 'translate3d(0,' + (gung - 8 * m).toFixed(2) + 'px,0) scale(' + (1 + .13 * m).toFixed(4) + ')';
        k.glod.style.opacity = m.toFixed(3);
        k.pris.style.transform = 'scale(' + (1 + .16 * m).toFixed(4) + ')';
      });
    });
    dr.forEach(function (d) {
      var s = 1 + .22 * Math.sin((t * 4 + d.f) * 2 * Math.PI);   /* 4 hela svängar per varv */
      d.el.style.transform = 'scaleY(' + s.toFixed(4) + ')';
    });
  };
  window.PROGRAM = { varv: VARV, total: VARV };
  window.sattTid = function (T) { var tot = VARV; T = ((T % tot) + tot) % tot; window.satt(T / tot); };

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
