// Renderar hela varvet (60 s) med båda skärmarna bredvid varandra: node rendera-film.mjs [fps]
import { chromium } from '/Users/emanuelboyaci/cutie-bd-sync/node_modules/playwright/index.mjs';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { spawn } from 'child_process';
const ROT = path.resolve('webb'), FPS = parseInt(process.argv[2] || '20', 10), SEK = 60;
const typ = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2', '.json': 'application/json' };
const srv = http.createServer((q, s) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/skarm') p = '/skarm.html'; const f = path.join(ROT, p);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); } else { s.writeHead(200, { 'Content-Type': typ[path.extname(f)] || 'application/octet-stream' }); s.end(d); } }); }).listen(8945);
const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 3000, height: 1920 }, deviceScaleFactor: 0.5 });
const p = await ctx.newPage(); await p.goto('http://localhost:8945/skarm?stilla'); await p.waitForTimeout(1500); await p.evaluate(() => document.fonts.ready);
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-vf', 'pad=1500:960:0:0:black,format=yuv420p', '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart', '_ut/Drippn menyskarmar v3.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
const n = FPS * SEK;
for (let i = 0; i < n; i++) { await p.evaluate(t => window.sattTid(t), i / FPS); const bild = await p.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(bild)) await new Promise(r => ff.stdin.once('drain', r)); if (i % 150 === 0) console.log(i, '/', n); }
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); srv.close(); console.log('film klar');
