// The whole package remains in memory until the final confirmation.
function showBundleLinks(payload,imageCount,skippedImages){
 importStep=4;updateWizardSteps();
 const target=$('#setpackagepreview');let rows=payload.flatMap(s=>s.cards.flatMap(card=>(card.cardmarketLinks||[]).map(l=>({card,version:l.version,url:l.url,valid:true})))),fileError='',reading=false,generation=0;
 target.innerHTML='<section class="panel"><h2>4. Tilføj Cardmarket-links</h2><p>Settet er endnu ikke oprettet. Vælg din links-fil, eller fortsæt uden links.</p><p>CSV-kolonner: setkode, kortnummer, version, cardmarket_url.</p><input id="bundle-links-file" type="file" accept=".csv,text/csv"><button id="bundle-links-clear">Fortsæt uden links</button><div id="bundle-links-preview"></div><label class="checkbox"><input id="bundle-links-skip" type="checkbox"> Spring rækker med fejl over</label><div id="bundle-links-error" class="error" role="alert"></div><button id="bundle-links-back">← Tilbage til billeder</button><button class="primary" id="bundle-links-next">Kontrollér import →</button></section>';
 const update=()=>{$('#bundle-links-error').textContent=fileError;$('#bundle-links-next').disabled=reading||!!fileError||rows.some(r=>!r.valid)&&!$('#bundle-links-skip').checked;};
 if(rows.length)$('#bundle-links-preview').textContent=rows.length+' links er allerede valgt. Behold dem, eller vælg en anden fil.';
 $('#bundle-links-skip').onchange=update;
 $('#bundle-links-back').onclick=()=>{showPackagePreview();$('#confirmsetimport').click();};
 $('#bundle-links-clear').onclick=()=>{generation++;rows=[];fileError='';reading=false;$('#bundle-links-file').value='';$('#bundle-links-preview').innerHTML='<p>Du fortsætter uden links. De kan importeres senere.</p>';update();};
 $('#bundle-links-file').onchange=async e=>{const run=++generation;rows=[];fileError='';reading=true;$('#bundle-links-skip').checked=false;$('#bundle-links-preview').innerHTML='Læser links…';update();try{
  const file=e.target.files[0];if(!file){reading=false;update();return;}
  const text=await file.text();if(run!==generation||!target.isConnected)return;
  const first=text.replace(/^\uFEFF/,'').split(/\r?\n/)[0],sep=first.split(';').length>first.split(',').length?';':',',parsed=parseCSV(text,sep),headers=parsed.shift()?.map(cmKey);
  if(!['setkode','kortnummer','version','cardmarket_url'].every(h=>headers?.includes(h))||new Set(headers).size!==headers.length)throw Error('CSV skal indeholde setkode, kortnummer, version og cardmarket_url én gang hver');
  rows=parsed.filter(r=>r.some(c=>c.trim())).map((row,i)=>{const p=Object.fromEntries(headers.map((h,j)=>[h,row[j]||''])),r={line:i+2,p,valid:false};try{
   const sets=payload.filter(s=>cmKey(s.setCode||s.sourceId)===cmKey(p.setkode));if(sets.length!==1)throw Error('Setkode findes ikke entydigt i denne import');
   const cards=sets[0].cards.filter(c=>normalizedNumber(c.number)===normalizedNumber(p.kortnummer));if(cards.length!==1)throw Error('Kortnummer findes ikke entydigt');
   const names=cards[0].versions||['Normal'],vs=p.version.trim()?names.filter(n=>cmKey(n)===cmKey(p.version)):names.length===1?names:[];if(vs.length!==1)throw Error('Version mangler eller findes ikke');
   Object.assign(r,{card:cards[0],version:vs[0],url:cmNormalize(p.cardmarket_url,sets[0].language||'ja'),valid:true,status:'Klar'});
  }catch(err){r.status=err.message;}return r;});
  for(const r of rows)if(r.valid&&rows.filter(x=>x.valid&&x.card===r.card&&x.version===r.version).length>1)r.duplicate=true;
  for(const r of rows)if(r.duplicate){r.valid=false;r.status='Flere CSV-rækker matcher samme version';}
  if(!rows.length)throw Error('CSV-filen indeholder ingen links');
  $('#bundle-links-preview').innerHTML=`<p>${rows.filter(r=>r.valid).length} matches · ${rows.filter(r=>!r.valid).length} rækker med fejl</p>`+table(['LINJE','KORT / VERSION','STATUS'],rows.map(r=>`<tr><td>${r.line}</td><td>${esc(r.p.setkode)}-${esc(r.p.kortnummer)} · ${esc(r.p.version)}</td><td>${esc(r.status)}</td></tr>`));decorateTables();
 }catch(err){if(run!==generation||!target.isConnected)return;fileError=err.message;$('#bundle-links-preview').innerHTML='';}finally{if(run===generation&&target.isConnected){reading=false;update();}}};
 $('#bundle-links-next').onclick=()=>{if($('#bundle-links-next').disabled)return;const chosen=rows.filter(r=>r.valid);for(const s of payload)for(const c of s.cards)c.cardmarketLinks=[];for(const r of chosen)r.card.cardmarketLinks.push({version:r.version,url:r.url});showBundleConfirmation(payload,imageCount,skippedImages,chosen.length,rows.length-chosen.length);};
 update();
}
function showBundleConfirmation(payload,imageCount,skippedImages,linkCount,skippedLinks){
 importStep=5;updateWizardSteps();$('#setpackagepreview').innerHTML=`<section class="panel"><h2>5. Kontrollér og afslut</h2><p>Intet er gemt endnu.</p><p>${payload.length} sets · ${sum(payload,s=>s.cards.length)} kort · ${imageCount} billeder · ${linkCount} Cardmarket-links</p><p>${skippedImages} billedfiler og ${skippedLinks} linkrækker springes over.</p><div id="bundle-save-error" class="error" role="alert"></div><button id="bundle-confirm-back">← Tilbage til links</button><button class="primary" id="bundle-save">Opret sets, billeder og links</button></section>`;
 $('#bundle-confirm-back').onclick=()=>showBundleLinks(payload,imageCount,skippedImages);
 $('#bundle-save').onclick=async()=>{const button=$('#bundle-save');button.disabled=true;$('#bundle-confirm-back').disabled=true;button.textContent='Gemmer import…';try{
  await save('import-bundle',{sets:payload});selectedImportSets.clear();importPackages=[];stagedFiles=[];page='Sets';render();const success=document.createElement('p');success.className='success';success.setAttribute('role','status');success.textContent=`Import afsluttet: ${payload.length} sets, ${sum(payload,s=>s.cards.length)} kort, ${imageCount} billeder og ${linkCount} Cardmarket-links gemt og kontrolleret.`;$('.title').after(success);
 }catch(err){$('#bundle-save-error').textContent=err.message;button.disabled=false;$('#bundle-confirm-back').disabled=false;button.textContent='Prøv import igen';}};
}
