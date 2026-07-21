from pathlib import Path
import json
import re
import html
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

HOUSING_TERMS = [
    "woning", "woningen", "woningmarkt", "wooncrisis", "woonbeleid",
    "huisvesting", "volkshuisvesting", "woningbouw", "nieuwbouw",
    "huur", "huurwoning", "huurwoningen", "huurmarkt", "huurprijs",
    "huurprijzen", "huurder", "huurders", "middenhuur", "sociale huur",
    "vrije sector", "koopwoning", "koopwoningen", "hypotheek",
    "doorstroming", "woondeal", "woonwijk", "woonlasten"
]

HOMELESS_TERMS = [
    "dakloos", "dakloosheid", "thuisloos", "thuisloosheid",
    "maatschappelijke opvang", "nachtopvang", "crisisopvang"
]

REALESTATE_TERMS = [
    "vastgoed", "vastgoedmarkt", "woningbelegger", "woningbeleggers",
    "belegger", "beleggers", "portefeuille", "portefeuilles",
    "transactie", "transacties", "projectontwikkelaar",
    "projectontwikkelaars", "ontwikkelaar", "ontwikkelaars"
]

POLICY_TERMS = [
    "woonminister", "minister van volkshuisvesting", "volkshuisvesting",
    "regiewet", "huurbeleid", "woonbeleid", "woningwet",
    "betaalbaar wonen", "huisvestingswet", "huurtoeslag"
]

def clean_text(value):
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def contains_term(text, terms):
    text = f" {text.lower()} "
    for term in terms:
        if f" {term.lower()} " in text:
            return True
    return False

def matching_terms(text, terms):
    text = f" {text.lower()} "
    found = []
    for term in terms:
        if f" {term.lower()} " in text:
            found.append(term)
    return found

def make_tags(title, summary, source_category):
    text = f"{title} {summary}".lower()

    matched_profiles = []
    matched_angles = []
    labels = []

    housing_hits = matching_terms(text, HOUSING_TERMS)
    homeless_hits = matching_terms(text, HOMELESS_TERMS)
    realestate_hits = matching_terms(text, REALESTATE_TERMS)
    policy_hits = matching_terms(text, POLICY_TERMS)

    if housing_hits:
        matched_profiles.append("woningmarkt")

    if homeless_hits:
        matched_profiles.append("dakloosheid")

    if realestate_hits:
        matched_profiles.append("vastgoedmarkt_en_transacties")

    if source_category == "policy" and (housing_hits or homeless_hits or realestate_hits or policy_hits):
        matched_angles.append("beleid")

    if matched_profiles:
        labels.append("priority")

    return matched_profiles, matched_angles, labels

def is_relevant(title, summary, source_category):
    text = f"{title} {summary}".lower()

    has_housing = contains_term(text, HOUSING_TERMS)
    has_homeless = contains_term(text, HOMELESS_TERMS)
    has_realestate = contains_term(text, REALESTATE_TERMS)
    has_policy = contains_term(text, POLICY_TERMS)

    if source_category == "policy":
        return has_housing or has_homeless or has_realestate or has_policy

    return has_housing or has_homeless or has_realestate

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

        if not is_relevant(title, summary, feed_conf["source_category"]):
            continue

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
            "entity_type": None,
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

    print(f"{len(all_items)} relevante items geschreven naar data/latest.json")

if __name__ == "__main__":
    main()
