"""Quick probe: count unique text-based posts in r/AIMain across all feeds."""
import re, time
import requests
from bs4 import BeautifulSoup

BASE    = "https://old.reddit.com"
DELAY   = 1.5
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
IMAGE_DOMAINS = {
    "i.redd.it","v.redd.it","preview.redd.it","external-preview.redd.it",
    "i.imgur.com","gfycat.com","redgifs.com","streamable.com","clips.twitch.tv",
}
IMAGE_EXTS = (".jpg",".jpeg",".png",".gif",".webp",".mp4",".gifv",".mov")

sess = requests.Session()
sess.headers.update(HEADERS)

def init():
    sess.get(f"{BASE}/", timeout=20)
    sess.cookies.set("over18","1",domain="old.reddit.com")
    time.sleep(DELAY)

def get(url):
    time.sleep(DELAY)
    r = sess.get(url, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def is_image(domain, url):
    if domain in IMAGE_DOMAINS: return True
    if url.lower().split("?")[0].endswith(IMAGE_EXTS): return True
    if domain == "imgur.com" and "/a/" not in url and "/gallery/" not in url: return True
    return False

def iter_listing(sub, feed):
    url = f"{BASE}/r/{sub}/{feed}/?limit=100" if feed not in ("top","controversial") \
          else f"{BASE}/r/{sub}/{feed}/?t=all&limit=100"
    while url:
        try: soup = get(url)
        except Exception as e:
            print(f"  Error: {e}"); break
        things = soup.select("div.thing")
        if not things: break
        for t in things:
            pid      = t.get("data-fullname","").replace("t3_","")
            link_url = t.get("data-url","")
            domain   = t.get("data-domain","")
            permalink= t.get("data-permalink","")
            if pid:
                yield pid, domain, link_url, permalink
        nxt = soup.select_one("span.next-button a")
        url = (BASE + nxt["href"]) if nxt else None

init()
feeds = ("top","hot","controversial","new","rising")
seen = set()
text_posts = 0
image_skipped = 0

for feed in feeds:
    print(f"\n-- {feed.upper()} --")
    for pid, domain, link_url, permalink in iter_listing("AIMain", feed):
        if pid in seen: continue
        seen.add(pid)
        if is_image(domain, link_url):
            image_skipped += 1
        else:
            text_posts += 1

print(f"\n{'='*40}")
print(f"Total unique posts seen : {len(seen)}")
print(f"Text-based (kept)       : {text_posts}")
print(f"Image/video (skipped)   : {image_skipped}")
