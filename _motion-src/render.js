// Export MP4 (réseaux sociaux) d'une animation « motion-design » : rend l'animation image par image
// à partir d'une page du site construit (jekyll build) et mixe la voix-off.
// Usage : NODE_PATH=<playwright> node _motion-src/render.js <url_page> <voix.mp3> <sortie.mp4>
//   ex. : node _motion-src/render.js http://localhost:4005/analyses/<slug>/ uploads/motion/<nom>/voix.mp3 uploads/motion/<nom>/<nom>.mp4
// ONLY=10,60 : n'écrit que des images de contrôle (still-*.png dans le dossier courant, à ne pas commiter).
const {chromium}=require('playwright');const {execSync}=require('child_process');const fs=require('fs'),path=require('path');
const FPS=24,[url,mp3,out]=process.argv.slice(2),only=process.env.ONLY?process.env.ONLY.split(',').map(Number):null;
const tmp=fs.mkdtempSync(path.join(process.env.TMPDIR||'/tmp','mx-'));
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
 const p=await b.newPage({viewport:{width:1280,height:720}});
 await p.goto(url,{waitUntil:'domcontentloaded'});await p.waitForSelector('.mx-start:not([hidden])',{timeout:20000});
 await p.evaluate(()=>document.fonts.ready);
 // le cadre 16:9 occupe tout l'écran 1280×720 ; commandes et reste de la page masqués
 await p.addStyleTag({content:'.mx-frame{position:fixed!important;inset:0!important;width:1280px!important;height:720px!important;z-index:2147483647!important;border:0!important;border-radius:0!important}.mx-start{display:none!important}.mx-sub{transition:none!important}'});
 await p.evaluate(()=>document.querySelector('.mx').classList.add('started'));
 const dur=await p.evaluate(src=>fetch(src+'/timeline.json').then(r=>r.json()).then(j=>j.total),await p.evaluate(()=>document.querySelector('.mx').dataset.src));
 const seek=t=>p.evaluate(t=>document.querySelector('.mx').__mxSeek(t),t);
 if(only){for(const t of only){await seek(t);await p.screenshot({path:`./still-${t}.png`});}await b.close();return;}
 for(let i=0;i<Math.ceil(dur*FPS);i++){await seek(i/FPS);await p.screenshot({path:`${tmp}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});}
 await b.close();
 execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${tmp}/f%05d.jpg -i ${mp3} -c:v libx264 -pix_fmt yuv420p -crf 22 -c:a aac -b:a 128k -shortest -movflags +faststart ${out}`);
 fs.rmSync(tmp,{recursive:true});console.log('ok',out,dur.toFixed(1)+'s');
})();
