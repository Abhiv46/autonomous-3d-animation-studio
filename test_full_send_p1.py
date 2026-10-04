import asyncio
from playwright.async_api import async_playwright

prompt_to_send = (
    "Use Veo 3.1 - Lite (8 seconds is fine). Please generate this exact scene now for Part 1:\n"
    "REFERENCE CHARACTERS: Use the attached existing Kaartik and Kaavya reference images. STRICT CHARACTER IDENTITY LOCK: preserve their exact faces, hairstyles, ages, body proportions, facial features and recognizable identity. Never redesign, morph, clone, duplicate or replace either child.\n"
    "Kaartik and Kaavya stand together in a breathtaking magical children's adventure-game world filled with giant colorful flowers, floating islands, glowing paths, rainbow clouds, sparkling particles and cute oversized objects. Suddenly the world loses almost all its colors and becomes soft pale pastel. A huge magical rainbow portal opens in front of them.\n"
    "Kaartik looks amazed and points toward the portal. Kaavya excitedly jumps once and reaches toward the glowing colors.\n"
    "CAMERA: cinematic push-in toward the children, then reveal the giant rainbow portal.\n"
    "MUSIC: one continuous original catchy nursery-adventure melody, bouncy xylophone, marimba, ukulele, soft drums, hand claps, playful bells, magical sparkles, approximately 125 BPM.\n"
    "SPEAKER LOCK — CRITICAL: KAARTIK is the ONLY speaking character in this shot. Kaartik clearly faces camera while pointing toward the rainbow portal and says/sings: 'Kaavya! Rang gayab ho gaye!' Kaavya remains completely silent, smiling with her mouth closed. NEVER give Kaartik's voice or dialogue to Kaavya.\n"
    "End with the rainbow portal glowing brighter, creating a strong visual transition into Part 2.\n"
    "NO dark atmosphere, no scary elements, no flat 2D animation, no dull colors, no extra children, no duplicate characters, no identity changes, no dialogue swapping."
)

async def test_full_send():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        flow_page = [pg for pg in b.contexts[0].pages if "flow.google.com/u/2" in pg.url][0]
        
        # Insert text cleanly into ProseMirror without triggering Enter
        await flow_page.evaluate("""(text) => {
            const pm = document.querySelector('div.ProseMirror');
            if (pm) {
                pm.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('delete', false, null);
                document.execCommand('insertText', false, text);
                pm.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", prompt_to_send)
        await flow_page.wait_for_timeout(1500)
        
        # Click the send button
        send_btn = flow_page.locator("button[aria-label*='Start generation' i], button:has-text('arrow_forward')").last
        print("Clicking Start Generation button...", flush=True)
        await send_btn.click(force=True)
        await flow_page.wait_for_timeout(4000)
        
        # Auto-approve if any popup
        for _ in range(5):
            app = flow_page.locator("button:has-text('Always approve'), button:has-text('Approve')").last
            if await app.count() > 0 and await app.is_visible():
                print("Clicked approval button:", await app.inner_text(), flush=True)
                await app.click(force=True)
                await flow_page.wait_for_timeout(1500)
                break
            await asyncio.sleep(1)

        await flow_page.screenshot(path=r"C:\Users\user\.gemini\antigravity\brain\2ebe07f2-7a70-428f-ab41-dc22d7b904d2\flow_p1_generation_triggered.png")
        print("Saved generation triggered screenshot!")

if __name__ == "__main__":
    asyncio.run(test_full_send())
