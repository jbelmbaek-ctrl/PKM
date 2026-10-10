import http from 'node:http';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
test('local server rejects cross-site writes and rebinding hosts',async()=>{
 const dir=mkdtempSync(path.join(tmpdir(),'pkm-security-')),port=45000+Math.floor(Math.random()*10000);
 const child=spawn(process.execPath,['server.js'],{env:{...process.env,PORT:String(port),PKM_DATA_DIR:dir},stdio:['ignore','pipe','pipe']});
 try{
  await new Promise((resolve,reject)=>{child.stdout.once('data',resolve);child.once('error',reject);child.once('exit',c=>reject(Error('Startup '+c)));});
  const url=`http://127.0.0.1:${port}`;
  assert.equal((await fetch(url+'/api/sets',{method:'POST',headers:{Origin:'https://evil.example','Content-Type':'application/json'},body:'{"name":"attack"}'})).status,403);
  assert.equal(await new Promise((resolve,reject)=>{http.get(url+'/api/state',{headers:{Host:'evil.example:'+port}},r=>{r.resume();resolve(r.statusCode)}).on('error',reject);}),403);
  const response=await fetch(url+'/api/state');assert.equal(response.status,200);assert.equal((await response.json()).sets.length,0);assert.equal(response.headers.get('x-content-type-options'),'nosniff');assert.match(response.headers.get('content-security-policy'),/frame-ancestors 'none'/);
 }finally{if(child.exitCode===null){const done=new Promise(r=>child.once('exit',r));child.kill();await done;}rmSync(dir,{recursive:true,force:true});}
});
