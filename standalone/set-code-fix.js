const previousNameChanges=oldNameChanges;
oldNameChanges=function correctSV1Codes(){const changes=previousNameChanges();for(const s of db.sets){const name=(s.englishName||s.name||'').trim();let code='';if(s.sourceId==='SV1S'||/^Scarlet ex(?:\s*\(|$)/i.test(name)||s.japaneseName==='スカーレットex')code='SV1S';if(s.sourceId==='SV1V'||/^Violet ex(?:\s*\(|$)/i.test(name)||s.japaneseName==='バイオレットex')code='SV1V';if(!code||(s.setCode===code))continue;const change=changes.sets.find(c=>c.id===s.id);if(change)change.setCode=code;else changes.sets.push({id:s.id,name:s.name,englishName:s.englishName||name,setCode:code});}return changes;};
const beforeFullSetCodes=renderSets;
renderSets=function renderFullSetCodes(){beforeFullSetCodes();for(const row of document.querySelectorAll('.set-row-table tbody tr')){const s=db.sets.find(s=>s.id===Number(row.querySelector('[data-set]').dataset.set));row.querySelector('.set-symbol').textContent=s.setCode||s.sourceId||'◈';}};
await upgradeNames();render();
