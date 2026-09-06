from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
root=Path(__file__).resolve().parent
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
    page.goto((root/'index.html').as_uri())
    page.screenshot(path=str(root/'qa-mobile.png'),full_page=True)
    overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
    assert not overflow, 'Mobile horizontal overflow'
    page.emulate_media(media='print')
    page.set_viewport_size({'width':794,'height':1123})
    page.pdf(path=str(root/'handout.pdf'),format='A4',print_background=True,prefer_css_page_size=True)
    for i, sheet in enumerate(page.locator('.sheet').all(),1):
        sheet.screenshot(path=str(root/f'qa-print-{i}.png'))
    browser.close()
reader=PdfReader(root/'handout.pdf')
assert len(reader.pages)==2, f'PDF has {len(reader.pages)} pages'
assert '119' in reader.pages[0].extract_text()
assert '出典' in reader.pages[1].extract_text()
print(json.dumps({'pdf_pages':len(reader.pages),'mobile_overflow':overflow,'pdf_bytes':(root/'handout.pdf').stat().st_size},ensure_ascii=False))
