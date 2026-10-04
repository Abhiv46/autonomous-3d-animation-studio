from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    flow_page = next((p for p in browser.contexts[0].pages if 'flow.google.com' in p.url), None)
    if flow_page:
        flow_page.keyboard.press('Escape')
        tiles = flow_page.evaluate("""() => {
            const videoTiles = Array.from(document.querySelectorAll('flow-video-tile, flow-scene-tile, flow-image-tile'));
            return videoTiles.map(t => {
                const img = t.querySelector('img');
                const video = t.querySelector('video');
                return {
                    tag: t.tagName.toLowerCase(),
                    text: t.innerText.replace(/\\s+/g, ' ').trim(),
                    src: (img ? img.src : (video ? video.src : '')).slice(0, 100),
                    box: t.getBoundingClientRect()
                };
            });
        }""")
        print(f"Found {len(tiles)} tiles:")
        for i, t in enumerate(tiles):
            print(f"[{i}] {t['tag']} - text: {t['text'][:60]} - box: ({t['box']['x']:.0f}, {t['box']['y']:.0f})")
