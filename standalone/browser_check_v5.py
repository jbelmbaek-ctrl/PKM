import os,shutil
from playwright.sync_api import sync_playwright,expect
from PIL import Image
from pathlib import Path
import json
Image.new('RGB',(100,140),'#dda440').save('/tmp/v5-card.png')
image=Path('/tmp/v5-card.png').read_bytes()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
 page.goto(os.environ.get('PKM_TEST_URL','http://127.0.0.1:3413/PKM-UI-V2.3.html'));page.wait_for_selector('#v5tools');assert page.locator('nav button').count()==5
 page.locator('nav button').filter(has_text='Import').click()
 package={'sets':[{'name':'Test Set','englishName':'Test Set','setCode':'TEST','cards':[{'name':'Test Card','englishName':'Test Card','number':'001','versions':['Normal','Holo']}]}]}
 page.locator('#setpackagefile').set_input_files({'name':'set.json','mimeType':'application/json','buffer':json.dumps(package).encode()})
 page.locator('#confirmsetimport').click();page.locator('#v5stagedfiles').set_input_files({'name':'TEST-001.png','mimeType':'image/png','buffer':image});expect(page.locator('#v5matchsummary')).to_contain_text('1 matches')
 assert page.evaluate("async()=> (await (await fetch('/api/state')).json()).cards.length")==0
 page.evaluate('window.originalConfirm=window.confirm;window.confirm=()=>false')
 page.locator('#v5finish').click();expect(page.locator('#bundle-links-file')).to_be_visible();assert page.evaluate("async()=> (await (await fetch('/api/state')).json()).sets.length")==0;page.locator('#bundle-links-next').click();page.locator('#bundle-save').click();expect(page.locator('h1')).to_have_text('Sets');expect(page.locator('.success')).to_contain_text('Import afsluttet')
 page.evaluate('window.confirm=window.originalConfirm')
 state=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert state['cards'][0]['image'].startswith('data:image/jpeg;')
 page.locator('[data-set="1"]').click();page.wait_for_function("document.querySelector('.collect-card img').naturalWidth>0")
 page.locator('.art-button[data-card="1"]').click();page.locator('[data-v5name="1"]').click();page.locator('[name="englishName"]').fill('Corrected Card');page.locator('#modal button.primary').click();expect(page.locator('.cardname')).to_contain_text('Corrected Card')
 result=page.evaluate("async()=>{for(const [kind,data] of [['locations',{name:'Binder'}],['holdings',{version_id:1,location_id:1,quantity:3,condition:'Near Mint'}],['move',{id:1,location_id:1}],['remove',{id:1}],['undo',{}]]){const r=await fetch('/api/'+kind,{body:JSON.stringify(data)});if(!r.ok)throw Error(await r.text());}return (await (await fetch('/api/state')).json());}");assert result['holdings'][0]['quantity']==3;assert len(result['auditLog'])==3
 page.reload();page.wait_for_selector('#v5tools');page.locator('nav button').filter(has_text='Samling').click();page.locator('[data-page="Historik"]').click();expect(page.locator('h1')).to_have_text('Historik')
 page.locator('#v5tools summary').click()
 with page.expect_download() as info:page.locator('#v5download').click()
 path=info.value.path();saved=json.loads(Path(path).read_text());assert saved['data']['cards'][0]['image'].startswith('data:');assert saved['format']=='pkm-collection-v2'
 page.locator('#v5restorefile').set_input_files(path);expect(page.locator('h1')).to_have_text('Historik')
 # Old JSON backup compatibility and corrupt input preservation.
 old={'format':'pkm-backup-v1','data':saved['data']}
 page.locator('#v5restorefile').set_input_files({'name':'legacy.json','mimeType':'application/json','buffer':json.dumps(old).encode()})
 expect(page.locator('h1')).to_have_text('Historik')
 page.locator('nav button').filter(has_text='Import').click();page.get_by_text('Kun billeder til eksisterende sets',exact=True).click()
 page.locator('#crossfiles').set_input_files({'name':'unknown.png','mimeType':'image/png','buffer':image})
 page.locator('[data-v5match="0"]').select_option('1');expect(page.locator('#v5matchsummary')).to_contain_text('1 matches')
 page.locator('#v5finish').click();expect(page.locator('#crosspreview .success')).to_be_visible()
 before=page.evaluate("async()=>await (await fetch('/api/state')).json()")
 page.locator('#crossfiles').set_input_files({'name':'TEST-001.png','mimeType':'image/png','buffer':b'invalid'})
 page.locator('#v5finish').click();expect(page.locator('#v5imageerror')).to_contain_text('browseren kunne ikke læse')
 after=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert before==after
 # Invalid bundles never leave partially imported sets behind.
 invalid={'sets':[{'name':'Another Set','cards':[{'name':'Valid','number':'1','versions':['Normal']},{'name':'Invalid','number':'1','versions':['Normal']}]}]}
 assert page.evaluate("async p=>(await fetch('/api/import-bundle',{body:JSON.stringify(p)})).status",invalid)==400
 assert before==page.evaluate("async()=>await (await fetch('/api/state')).json()")
 page.set_viewport_size({'width':390,'height':844});page.locator('#ui-menu').click();page.locator('nav button').filter(has_text='Sets').click();page.locator('[data-set="1"]').click()
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path='/tmp/v5-gallery-mobile.png')
 assert not errors,errors
 print('PASS: five menus, staged set+image import, image rendering, custom name, stock history and undo, reload, collection file with images and restore');b.close()
