from playwright.sync_api import sync_playwright,expect
from PIL import Image
from pathlib import Path
Image.new('RGB',(100,140),'#d8a440').save('/tmp/check-image.png');image=Path('/tmp/check-image.png').read_bytes()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
 page.goto('http://127.0.0.1:3404/PKM-v4.1.html');page.wait_for_selector('nav button[data-page="Import"]')
 result=page.evaluate("async()=>{const r=await fetch('/api/import-sets',{body:JSON.stringify({sets:[{name:'My Set',language:'ja',sourceId:'SV7',setCode:'SV7',cards:[{name:'Ledyba',number:'001',versions:['Normal','Holo']}]}]})});return r.status;}");assert result==200
 page.reload();page.wait_for_selector('h1');page.locator('nav button[data-page="Import"]').click()
 assert page.locator('#imageset').count()==1
 page.locator('#crossfiles').set_input_files({'name':'SV7-001.JPG','mimeType':'','buffer':image})
 expect(page.locator('#crosspreview')).to_contain_text('1 matches')
 page.locator('#crosspreview button.primary').click();expect(page.locator('#crosspreview .success')).to_contain_text('1 billeder gemt')
 first=page.evaluate("async()=>await (await fetch('/api/state')).json()")['cards'][0]['image'];assert first.startswith('data:image/jpeg;base64,')
 page.locator('#crossfiles').set_input_files({'name':'001.png','mimeType':'image/png','buffer':image})
 expect(page.locator('#crosspreview')).to_contain_text('Vælg et set')
 page.locator('#imageset').select_option('1');expect(page.locator('#crosspreview')).to_contain_text('1 matches')
 page.locator('#crosspreview button.primary').click();expect(page.locator('#crosspreview .success')).to_contain_text('1 billeder gemt')
 page.locator('#crossfiles').set_input_files({'name':'SV7-001.jpg','mimeType':'image/jpeg','buffer':b'not an image'})
 page.locator('#crosspreview button.primary').click();expect(page.locator('#crosspreview .error')).to_contain_text('Ingen billeder er gemt')
 assert page.evaluate("async()=>await (await fetch('/api/state')).json()")['cards'][0]['image']==first
 page.locator('#crossfiles').set_input_files([{'name':'UNKNOWN-001.png','mimeType':'image/png','buffer':image},{'name':'readme.txt','mimeType':'text/plain','buffer':b'hi'}])
 expect(page.locator('#crosspreview')).to_contain_text('2 filer valgt');expect(page.locator('#crosspreview')).to_contain_text('Ukendt setkode');expect(page.locator('#crosspreview')).to_contain_text('Ikke et understøttet billedformat')
 page.locator('#crossfiles').set_input_files({'name':'sv7_001.png','mimeType':'image/png','buffer':image});expect(page.locator('#crosspreview')).to_contain_text('1 matches')
 page.locator('#crosspreview button.primary').click();expect(page.locator('#crosspreview .success')).to_be_visible();page.locator('#gotoimported').click();expect(page.locator('.collect-card img')).to_have_count(1);page.wait_for_function("document.querySelector('.collect-card img').naturalWidth>0")
 page.reload();page.wait_for_selector('h1');page.locator('nav button[data-page="Kortkatalog"]').click();page.wait_for_function("document.querySelector('.collect-card img').naturalWidth>0")
 # A decoder which never fires load/error must stop with an actionable message.
 page.locator('nav button[data-page="Import"]').click()
 page.evaluate("window.savedImage=window.Image;window.savedTimeout=window.setTimeout;window.Image=class {set src(x){}};window.setTimeout=(f,ms,...args)=>window.savedTimeout(f,ms===15000?100:ms,...args)")
 page.locator('#crossfiles').set_input_files({'name':'SV7-001.png','mimeType':'image/png','buffer':image})
 page.locator('#crosspreview button.primary').click()
 expect(page.locator('#crosspreview .error')).to_contain_text('for lang tid')
 assert page.evaluate("async()=>await (await fetch('/api/state')).json()")['cards'][0]['image']==first
 page.evaluate('window.Image=window.savedImage;window.setTimeout=window.savedTimeout')
 assert not errors,errors;print('PASS: missing MIME, prefixed and bare names, unknown/unsupported diagnostics, corrupt image rollback, saved image rendering and reload');b.close()
