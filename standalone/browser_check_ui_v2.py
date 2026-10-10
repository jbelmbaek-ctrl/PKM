import os,shutil
from playwright.sync_api import sync_playwright,expect
from pathlib import Path
from PIL import Image,ImageDraw
import base64,json
img=Image.new('RGB',(315,440),'#f0c96b');draw=ImageDraw.Draw(img);draw.rounded_rectangle((12,12,303,428),radius=12,fill='#e2ecdc');draw.rectangle((24,60,290,265),fill='#8bb3a5');draw.ellipse((86,98,232,241),fill='#e4a964');draw.line((48,303,270,303),fill='#94aa9d',width=5);draw.line((48,330,240,330),fill='#94aa9d',width=5);img.save('/tmp/ui-test-card.png');image='data:image/png;base64,'+base64.b64encode(Path('/tmp/ui-test-card.png').read_bytes()).decode()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1512,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept());page.goto(os.environ.get('PKM_TEST_URL','http://127.0.0.1:3413/PKM-UI-V2.2.html'));page.wait_for_selector('.ui-topbar')
 page.wait_for_function("document.fonts.check('16px \"PKM Inter\"')")
 assert page.locator('aside').count()==0;assert page.locator('nav button').count()==5;assert page.locator('main').evaluate("e=>getComputedStyle(e).marginLeft")!='224px'
 cards=[{'name':n+' (テスト)','englishName':n,'japaneseName':'テスト','number':str(i+1).zfill(3),'image':image if i<8 else '', 'versions':['Normal','Holo']} for i,n in enumerate(['Ledyba','Ledian','Ariados','Venonat','Venomoth','Oddish','Spinarak','Crobat','Chinchou','Lanturn','Hoppip','Skiploom'])]
 payload={'sets':[{'name':'Stellar Miracle (ステラミラクル)','englishName':'Stellar Miracle','japaneseName':'ステラミラクル','setCode':'SV7','sourceId':'SV7','language':'ja','series':'Scarlet & Violet','releaseDate':'2024-07-19','cards':cards}]}
 assert page.evaluate("async p=>(await fetch('/api/import-bundle',{body:JSON.stringify(p)})).status",payload)==200
 for kind,data in [('locations',{'name':'Mappe A'}),('locations',{'name':'Kasse B'}),('holdings',{'version_id':1,'location_id':1,'quantity':3,'condition':'Near Mint'}),('holdings',{'version_id':2,'location_id':2,'quantity':2,'condition':'Good'})]:assert page.evaluate("async x=>(await fetch('/api/'+x.kind,{body:JSON.stringify(x.data)})).status",{'kind':kind,'data':data})==200
 page.reload();page.wait_for_selector('.ui-topbar');page.screenshot(path='/tmp/PKM-UI-V2-overblik.png')
 page.locator('nav button').filter(has_text='Sets').click();expect(page.locator('.ui-code')).to_have_text('SV7');page.locator('[data-set="1"]').click();expect(page.locator('.collect-card')).to_have_count(12);expect(page.locator('#ui-set-summary')).to_contain_text('5 eksemplarer');assert page.locator('#ui-set-summary').count()==1
 assert page.locator('.ui-catalog-toolbar .catalog-tabs').count()==1;page.screenshot(path='/tmp/PKM-UI-V2-kort.png')
 page.locator('.v5-register summary').click();page.locator('#registerlocation').select_option('1');first=page.locator('.collect-card').first;expect(first.locator('.ui-version-line')).to_contain_text('5 i alt');expect(first.locator('.card-counter strong')).to_have_text('3 her')
 first.locator('[data-delta="1"]').click();expect(first.locator('.card-counter strong')).to_have_text('4 her');page.locator('#ui-extra-filters summary').click();page.locator('#versionfilter').select_option('Holo');expect(first.locator('[data-cardversion]')).to_have_value('2');expect(first.locator('.card-counter strong')).to_have_text('0 her');page.locator('#versionfilter').select_option('');page.locator('#ui-extra-filters summary').click()
 page.locator('#search').fill('Ledian');expect(page.locator('.collect-card')).to_have_count(1);page.locator('#search').fill('');expect(page.locator('.collect-card')).to_have_count(12)
 page.locator('[data-view="table"]').click();expect(page.locator('#cards tbody tr')).to_have_count(12);page.locator('[data-view="grid"]').click();expect(page.locator('.collect-card')).to_have_count(12)
 page.locator('nav button').filter(has_text='Samling').click();expect(page.locator('#stocktable tbody tr')).to_have_count(2);page.locator('#stocklocation').select_option('1');expect(page.locator('#stocktable tbody tr')).to_have_count(1)
 with page.expect_download() as info:page.locator('[data-stockexport="filtered"]').click()
 csv=Path(info.value.path()).read_text();assert 'Setkode' in csv and 'SV7' in csv and 'Mappe A' in csv and 'Kasse B' not in csv
 page.locator('[data-page="Historik"]').click();page.locator('[data-v5undo]').click();expect(page.locator('h1')).to_have_text('Historik')
 page.locator('[data-page="Masseregistrering"]').click();page.locator('#massset').select_option('1');page.locator('#masslocation').select_option('1');page.locator('[data-massquantity="1"]').fill('2');page.locator('#masssave').click();expect(page.locator('#masssummary')).to_contain_text('0 nye')
 state=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert next(h for h in state['holdings'] if h['id']==1)['quantity']==5
 page.locator('[data-page="Lagerliste"]').click();page.locator('#stocklocation').select_option('');page.locator('[data-move="1"]').click();page.locator('#modal [name="location_id"]').select_option('2');page.locator('#modal button.primary').click();expect(page.locator('#modal')).not_to_be_visible()
 state=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert next(h for h in state['holdings'] if h['id']==1)['location_id']==2
 page.locator('[data-page="Historik"]').click();page.locator('[data-v5undo]').click();state=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert next(h for h in state['holdings'] if h['id']==1)['location_id']==1
 page.locator('[data-page="Lagerliste"]').click();page.locator('[data-remove="1"]').click();expect(page.locator('#stocktable tbody tr')).to_have_count(1);page.locator('[data-page="Historik"]').click();page.locator('[data-v5undo]').click();state=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert next(h for h in state['holdings'] if h['id']==1)['quantity']==5
 for w in [390,760,1024,1512]:
  page.set_viewport_size({'width':w,'height':950})
  if w<=760:page.locator('#ui-menu').click()
  page.locator('nav button').filter(has_text='Sets').click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('sets',w)
  page.locator('[data-set="1"]').click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),('cards',w)
  if w==390:page.screenshot(path='/tmp/PKM-UI-V2-mobil.png',full_page=True)
 assert not errors,errors;print('PASS: embedded Inter, top navigation, summary and unified filters, scoped quantities, version filtering, search, gallery/list, stock CSV, undo, responsive sets/cards at four widths');b.close()
