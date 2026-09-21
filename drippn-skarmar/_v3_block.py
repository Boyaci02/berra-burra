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
        tx = int(W * .06); ty = int(H * .20) if W > H else int(H * .08)
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
    ut.append(hjalte(1, "h1", HJALTAR_1, 1920, 1080, 190))
    ut.append("</section>")
    return "".join(ut)


def staende():
    X = 1920
    ut = [f'<section class="skarm" id="s2" style="left:{X}px;top:0;width:1080px;height:1920px">',
          '<h1 class="rubrik r2" style="left:50px;top:30px;font-size:104px;line-height:.92">Sides<br>&amp; snacks</h1>',
          '<img class="logga l2" src="/assets/logga-svart.png" alt="Dripp\'n Burgers" style="left:760px;top:44px;width:270px">',
          '<i class="linje" style="left:539px;top:300px;height:1240px"></i>']
    n = 0
    ut.append('<h2 class="sek" style="left:50px;top:246px">Snacks</h2>')
    for i, (bild, namn, pris, text, ai) in enumerate(SNACKS):
        kol, rad = i % 2, i // 2
        ut.append(ratt(n, "g2", bild, namn, pris, text, 50 + kol * 510, 306 + rad * 214, 470, 204, 232, (rad + kol) % 2 == 0, 33, 16, 92)); n += 1
    ut.append('<h2 class="sek" style="left:50px;top:748px">Sides</h2>')
    for i, (bild, namn, pris, text, ai) in enumerate(SIDES):
        kol, rad = i % 2, i // 2
        ut.append(ratt(n, "g2", bild, namn, pris, text, 50 + kol * 510, 808 + rad * 196, 470, 186, 214, (rad + kol) % 2 == 0, 32, 16, 88)); n += 1
    rad_ = "".join(f'<span>{e(t)} <b>{p} kr</b></span>' for t, p in SIDES_TEXT)
    ut.append(f'<div class="lista" style="left:50px;top:1404px;width:980px">{rad_}</div>')
    ut.append(f'<div class="dipp" style="left:50px;top:1446px;width:980px"><b>Dipsåser 15 kr</b> {e(DIPPAR)}</div>')
    ut.append('<h2 class="sek" style="left:50px;top:1520px">Efterrätt &amp; shakes</h2>')
    ut.append('<i class="linje" style="left:539px;top:1580px;height:290px"></i>')
    for i, (bild, namn, pris, text, ai) in enumerate(EFTER):
        kol, rad = i % 2, i // 2
        ut.append(ratt(n, "g2", bild, namn, pris, text, 50 + kol * 510, 1580 + rad * 150, 470, 142, 176, (rad + kol) % 2 == 0, 29, 15, 80)); n += 1
    rad_ = "".join(f'<span>{e(t)} <b>{p} kr</b></span>' for t, p in EFTER_TEXT)
    ut.append(f'<div class="lista liten" style="left:50px;top:1884px;width:980px">{rad_}</div>')
    ut.append(hjalte(2, "h2", HJALTAR_2, 1080, 1920, 150))
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
  var S = [skarm('s1', 'g1', 'h1'), skarm('s2', 'g2', 'h2')];

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
  };
  window.satt = function (t) { window.sattTid(t * VARV); };
  window.PROGRAM = { varv: VARV, total: VARV };
"""
