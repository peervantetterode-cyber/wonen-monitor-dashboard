from pathlib import Path
import json
import datetime as dt

import feedparser  # moet in requirements.txt staan
import requests


FEEDS = [
    {
        "source_id": "nos",
        "source_name": "NOS",
        "source_category": "media",
        "url": "https://feeds.nos.nl/nosnieuwsbinnenland"
    },
    {
        "source_id": "rijksoverheid",
        "source_name": "Rijksoverheid",
        "source_category": "policy",
        "url": "https://feeds.rijksoverheid.nl/nieuws.rss"
    },
]

def fetch_feed(feed_conf):
    d = feedparser.parse(feed_conf["url"])
    items = []
    for entry in d.entries[:20]:  # max 20 per bron om het klein te houden
        title = getattr(entry, "title", "")
        link = getattr(entry, "link", "")
        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        published = getattr(entry, "published", "") or getattr(entry, "updated", "")

        item = {
            "source_id": feed_conf["source_id"],
            "source_name": feed_conf["source_name"],
            "source_category": feed_conf["source_category"],
            "source_priority": "medium",
            "title": title,
            "url": link,
            "summary": summary,
            "published_at": published,
            "raw_text": summary,
            # heel simpele tagging – dit kun je later slimmer maken
            "matched_profiles": ["woningmarkt"] if "woning" in title.lower() or "huur" in title.lower() else [],
            "matched_angles": [],
            "score": 10,
            "labels": [],
            "entity_type": None,
            "political_context": None,
        }
        items.append(item)
    return items


def main():
    all_items = []
    for f in FEEDS:
        try:
            all_items.extend(fetch_feed(f))
        except Exception as e:
            print("Fout bij feed", f["source_id"], e)

    # heel simpele sortering: nieuwste eerst op published_at als string
    all_items.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    Path("data").mkdir(exist_ok=True)
    out_path = Path("data/latest.json")
    out_path.write_text(
        json.dumps(all_items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"{len(all_items)} items naar {out_path} geschreven")


if __name__ == "__main__":
    main()
