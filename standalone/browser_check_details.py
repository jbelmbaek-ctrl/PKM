import os,shutil
from playwright.sync_api import sync_playwright,expect
from PIL import Image
from pathlib import Path
import base64
Image.new('RGB',(700,980),'#edc451').save('/tmp/detail-test.jpg')
image='data:image/jpeg;base64,'+base64.b64encode(Path('/tmp/detail-test.jpg').read_bytes()).decode()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000},color_scheme='dark');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(os.environ.get('PKM_TEST_URL','http://127.0.0.1:3413/PKM-UI-V2.2.html'));page.wait_for_selector('#v5tools')
 assert page.evaluate("async image=>{const r=await fetch('/api/import-bundle',{body:JSON.stringify({sets:[{name:'Stellar Miracle','englishName':'Stellar Miracle',setCode:'SV7',cards:[{name:'Ledyba (レディバ)',englishName:'Ledyba',japaneseName:'レディバ',number:'001',image,versions:['Normal','Reverse Holo']},{name:'No Image',number:'002',versions:['Normal']}]}]})});return r.status}",image)==200
 page.reload();page.wait_for_selector('#v5tools');page.locator('nav button').filter(has_text='Sets').click();page.locator('[data-set="1"]').click();page.locator('.art-button[data-card="1"]').click()
 expect(page.locator('#modal')).to_be_visible();expect(page.locator('.card-detail-data')).to_contain_text('Reverse Holo');assert page.locator('#modal').evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(255, 255, 255)'
 small=page.locator('.card-detail-image img').bounding_box()['height'];page.locator('[data-enlargecard]').click();expect(page.locator('#card-image-viewer')).to_be_visible();page.wait_for_function("document.querySelector('#card-image-viewer img').naturalWidth>0");assert page.locator('#card-image-viewer img').bounding_box()['height']>small*1.5
 page.screenshot(path='/tmp/PKM-v5.2-large.png');page.keyboard.press('Escape');expect(page.locator('#card-image-viewer')).not_to_be_visible();expect(page.locator('#modal')).to_be_visible();page.screenshot(path='/tmp/PKM-v5.2-details.png')
 page.locator('.card-detail-close').click();expect(page.locator('#modal')).not_to_be_visible();page.locator('.art-button[data-card="2"]').click();expect(page.locator('.card-detail-noimage')).to_be_visible();assert page.locator('[data-enlargecard]').count()==0
 page.locator('.card-detail-close').click();page.set_viewport_size({'width':390,'height':844});page.locator('.art-button[data-card="1"]').click();assert page.locator('#modal').evaluate('e=>e.scrollWidth<=e.clientWidth');page.locator('[data-enlargecard]').click();expect(page.locator('#card-image-viewer')).to_be_visible();assert page.locator('#card-image-viewer').evaluate('e=>e.scrollWidth<=e.clientWidth');page.locator('#close-card-image').click();expect(page.locator('#modal')).to_be_visible()
 page.locator('[data-addcard="1"]').click();expect(page.locator('#modal h2')).to_have_text('Klargør din samling');assert page.locator('#modal').evaluate("e=>!e.classList.contains('card-detail-dialog')")
 assert not errors,errors;print('PASS: light detail dialog in dark OS mode, versions and stock, enlarged image, Escape returns to details, close, no-image card, mobile fit and registration dialog');b.close()
