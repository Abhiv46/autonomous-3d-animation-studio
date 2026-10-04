from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Inspect all elements in upload dialog
    info = page.evaluate("""() => {
        function findFileInputs(node) {
            let inputs = [];
            if (node.tagName === 'INPUT' && node.type === 'file') {
                inputs.push({
                    id: node.id,
                    className: node.className,
                    name: node.name,
                    parent: node.parentElement ? node.parentElement.tagName : ''
                });
            }
            if (node.shadowRoot) {
                inputs = inputs.concat(findFileInputs(node.shadowRoot));
            }
            for (let child of node.children || []) {
                inputs = inputs.concat(findFileInputs(child));
            }
            return inputs;
        }
        return findFileInputs(document.body);
    }""")
    print("All file inputs in DOM and shadow roots:", info)
