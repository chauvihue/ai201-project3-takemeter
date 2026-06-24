"""
Scraper for r/AIBubble and r/AIMain using old.reddit.com (no API key needed).

Collects text-based posts from both subreddits.
- Skips image/video posts (i.redd.it, i.imgur.com, etc.)
- Keeps link posts (article URLs) and embeds the URL in the text field
- No comments — posts only, to maximize unique examples

Usage:
    python scrape.py

Output:
    dataset_raw.csv  — columns: type, id, url, text, label, notes
    Fill in 'label' and 'notes' during annotation.

Requires:
    pip install requests beautifulsoup4
"""

import csv
import re
import time

import requests
from bs4 import BeautifulSoup

# ── Config ─────────────────────────────────────────────────────────────────────
SUBREDDITS  = ["AIBubble", "AIMain"]
OUTPUT_FILE = "dataset_raw.csv"
DELAY       = 2.5    # seconds between requests
TARGET      = 300    # stop collecting once we hit this many rows total

BASE    = "https://old.reddit.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Domains that are purely image/video — skip posts hosted here
IMAGE_DOMAINS = {
    "i.redd.it", "v.redd.it", "preview.redd.it",
    "external-preview.redd.it", "i.imgur.com",
    "gfycat.com", "redgifs.com", "streamable.com",
    "clips.twitch.tv",
}
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".gifv", ".mov")

REDDIT_POST_RE = re.compile(
    r"^(?:https?://(?:www\.|old\.)?reddit\.com)?/r/\w+/comments/(\w+)"
)

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# ── Session init ───────────────────────────────────────────────────────────────

def init_session():
    print("Initialising session...")
    SESSION.get("https://old.reddit.com/", timeout=20)
    SESSION.cookies.set("over18", "1", domain="old.reddit.com")
    time.sleep(DELAY)


# ── HTTP ───────────────────────────────────────────────────────────────────────

def get(url):
    for attempt in range(4):
        time.sleep(DELAY * (2 ** attempt))   # 2.5 → 5 → 10 → 20 s on retries
        try:
            r = SESSION.get(url, timeout=20)
            if r.status_code == 429:
                wait = 30 + 30 * attempt
                print(f"    Rate-limited — sleeping {wait}s…")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            if attempt == 3:
                raise
            print(f"    Retry {attempt+1}: {e}")
    raise RuntimeError(f"Failed to fetch {url}")


# ── Filters ────────────────────────────────────────────────────────────────────

def is_image_post(domain, url):
    if domain in IMAGE_DOMAINS:
        return True
    if url.lower().split("?")[0].endswith(IMAGE_EXTS):
        return True
    if domain == "imgur.com" and "/a/" not in url and "/gallery/" not in url:
        return True
    return False


# ── Parsers ────────────────────────────────────────────────────────────────────

def build_text(title, body="", article_url=""):
    """Build the text field: title + optional article URL + optional body."""
    parts = [title.strip()]
    if article_url:
        parts.append(article_url)
    body = (body or "").strip()
    if body and body not in ("[deleted]", "[removed]"):
        parts.append(body)
    return "\n\n".join(parts).strip()


def fetch_post_page(permalink):
    try:
        soup = get(BASE + permalink)
    except Exception as e:
        print(f"    Could not fetch {permalink}: {e}")
        return "", "", ""

    title_el = soup.select_one("a.title")
    title    = title_el.get_text().strip() if title_el else ""
    body_el  = soup.select_one("div.expando div.usertext-body div.md")
    body     = body_el.get_text(separator="\n").strip() if body_el else ""
    thing_el = soup.select_one("div.thing[data-url]")
    link_url = thing_el.get("data-url", "") if thing_el else ""
    return title, body, link_url


def fetch_linked_post_text(url_field):
    """If url_field is a Reddit post URL, return its full text (title + article URL + body)."""
    if not REDDIT_POST_RE.match(url_field or ""):
        return ""
    permalink = re.sub(r"^https?://[^/]+", "", url_field)
    title, body, link_url = fetch_post_page(permalink)
    is_self = link_url and (
        re.sub(r"^https?://[^/]+", "", link_url).rstrip("/") == permalink.rstrip("/")
    )
    article_url = ""
    if link_url and not is_self and not REDDIT_POST_RE.match(link_url):
        domain = link_url.split("/")[2] if link_url.startswith("http") else ""
        if not is_image_post(domain, link_url):
            article_url = link_url
    return build_text(title, body, article_url)


# ── Listing ────────────────────────────────────────────────────────────────────

def iter_listing(subreddit, feed):
    if feed == "top":
        url = f"{BASE}/r/{subreddit}/top/?t=all&limit=100"
    elif feed == "controversial":
        url = f"{BASE}/r/{subreddit}/controversial/?t=all&limit=100"
    else:
        url = f"{BASE}/r/{subreddit}/{feed}/?limit=100"

    while url:
        print(f"  Listing: {url.split('reddit.com')[-1][:80]}")
        try:
            soup = get(url)
        except Exception as e:
            print(f"  Error fetching listing: {e}")
            break

        things = soup.select("div.thing")
        if not things:
            break

        for thing in things:
            pid       = thing.get("data-fullname", "").replace("t3_", "")
            permalink = thing.get("data-permalink", "")
            link_url  = thing.get("data-url", "")
            domain    = thing.get("data-domain", "")
            if pid and permalink:
                yield {"id": pid, "permalink": permalink,
                       "link_url": link_url, "domain": domain}

        nxt = soup.select_one("span.next-button a")
        if nxt:
            href = nxt["href"]
            # href may be absolute (https://old.reddit.com/...) or relative (/r/...)
            url = href if href.startswith("http") else BASE + href
        else:
            url = None


# ── Main ───────────────────────────────────────────────────────────────────────

def scrape(subreddits):
    feeds = ("top", "hot", "controversial", "new", "rising")
    seen  = set()
    rows  = []

    for subreddit in subreddits:
        print(f"\n{'='*50}")
        print(f"  r/{subreddit}")
        print(f"{'='*50}")

        for feed in feeds:
            if len(rows) >= TARGET:
                print(f"\nReached {TARGET} rows -- done.")
                return rows

            print(f"\n-- {feed.upper()} --------------------------")

            for post in iter_listing(subreddit, feed):
                if len(rows) >= TARGET:
                    break

                pid = post["id"]
                if pid in seen:
                    continue
                seen.add(pid)

                if is_image_post(post["domain"], post["link_url"]):
                    print(f"  [skip image] {post['link_url'][:70]}")
                    continue

                title, body, _ = fetch_post_page(post["permalink"])
                if not title:
                    continue

                # Determine whether the link_url is an external article or another Reddit post
                linked = post["link_url"]
                is_reddit_link = bool(REDDIT_POST_RE.match(linked or ""))
                is_self_link   = linked and (
                    re.sub(r"^https?://[^/]+", "", linked).rstrip("/")
                    == post["permalink"].rstrip("/")
                )

                article_url  = ""
                linked_text  = ""

                if linked and not is_reddit_link and not is_self_link:
                    # External article/URL — embed it in the text
                    article_url = linked
                elif is_reddit_link and not is_self_link:
                    # Links to another Reddit post — fetch that post's full content
                    linked_text = fetch_linked_post_text(linked)
                    if linked_text:
                        print(f"    Embedded Reddit post fetched")

                orig_text = build_text(title, body, article_url)
                # Embedded post content goes first; original post content follows
                text = (linked_text + "\n\n---\n[Original Post]\n" + orig_text
                        if linked_text else orig_text)

                rows.append({
                    "type":  "post",
                    "id":    pid,
                    "url":   BASE + post["permalink"],
                    "text":  text,
                    "label": "",
                    "notes": "",
                })
                print(f"  [{len(rows):>3}/{TARGET}] {subreddit}: {title[:60]}")

    return rows


def save_csv(rows, path):
    fields = ["type", "id", "url", "text", "label", "notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved {len(rows)} rows -> {path}")


if __name__ == "__main__":
    init_session()
    rows = scrape(SUBREDDITS)
    save_csv(rows, OUTPUT_FILE)
