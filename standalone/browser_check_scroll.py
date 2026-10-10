import os,shutil
from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':900});page.goto(os.environ['PKM_TEST_URL']);page.wait_for_selector('#v5tools')
 payload={'sets':[{'name':'Long set','setCode':'SCROLL','cards':[{'name':f'Card {i}','number':str(i),'versions':['Normal']} for i in range(1,61)]}]}
 assert page.evaluate("async p=>(await fetch('/api/import-bundle',{body:JSON.stringify(p)})).status",payload)==200
 page.reload();page.wait_for_selector('#v5tools');page.locator('nav button').filter(has_text='Sets').click();page.locator('[data-set="1"]').click()
 for viewport in [{'width':1440,'height':900},{'width':390,'height':844}]:
  page.set_viewport_size(viewport);card=page.locator('.art-button').last;card.scroll_into_view_if_needed();before=page.evaluate('window.scrollY');assert before>900;card.click();expect(page.locator('#modal')).to_be_visible();rect=page.locator('#modal').bounding_box();assert rect['y']>=0 and rect['y']+rect['height']<=viewport['height']+1,rect;assert abs(page.evaluate('window.scrollY')-before)<2
  # Details scroll independently while the underlying set keeps its position.
  page.locator('#modal').evaluate('e=>e.scrollTop=e.scrollHeight');assert abs(page.evaluate('window.scrollY')-before)<2;page.keyboard.press('Escape');expect(page.locator('#modal')).not_to_be_visible();assert abs(page.evaluate('window.scrollY')-before)<2
 print('PASS: details open inside viewport after deep scrolling on desktop/mobile; set position preserved on open, dialog scroll and Escape');b.close()
