from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        flow_page.keyboard.press('Escape')
        # Let's inspect all video cards or recent cards
        info = flow_page.evaluate("""() => {
            // Find all elements that look like cards or items in the grid
            const elements = Array.from(document.querySelectorAll('button, div[tabindex="0"], mat-card, [role="gridcell"]'));
            // Filter to those with images or videos
            const mediaCards = elements.filter(el => {
                return el.querySelector('img') || el.querySelector('video') || el.innerText.includes('Untitled');
            });
            return mediaCards.slice(0, 20).map(el => ({
                text: el.innerText.replace(/\\s+/g, ' ').trim(),
                hasVideo: !!el.querySelector('video'),
                hasImg: !!el.querySelector('img'),
                imgSrc: el.querySelector('img') ? el.querySelector('img').src.slice(0, 100) : ''
            }));
        }""")
        print(f"Found {len(info)} cards:")
        for idx, item in enumerate(info):
            print(f"[{idx}]: {item}")
