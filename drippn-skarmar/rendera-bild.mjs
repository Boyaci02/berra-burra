// Stillbild av båda skärmarna vid en given tid: node rendera-bild.mjs 2.5
import { chromium } from '/Users/emanuelboyaci/cutie-bd-sync/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path';
const ROT = path.resolve('webb'), T = parseFloat(process.argv[2] || '2.5');
const typ = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2', '.json': 'application/json' };
const srv = http.createServer((q, s) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/skarm') p = '/skarm.html'; const f = path.join(ROT, p);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); } else { s.writeHead(200, { 'Content-Type': typ[path.extname(f)] || 'application/octet-stream' }); s.end(d); } }); }).listen(8947);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 3000, height: 1920 } });
await p.goto('http://localhost:8947/skarm?stilla'); await p.waitForTimeout(1500); await p.evaluate(() => document.fonts.ready);
await p.evaluate(t => window.sattTid(t), T);
await p.screenshot({ path: '_ut/skarm1.png', clip: { x: 0, y: 0, width: 1920, height: 1080 } });
await p.screenshot({ path: '_ut/skarm2.png', clip: { x: 1920, y: 0, width: 1080, height: 1920 } });
await b.close(); srv.close(); console.log('klart', T);
