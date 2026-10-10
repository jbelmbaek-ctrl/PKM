import os,shutil,json
from pathlib import Path
from PIL import Image
from io import BytesIO
image=BytesIO();Image.new('RGB',(100,140),'#dda440').save(image,format='PNG')
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(os.environ['PKM_TEST_URL']);page.wait_for_selector('#v5tools')
 page.locator('nav button').filter(has_text='Import').click()
 package={'sets':[{'name':'Stellar Miracle','setCode':'SV7','language':'ja','cards':[{'name':'Joltik','number':'032','versions':['Normal','Holo']}]}]}
 page.locator('#setpackagefile').set_input_files({'name':'set.json','mimeType':'application/json','buffer':json.dumps(package).encode()});page.locator('#confirmsetimport').click()
 # Both images and links remain staged until explicit final commit.
 page.locator('#v5stagedfiles').set_input_files({'name':'SV7-032.png','mimeType':'image/png','buffer':image.getvalue()});expect(page.locator('#v5matchsummary')).to_contain_text('1 matches');page.locator('#v5finish').click()
 state=lambda:page.evaluate("async()=>await(await fetch('/api/state')).json()")
 assert not state()['sets']
 url='https://www.cardmarket.com/en/Pokemon/Products/Singles/Stellar-Miracle/Joltik-V1-sv7032?language=7'
 csv='setkode;kortnummer;version;cardmarket_url\nSV7;032;Normal;'+url+'\nSV7;032;Holo;https://example.com/bad\n'
 page.locator('#bundle-links-file').set_input_files({'name':'links.csv','mimeType':'text/csv','buffer':csv.encode()});expect(page.locator('#bundle-links-preview')).to_contain_text('1 matches');expect(page.locator('#bundle-links-next')).to_be_disabled();assert not state()['sets']
 page.locator('#bundle-links-skip').check();page.locator('#bundle-links-next').click();assert not state()['sets'];expect(page.locator('#setpackagepreview')).to_contain_text('1 Cardmarket-links')
 page.locator('#bundle-confirm-back').click();expect(page.locator('#bundle-links-preview')).to_contain_text('1 links er allerede valgt');page.locator('#bundle-links-next').click()
 # Simulate a failed atomic write, then retry with the same staged package.
 page.evaluate("()=>{window.realFetch=window.fetch;window.fetch=async(u,o)=>u==='/api/import-bundle'?new Response(JSON.stringify({error:'Testfejl'}),{status:400}):window.realFetch(u,o)}")
 page.locator('#bundle-save').click();expect(page.locator('#bundle-save-error')).to_contain_text('Testfejl');assert not state()['sets'];page.evaluate('()=>{window.fetch=window.realFetch}')
 page.locator('#bundle-save').click();expect(page.locator('.success')).to_contain_text('1 Cardmarket-links');saved=state();assert len(saved['sets'])==1 and saved['cards'][0]['image'].startswith('data:image/');assert saved['versions'][0]['cardmarketUrl']==url;assert not saved['versions'][1].get('cardmarketUrl')
 bad={'sets':[{'name':'Invalid bundle','setCode':'BAD','cards':[{'name':'Bad card','number':'001','versions':['Normal'],'cardmarketLinks':[{'version':'Normal','url':'https://evil.example/link'}]}]}]}
 assert page.evaluate("async p=>(await fetch('/api/import-bundle',{body:JSON.stringify(p)})).status",bad)==400;assert state()==saved
 page.reload();page.wait_for_selector('#v5tools');assert state()==saved;assert not errors,errors
 print('PASS: no early set creation, staged images and per-version links, invalid rows block commit, back preserves links, failed save and retry, persistence');b.close()
