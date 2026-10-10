from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json
URL='https://www.cardmarket.com/en/Pokemon/Products/Singles/Stellar-Miracle/Joltik-V1-sv7032?language=7'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept());page.goto('http://127.0.0.1:3413/PKM-UI-V2.1.html');page.wait_for_selector('#v5tools')
 payload={'sets':[{'name':'Stellar Miracle','setCode':'SV7','language':'ja','cards':[{'name':'Joltik','englishName':'Joltik','number':'032','versions':['Normal','Holo']}]}]}
 assert page.evaluate("async p=>(await fetch('/api/import-bundle',{body:JSON.stringify(p)})).status",payload)==200
 page.reload();page.wait_for_selector('#v5tools');page.locator('nav button').filter(has_text='Sets').click();page.locator('[data-set="1"]').click();expect(page.locator('.cm-link.compact')).to_contain_text('Søg');assert 'searchString=Joltik' in page.locator('.cm-link.compact').get_attribute('href') and 'language=7' in page.locator('.cm-link.compact').get_attribute('href')
 page.locator('.art-button').click();expect(page.locator('.cm-versions>div')).to_have_count(2);page.locator('[data-cm-edit]').click();page.locator('[name="cm-1"]').fill(URL);page.locator('#modal button.primary').click();expect(page.locator('.cm-link.compact')).to_contain_text('Åbn');assert page.locator('.cm-link.compact').get_attribute('href')==URL
 page.locator('[data-cardversion]').select_option('2');expect(page.locator('.cm-link.compact')).to_contain_text('Søg')
 page.locator('nav button').filter(has_text='Import').click();csv='setkode;kortnummer;version;cardmarket_url\r\nSV7;032;normal;'+URL+'\r\nUNKNOWN;001;Normal;'+URL+'\r\nSV7;032;Holo;https://example.com/wrong\r\n'
 page.locator('#cm-file').set_input_files({'name':'links.csv','mimeType':'text/csv','buffer':csv.encode()});expect(page.locator('#cm-preview')).to_contain_text('1 matches');expect(page.locator('#cm-save')).to_be_disabled();page.locator('#cm-replace').check();expect(page.locator('#cm-save')).to_be_enabled();page.locator('#cm-save').click();expect(page.locator('#cm-preview .success')).to_contain_text('1 Cardmarket-links gemt')
 csv='setkode,kortnummer,version,cardmarket_url\nSV7,032,Holo,'+URL+'\nSV7,032,Holo,'+URL+'\n';page.locator('#cm-file').set_input_files({'name':'duplicate.csv','mimeType':'text/csv','buffer':csv.encode()});expect(page.locator('#cm-save')).to_be_disabled();expect(page.locator('#cm-preview')).to_contain_text('Flere CSV-rækker')
 bad={'links':[{'version_id':2,'url':URL},{'version_id':1,'url':'https://www.cardmarket.com.evil.test/en/Pokemon/Products/Singles/x/y'}]}
 assert page.evaluate("async p=>(await fetch('/api/cardmarket-links',{body:JSON.stringify(p)})).status",bad)==400
 state=page.evaluate("async()=>await (await fetch('/api/state')).json()");assert not state['versions'][1].get('cardmarketUrl');assert state['versions'][0]['cardmarketUrl']==URL
 page.reload();page.wait_for_selector('#v5tools');page.locator('#v5tools summary').click()
 with page.expect_download() as info:page.locator('#v5download').click()
 saved=json.loads(Path(info.value.path()).read_text());assert saved['data']['versions'][0]['cardmarketUrl']==URL
 page.locator('#v5restorefile').set_input_files(info.value.path());page.locator('nav button').filter(has_text='Sets').click();page.locator('[data-set="1"]').click();expect(page.locator('.cm-link.compact')).to_contain_text('Åbn')
 page.locator('.art-button').click();page.locator('[data-cm-edit]').click();page.locator('[name="cm-1"]').fill('');page.locator('#modal button.primary').click();expect(page.locator('.cm-link.compact')).to_contain_text('Søg')
 assert not errors,errors;print('PASS: Japanese search fallback, manual per-version exact links, variant isolation, CSV preview/overwrite/invalid/duplicates, atomic URL validation, reload, collection file roundtrip and link removal');b.close()
