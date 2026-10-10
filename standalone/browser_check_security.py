from playwright.sync_api import sync_playwright
import os,shutil,json
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page();messages=[];page.on('dialog',lambda d:(messages.append(d.message),d.accept()));page.goto(os.environ['PKM_TEST_URL']);page.wait_for_selector('#v5tools')
 assert page.locator('meta[http-equiv="Content-Security-Policy"]').count()==1
 page.evaluate("()=>{const s=document.createElement('script');s.textContent='window.injected=true';document.body.append(s)}")
 assert page.evaluate('window.injected===undefined')
 assert page.evaluate("async()=> (await fetch('/api/sets',{body:JSON.stringify({name:'Original'})})).status")==200
 original=page.evaluate("async()=>await(await fetch('/api/state')).json()")
 replacement={**original,'sets':[{'id':1,'name':'Replacement'}]}
 def load(data):page.locator('#v5restorefile').set_input_files({'name':'test.pkm','mimeType':'application/json','buffer':json.dumps({'format':'pkm-collection-v2','data':data}).encode()})
 load(replacement);page.wait_for_function("()=>document.querySelector('#content').textContent.includes('Replacement')")
 page.locator('#v5tools summary').click();page.locator('#pkm-recovery').click();page.wait_for_function("()=>document.querySelector('#content').textContent.includes('Original')")
 assert page.evaluate("async()=>await(await fetch('/api/state')).json()")['sets']==original['sets']
 bad={**replacement,'cards':[{'id':1,'set_id':1,'name':'Bad','number':'001','image':'data:image/svg+xml,<svg onload=alert(1) />'}]}
 with page.expect_event('dialog') as error:load(bad)
 assert 'usikkert' in error.value.message;assert page.evaluate("async()=>await(await fetch('/api/state')).json()")==original
 page.reload();page.wait_for_selector('#v5tools');assert page.evaluate("async()=>await(await fetch('/api/state')).json()")==original
 print('PASS: CSP blocks injected script, pre-restore snapshot, recovery, unsafe-image rejection without data loss, persistence');b.close()
