import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
test('catalogue, variants, stock, move, atomic import and persistence',async()=>{
const dir=mkdtempSync(path.join(tmpdir(),'pkm-test-')),port=34000+Math.floor(Math.random()*10000);let child;
const start=async()=>{child=spawn(process.execPath,['server.js'],{env:{...process.env,PORT:String(port),PKM_DATA_DIR:dir},stdio:['ignore','pipe','pipe']});await new Promise((resolve,reject)=>{child.stdout.once('data',resolve);child.once('error',reject);child.once('exit',c=>reject(Error('Startup failed '+c)));});};
const stop=async()=>{const done=new Promise(r=>child.once('exit',r));child.kill();await done;};
const call=async(route,p)=>{const r=await fetch(`http://127.0.0.1:${port}/api/${route}`,p?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)}:{});return {status:r.status,data:await r.json()};};
try{await start();assert.equal((await call('state')).data.cards.length,0);
await call('sets',{name:'Test Set',game:'Pokémon',year:'2026'});await call('locations',{name:'Kasse A'});await call('locations',{name:'Mappe B'});
let r=await call('cards',{set_id:1,name:'Pikachu',number:'025',versions:['Normal','Holo']});assert.equal(r.status,200);assert.equal(r.data.versions.length,2);
r=await call('holdings',{version_id:2,location_id:1,quantity:3,condition:'Near Mint'});assert.equal(r.data.holdings[0].quantity,3);
assert.equal((await call('holdings',{version_id:2,location_id:1,quantity:-1,condition:'Good'})).status,400);
r=await call('move',{id:1,location_id:2});assert.equal(r.data.holdings[0].location_id,2);
r=await call('import',{cards:[{set_id:1,name:'New',number:'026'},{set_id:1,name:'Duplicate',number:'025'}]});assert.equal(r.status,400);assert.equal((await call('state')).data.cards.length,1);
r=await call('import',{cards:[{set_id:1,name:'New',number:'026',versions:['Normal','Reverse Holo']}]});assert.equal(r.data.cards.length,2);
await stop();await start();r=await call('state');assert.equal(r.data.cards.length,2);assert.equal(r.data.holdings[0].quantity,3);
r=await call('remove',{id:1});assert.equal(r.data.holdings.length,0);assert.equal(r.data.cards.length,2);
assert.equal((await fetch(`http://127.0.0.1:${port}/`)).status,200);
}finally{if(child?.exitCode===null)await stop();rmSync(dir,{recursive:true,force:true});}
});
