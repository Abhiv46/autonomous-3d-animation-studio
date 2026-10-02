import asyncio
import json
import os
import urllib.request
import websockets
from pathlib import Path

VIDEO_PATH = r"C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\data\processed_episodes\TheNaughtyDuo_EP22_ChocolateFaceMask_OriginalAudio_Master.mp4"
TITLE = "Mummy Ka Chocolate Face Mask! 🍫😱 Kaavya Ne Chaat Liya! #TheNaughtyDuo #shorts"

async def check():
    print(f"Master Video ready for publishing: {os.path.exists(VIDEO_PATH)}")

if __name__ == "__main__":
    asyncio.run(check())
