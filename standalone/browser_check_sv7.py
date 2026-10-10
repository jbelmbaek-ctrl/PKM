"""Regression: the shipped CSV must match the actual Japanese SV7 catalogue before creation."""
import os,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('PKM_BROWSER_EXECUTABLE') or shutil.which('chromium') or shutil.which('google-chrome'),headless=True,args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(os.environ['PKM_TEST_URL']);page.wait_for_selector('#v5tools')
 page.locator('nav button').filter(has_text='Import').click();assert page.locator('#cm-file').count()==0
 page.locator('#librarysearch').fill('SV7');page.locator('[data-importset="SV7"]').check();page.locator('#previewsets').click();page.locator('#confirmsetimport').click();page.locator('#v5finish').click()
 state=lambda:page.evaluate("async()=>await(await fetch('/api/state')).json()")
 assert not state()['sets'];page.locator('#bundle-links-file').set_input_files(str(root/'downloads/Cardmarket-SV7.csv'));expect(page.locator('#bundle-links-preview')).to_contain_text('135 matches · 0 rækker med fejl');assert not state()['sets']
 page.locator('#bundle-links-next').click();expect(page.locator('#setpackagepreview')).to_contain_text('135 Cardmarket-links');assert not state()['sets'];page.locator('#bundle-save').click();expect(page.locator('.success')).to_contain_text('135 Cardmarket-links')
 saved=state();assert len(saved['sets'])==1 and saved['sets'][0]['setCode']=='SV7';assert len(saved['cards'])==135;assert sum(bool(v.get('cardmarketUrl')) for v in saved['versions'])==135;assert all('language=7' in v['cardmarketUrl'] for v in saved['versions'] if v.get('cardmarketUrl'))
 page.reload();page.wait_for_selector('#v5tools');assert state()==saved;assert not errors,errors;print('PASS: actual Stellar Miracle catalogue + shipped CSV, 135/135 staged matches, no premature creation, saved links and reload');b.close()
