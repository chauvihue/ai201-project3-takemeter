"""
Scraper for r/AIBubble using old.reddit.com (no API key needed).

Collects posts + top comments to reach 200-300 labeled examples.
- Skips image/video posts (i.redd.it, i.imgur.com, etc.)
- Keeps link posts (article URLs) — these become the `articles` label
- Pulls up to MAX_COMMENTS_PER_POST substantive comments per post
- Substantive = >= MIN_COMMENT_CHARS characters and not deleted/removed

Usage:
    python scrape.py

Output:
    dataset_raw.csv  — columns: type, id, url, text, label, notes
    type = 'post' or 'comment'
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
SUBREDDIT             = "AIBubble"
OUTPUT_FILE           = "dataset_raw.csv"
DELAY                 = 1.5    # seconds between requests
MAX_COMMENTS_PER_POST = 4      # max substantive comments to pull per post
MIN_COMMENT_CHARS     = 100    # minimum characters for a comment to be kept
TARGET                = 280    # stop collecting once we hit this many rows

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
    time.sleep(DELAY)
    r = SESSION.get(url, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


# ── Filters ────────────────────────────────────────────────────────────────────

def is_image_post(domain, url):
    """Return True for posts whose content is purely image/video."""
    if domain in IMAGE_DOMAINS:
        return True
    if url.lower().split("?")[0].endswith(IMAGE_EXTS):
        return True
    # imgur.com direct links without /a/ (albums) are usually single images
    if domain == "imgur.com" and "/a/" not in url and "/gallery/" not in url:
        return True
    return False


def is_substantive_comment(text):
    """Return True if a comment is worth keeping."""
    if not text or text in ("[deleted]", "[removed]"):
        return False
    # Strip whitespace and check length
    clean = " ".join(text.split())
    return len(clean) >= MIN_COMMENT_CHARS


# ── Parsers ────────────────────────────────────────────────────────────────────

def build_text(title, body=""):
    parts = [title.strip()]
    body = (body or "").strip()
    if body and body not in ("[deleted]", "[removed]"):
        parts.append(body)
    return "\n\n".join(parts).strip()


def parse_comments(soup):
    """Return a list of substantive top-level comment texts from a post page."""
    comments = []
    for div in soup.select("div.commentarea div.thing.comment"):
        body_el = div.select_one("div.usertext-body div.md")
        if not body_el:
            continue
        text = body_el.get_text(separator="\n").strip()
        if is_substantive_comment(text):
            comments.append(text)
        if len(comments) >= MAX_COMMENTS_PER_POST:
            break
    return comments


def fetch_post_page(permalink):
    """Fetch a post page and return (title, body, comments)."""
    try:
        soup = get(BASE + permalink)
    except Exception as e:
        print(f"    Could not fetch {permalink}: {e}")
        return "", "", []

    title_el = soup.select_one("a.title")
    title    = title_el.get_text().strip() if title_el else ""
    body_el  = soup.select_one("div.expando div.usertext-body div.md")
    body     = body_el.get_text(separator="\n").strip() if body_el else ""
    comments = parse_comments(soup)
    return title, body, comments


def fetch_linked_post_text(url_field):
    """If url_field is a Reddit post link, return its text. Otherwise ''."""
    if not REDDIT_POST_RE.match(url_field or ""):
        return ""
    permalink = re.sub(r"^https?://[^/]+", "", url_field)
    title, body, _ = fetch_post_page(permalink)   # don't pull comments from linked posts
    return build_text(title, body)


# ── Listing ────────────────────────────────────────────────────────────────────

def iter_listing(subreddit, feed):
    """Yield post metadata dicts from a feed listing page."""
    if feed == "top":
        url = f"{BASE}/r/{subreddit}/top/?t=all&limit=100"
    elif feed == "controversial":
        url = f"{BASE}/r/{subreddit}/controversial/?t=all&limit=100"
    else:
        url = f"{BASE}/r/{subreddit}/{feed}/?limit=100"

    while url:
        print(f"  Listing: {url.split('reddit.com')[-1]}")
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
        url = (BASE + nxt["href"]) if nxt else None


# ── Main ───────────────────────────────────────────────────────────────────────

def scrape(subreddit):
    feeds   = ("top", "hot", "controversial", "new", "rising")
    seen    = set()
    rows    = []

    for feed in feeds:
        if len(rows) >= TARGET:
            print(f"\nReached {TARGET} rows — done.")
            break

        print(f"\n-- {feed.upper()} --------------------------")

        for post in iter_listing(subreddit, feed):
            if len(rows) >= TARGET:
                break

            pid = post["id"]
            if pid in seen:
                continue
            seen.add(pid)

            # Skip image/video posts
            if is_image_post(post["domain"], post["link_url"]):
                print(f"  [skip image] {post['link_url'][:70]}")
                continue

            # Fetch page (post body + comments in one request)
            title, body, comments = fetch_post_page(post["permalink"])
            if not title:
                continue

            text = build_text(title, body)

            # Append linked Reddit post text if applicable
            linked = post["link_url"]
            if linked and REDDIT_POST_RE.match(linked):
                norm_linked = re.sub(r"^https?://[^/]+", "", linked).rstrip("/")
                if norm_linked.rstrip("/") != post["permalink"].rstrip("/"):
                    linked_text = fetch_linked_post_text(linked)
                    if linked_text:
                        text += "\n\n---\n[Linked Post]\n" + linked_text
                        print(f"    Linked post appended")

            # Add post row
            rows.append({
                "type":  "post",
                "id":    pid,
                "url":   BASE + post["permalink"],
                "text":  text,
                "label": "",
                "notes": "",
            })
            print(f"  [{len(rows):>3}/{TARGET}] POST: {title[:60]}")

            # Add comment rows
            for i, comment_text in enumerate(comments):
                if len(rows) >= TARGET:
                    break
                rows.append({
                    "type":  "comment",
                    "id":    f"{pid}_c{i}",
                    "url":   BASE + post["permalink"],
                    "text":  comment_text,
                    "label": "",
                    "notes": "",
                })
                print(f"  [{len(rows):>3}/{TARGET}]   comment ({len(comment_text)} chars)")

    return rows


def save_csv(rows, path):
    fields = ["type", "id", "url", "text", "label", "notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    posts    = sum(1 for r in rows if r["type"] == "post")
    comments = sum(1 for r in rows if r["type"] == "comment")
    print(f"\nSaved {len(rows)} rows ({posts} posts + {comments} comments) -> {path}")


if __name__ == "__main__":
    init_session()
    rows = scrape(SUBREDDIT)
    save_csv(rows, OUTPUT_FILE)
