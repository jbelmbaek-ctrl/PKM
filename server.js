import http from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import {mkdirSync,readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));
const dataDir=process.env.PKM_DATA_DIR||path.join(root,'data');
mkdirSync(dataDir,{recursive:true});
const db=new DatabaseSync(path.join(dataDir,'catalog.sqlite'));
db.exec(`PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sets(id INTEGER PRIMARY KEY,name TEXT NOT NULL,game TEXT NOT NULL DEFAULT '',year TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY,set_id INTEGER NOT NULL REFERENCES sets(id),name TEXT NOT NULL,number TEXT NOT NULL,image TEXT NOT NULL DEFAULT '',UNIQUE(set_id,number));
CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY,card_id INTEGER NOT NULL REFERENCES cards(id),name TEXT NOT NULL,UNIQUE(card_id,name));
CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS holdings(id INTEGER PRIMARY KEY,version_id INTEGER NOT NULL REFERENCES versions(id),location_id INTEGER NOT NULL REFERENCES locations(id),quantity INTEGER NOT NULL CHECK(quantity>0),condition TEXT NOT NULL);
`);
const state=()=>Object.fromEntries(['sets','cards','versions','locations','holdings'].map(t=>[t,db.prepare('SELECT * FROM '+t).all()]));
function required(v,label){if(typeof v!=='string'||!v.trim())throw Error(label+' skal udfyldes');return v.trim();}
function addCard(p){const set=Number(p.set_id);if(!db.prepare('SELECT id FROM sets WHERE id=?').get(set))throw Error('Vælg et gyldigt set');const name=required(p.name,'Navn'),number=required(p.number,'Kortnummer');const image=String(p.image||'');if(image&&!/^https?:\/\//.test(image)&&!/^data:image\/(png|jpeg|webp|gif);base64,/.test(image))throw Error('Ugyldigt billede');const names=[...new Set((p.versions||['Normal']).map(v=>required(v,'Version')))];if(!names.length)throw Error('Tilføj mindst én version');const id=Number(db.prepare('INSERT INTO cards(set_id,name,number,image) VALUES(?,?,?,?)').run(set,name,number,image).lastInsertRowid);for(const v of names)db.prepare('INSERT INTO versions(card_id,name) VALUES(?,?)').run(id,v);}
http.createServer(async(req,res)=>{try{
res.setHeader('X-Content-Type-Options','nosniff');
res.setHeader('Referrer-Policy','no-referrer');
res.setHeader('Content-Security-Policy',"default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'");
const expectedPort=String(process.env.PORT||3000);
if(!['127.0.0.1:'+expectedPort,'localhost:'+expectedPort].includes(req.headers.host)||req.headers.origin&&!['http://127.0.0.1:'+expectedPort,'http://localhost:'+expectedPort].includes(req.headers.origin)){res.writeHead(403);res.end('Adgang afvist');return;}

if(req.url==='/api/state'&&req.method==='GET'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(state()));return;}
if(req.url?.startsWith('/api/')&&req.method==='POST'){let raw='';for await(const chunk of req){raw+=chunk;if(raw.length>15e6)throw Error('Filen er for stor');}const p=JSON.parse(raw);db.exec('BEGIN');try{switch(req.url){
case '/api/sets':db.prepare('INSERT INTO sets(name,game,year) VALUES(?,?,?)').run(required(p.name,'Setnavn'),String(p.game||''),String(p.year||''));break;
case '/api/locations':db.prepare('INSERT INTO locations(name) VALUES(?)').run(required(p.name,'Lokation'));break;
case '/api/cards':addCard(p);break;
case '/api/import':if(!Array.isArray(p.cards)||!p.cards.length)throw Error('Ingen kort at importere');for(const c of p.cards)addCard(c);break;
case '/api/versions':db.prepare('INSERT INTO versions(card_id,name) VALUES(?,?)').run(Number(p.card_id),required(p.name,'Version'));break;
case '/api/holdings':{const q=Number(p.quantity);if(!Number.isSafeInteger(q)||q<1)throw Error('Antal skal være et positivt heltal');db.prepare('INSERT INTO holdings(version_id,location_id,quantity,condition) VALUES(?,?,?,?)').run(Number(p.version_id),Number(p.location_id),q,required(p.condition,'Stand'));break;}
case '/api/move':{if(!db.prepare('SELECT id FROM holdings WHERE id=?').get(Number(p.id)))throw Error('Beholdning findes ikke');db.prepare('UPDATE holdings SET location_id=? WHERE id=?').run(Number(p.location_id),Number(p.id));break;}
case '/api/remove':db.prepare('DELETE FROM holdings WHERE id=?').run(Number(p.id));break;
default:throw Error('Ukendt handling');}db.exec('COMMIT');}catch(e){db.exec('ROLLBACK');throw e;}res.setHeader('Content-Type','application/json');res.end(JSON.stringify(state()));return;}
const files={'/':'index.html','/app.js':'app.js','/style.css':'style.css'};const f=files[req.url];if(!f){res.writeHead(404);res.end();return;}res.setHeader('Content-Type',f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':'text/html');res.end(readFileSync(path.join(root,'public',f)));
}catch(e){res.writeHead(400,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message.includes('UNIQUE')?'Denne post findes allerede':e.message.includes('FOREIGN KEY')?'Vælg en gyldig version og lokation':e.message}));}}).listen(Number(process.env.PORT||3000),'127.0.0.1',()=>console.log('PKM startet på port '+(process.env.PORT||3000)));
