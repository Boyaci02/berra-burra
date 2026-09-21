// Flera tidpunkter av båda skärmarna på ett ark: node rendera-ark.mjs 12 20.4 32 52
import { chromium } from '/Users/emanuelboyaci/cutie-bd-sync/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path';
const ROT = path.resolve('webb'), tider = process.argv.slice(2).map(parseFloat);
const typ = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2', '.json': 'application/json' };
const srv = http.createServer((q, s) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/skarm') p = '/skarm.html'; const f = path.join(ROT, p);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); } else { s.writeHead(200, { 'Content-Type': typ[path.extname(f)] || 'application/octet-stream' }); s.end(d); } }); }).listen(8946);
const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 3000, height: 1920 }, deviceScaleFactor: 0.4 });
const p = await ctx.newPage(); const fel = []; p.on('pageerror', e => fel.push(e.message));
await p.goto('http://localhost:8946/skarm?stilla'); await p.waitForTimeout(2000); await p.evaluate(() => document.fonts.ready);
for (const t of tider) { await p.evaluate(x => window.sattTid(x), t); await p.waitForTimeout(150); await p.screenshot({ path: `_ut/ark-${t}.jpg`, type: 'jpeg', quality: 85 }); }
await b.close(); srv.close(); console.log('fel:', fel.slice(0, 3));
