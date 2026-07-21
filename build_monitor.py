import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from sources import SITE_FEEDS, SCRAPE_SITES, SEARCH_TERMS, google_news_rss_url, RECHTSPRAAK_TERMS, rechtspraak_rss_url

WOON_KEYWORDS = [
    "woning", "woningen", "woningmarkt", "huizenmarkt",
    "huur", "huurt", "huurprijs", "huurprijzen", "huurmarkt",
    "hypotheek", "hypotheken",
    "vastgoed", "vastgoedmarkt",
    "huurwoning", "koopwoning", "huurwoningen", "koopwoningen",
    "corporatie", "woningcorporatie", "woningcorporaties"
]

SPORT_BLACKLIST = [
    "voetbal", "ajax", "feyenoord", "psv", "eredivisie",
    "champions league", "europa league", "oranje", "wk", "ek"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WoonMonitorBot/1.0)"}
TIMEOUT = 15

def fetch_rss(name, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:15]:
            items.append({
                "source": name,
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "published": entry.get("published", entry.get("updated", "")),
                "type": "rss",
            })
    except Exception as e:
        print(f"[WARN] RSS failed for {name}: {e}")
    return items

def try_discover_rss(base_url):
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")
        link = soup.find("link", {"type": "application/rss+xml"})
        if link and link.get("href"):
            href = link["href"]
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            return href
    except Exception as e:
        print(f"[WARN] discovery failed for {base_url}: {e}")
    return None

def fetch_scrape_fallback(name, base_url):
    discovered = try_discover_rss(base_url)
    if discovered:
        print(f"[INFO] Discovered RSS for {name}: {discovered}")
        return fetch_rss(name, discovered)

    items = []
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=True)
        seen = set()
        count = 0
        for a in links:
            title = a.get_text(strip=True)
            href = a["href"]
            if not title or len(title) < 25:
                continue
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            if href in seen or not href.startswith("http"):
                continue
            seen.add(href)
            items.append({
                "source": name,
                "title": title,
                "link": href,
                "published": "",
                "type": "scrape",
            })
            count += 1
            if count >= 15:
                break
    except Exception as e:
        print(f"[WARN] scrape failed for {name}: {e}")
    return items

def fetch_search_term(term):
    url = google_news_rss_url(term)
    label = f"Zoekterm: {term}"
    items = fetch_rss(label, url)
    for it in items:
        it["search_term"] = term
    return items

def fetch_rechtspraak_term(term):
    url = rechtspraak_rss_url(term)
    label = f"Rechtspraak.nl: {term}"
    items = fetch_rss(label, url)
    for it in items:
        it["search_term"] = term
    return items

def dedupe(items):
    seen = set()
    result = []
    for it in items:
        key = hashlib.sha1(it["title"].strip().lower().encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        result.append(it)
    return result

def is_relevant(item):
    text = f"{item.get('title','')} {item.get('source','')}".lower()

    # sport wegfilteren
    for bad in SPORT_BLACKLIST:
        if bad in text:
            return False

    # alleen houden als er een woon/vastgoed trefwoord in zit
    for kw in WOON_KEYWORDS:
        if kw in text:
            return True

    # alles zonder trefwoord weggooien
    return False

def main():
    all_items = []

    # vaste RSS-bronnen
    for name, url in SITE_FEEDS.items():
        print(f"Fetching site feed: {name}")
        all_items.extend(fetch_rss(name, url))
        time.sleep(0.3)

    # sites zonder bekende RSS (fallback: auto-detect + scrape)
    for name, url in SCRAPE_SITES.items():
        print(f"Fetching scrape/fallback: {name}")
        all_items.extend(fetch_scrape_fallback(name, url))
        time.sleep(0.3)

    # Google News zoektermen
    for term in SEARCH_TERMS:
        print(f"Fetching search term: {term}")
        all_items.extend(fetch_search_term(term))
        time.sleep(0.3)

    # Rechtspraak.nl (vastgoed / huur / corporaties / sociale huur)
    for term in RECHTSPRAAK_TERMS:
        print(f"Fetching rechtspraak.nl term: {term}")
        all_items.extend(fetch_rechtspraak_term(term))
        time.sleep(0.3)

      # dedupliceren op titel
    all_items = dedupe(all_items)

    # alleen relevante woon/vastgoed-items overhouden
    filtered = [it for it in all_items if is_relevant(it)]
    print(f"Filtered down from {len(all_items)} to {len(filtered)} relevant items.")
    all_items = filtered

    os.makedirs("output", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    with open("output/monitor_data.json", "w", encoding="utf-8") as f:
        json.dump({"generated_at": now, "items": all_items}, f, ensure_ascii=False, indent=2)

    generate_html(all_items, now)
    print(f"Done. {len(all_items)} unique items collected.")

def generate_html(items, generated_at):
    by_source = {}
    for it in items:
        by_source.setdefault(it["source"], []).append(it)

    html = [
        "<!DOCTYPE html><html lang='nl'><head><meta charset='UTF-8'>",
        "<title>Woonmonitor Dashboard</title>",
        "<style>",
        "body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:0 auto;padding:24px;background:#fafafa;color:#1a1a1a;}",
        "h1{font-size:1.6rem;} h2{font-size:1.1rem;border-bottom:2px solid #ddd;padding-bottom:6px;margin-top:32px;}",
        "ul{list-style:none;padding:0;} li{padding:8px 0;border-bottom:1px solid #eee;}",
        "a{color:#0645ad;text-decoration:none;} a:hover{text-decoration:underline;}",
        ".meta{color:#777;font-size:0.85rem;} .ts{color:#999;font-size:0.8rem;}",
        "</style></head><body>",
        f"<h1>Woonmonitor Dashboard</h1><p class='meta'>Laatst bijgewerkt: {generated_at}</p>",
    ]

    for source, entries in by_source.items():
        html.append(f"<h2>{source}</h2><ul>")
        for e in entries:
            pub = f"<span class='ts'>{e['published']}</span>" if e["published"] else ""
            html.append(f"<li><a href='{e['link']}' target='_blank'>{e['title']}</a> {pub}</li>")
        html.append("</ul>")

    html.append("</body></html>")

    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html))

if __name__ == "__main__":
    main()
