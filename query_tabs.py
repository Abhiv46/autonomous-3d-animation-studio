import urllib.request
import json

data = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
for item in data:
    t = item.get("type")
    title = item.get("title", "")
    url = item.get("url", "")
    print(f"[{t}] {title} -> {url}")
