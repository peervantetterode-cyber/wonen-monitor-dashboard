from pathlib import Path
import json
import feedparser

RSS_FEEDS = [
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
    }
]

def clean_text(value):
    return (value or "").strip()

def make_tags(title, summary, source_category):
    text = f"{title} {summary}".lower()

    matched_profiles = []
    matched_angles = []
    labels = []

    if any(w in text for w in ["woning", "woningen", "huur", "huren", "huurder", "huurders", "koopwoning", "koopwoningen", "hypotheek"]):
        matched_profiles.append("woningmarkt")

    if any(w in text for w in ["dakloos", "dakloosheid", "opvang", "maatschappelijke opvang", "thuisloos"]):
        matched_profiles.append("dakloosheid")

    if any(w in text for w in ["vastgoed", "belegger", "beleggers", "portefeuille", "transactie", "transacties"]):
        matched_profiles.append("vastgoedmarkt_en_transacties")

    if source_category == "policy" or any(w in text for w in ["minister", "kamer", "beleid", "wet", "wetsvoorstel", "volkshuisvesting"]):
        matched_angles.append("beleid")

    if matched_profiles:
        labels.append("priority")

    return matched_profiles, matched_angles, labels

def parse_feed(feed_conf):
    parsed = feedparser.parse(feed_conf["url"])
    items = []

    for entry in parsed.entries[:30]:
        title = clean_text(getattr(entry, "title", ""))
        link = clean_text(getattr(entry, "link", ""))
        summary = clean_text(
            getattr(entry, "summary", "") or getattr(entry, "description", "")
        )
        published = clean_text(
            getattr(entry, "published", "") or getattr(entry, "updated", "")
        )

        matched_profiles, matched_angles, labels = make_tags(
            title, summary, feed_conf["source_category"]
        )

        item = {
            "source_id": feed_conf["source_id"],
            "source_name": feed_conf["source_name"],
            "source_category": feed_conf["source_category"],
            "source_priority": "high" if labels else "medium",
            "title": title,
            "url": link,
            "summary": summary,
            "published_at": published,
            "raw_text": f"{title} {summary}",
            "matched_profiles": matched_profiles,
            "matched_angles": matched_angles,
            "score": 10 + len(matched_profiles) * 3 + len(matched_angles) * 2,
            "labels": labels,
            "entity_type": "Activiteit" if feed_conf["source_id"] == "tweede_kamer" else None,
            "political_context": "Rijksbeleid" if feed_conf["source_category"] == "policy" else None
        }
        items.append(item)

    return items

def main():
    all_items = []

    for feed_conf in RSS_FEEDS:
        try:
            all_items.extend(parse_feed(feed_conf))
        except Exception as e:
            print(f"Fout bij {feed_conf['source_name']}: {e}")

    all_items.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    Path("data").mkdir(exist_ok=True)
    Path("data/latest.json").write_text(
        json.dumps(all_items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"{len(all_items)} items geschreven naar data/latest.json")

if __name__ == "__main__":
    main()
