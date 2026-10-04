import urllib.request
import re

url = "https://www.youtube.com/shorts/k2JBp96Iqa4"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode("utf-8", errors="ignore")
    m_title = re.search(r"<title>(.*?)</title>", html)
    title = m_title.group(1) if m_title else "None"
    print("Page Title:", title.encode("ascii", "replace").decode("ascii"))
    m_og_title = re.search(r'<meta property="og:title" content="(.*?)"', html)
    og_title = m_og_title.group(1) if m_og_title else "None"
    print("OG Title:", og_title.encode("ascii", "replace").decode("ascii"))
    m_desc = re.search(r'<meta property="og:description" content="(.*?)"', html)
    desc = m_desc.group(1) if m_desc else "None"
    print("OG Description:", desc[:100].encode("ascii", "replace").decode("ascii"))
except Exception as e:
    print("Error:", e)
