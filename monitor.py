from pathlib import Path
import json
import re
import html
import feedparser

RSS_FEEDS = [
    # Kranten en algemene media
    {
        "source_id": "fd",
        "source_name": "FD",
        "source_category": "media",
        "url": "https://fd.nl/?rss"
    },
    {
        "source_id": "volkskrant",
        "source_name": "de Volkskrant",
        "source_category": "media",
        "url": "https://www.volkskrant.nl/rss/feeds"  # kies hier later een specifieke feed-URL uit
    },
    {
        "source_id": "nrc",
        "source_name": "NRC",
        "source_category": "media",
        "url": ">>> vul hier de NRC-rss-url in die je kiest <<<"
    },
    {
        "source_id": "telegraaf",
        "source_name": "De Telegraaf",
        "source_category": "media",
        "url": ">>> vul hier de Telegraaf-rss-url in <<<"
    },
    {
        "source_id": "nos",
        "source_name": "NOS",
        "source_category": "media",
        "url": "https://feeds.nos.nl/nosnieuwsbinnenland"
    },
    {
        "source_id": "rtl",
        "source_name": "RTL Nieuws",
        "source_category": "media",
        "url": ">>> concrete RTL-nieuws-rss-url, bijv. via rtlnieuws.nl/rss <<<"
    },

    # Onderzoeksjournalistiek
    {
        "source_id": "ftm",
        "source_name": "Follow the Money",
        "source_category": "media",
        "url": ">>> evt. FTM-rss of notificatie-feed, alleen titel+link gebruiken <<<"
    },

    # Beleid, overheid, parlement
    {
        "source_id": "rijksoverheid_algemeen",
        "source_name": "Rijksoverheid",
        "source_category": "policy",
        "url": "https://feeds.rijksoverheid.nl/nieuws.rss"
    },
    {
        "source_id": "rijksoverheid_volkshuisvesting",
        "source_name": "Rijksoverheid Volkshuisvesting",
        "source_category": "policy",
        "url": "https://feeds.rijksoverheid.nl/onderwerpen/volkshuisvesting/nieuws.rss"
    },
    {
        "source_id": "min_vro",
        "source_name": "Ministerie VRO",
        "source_category": "policy",
        "url": "https://feeds.rijksoverheid.nl/ministeries/ministerie-van-volkshuisvesting-en-ruimtelijke-ordening/nieuws.rss"
    },
    {
        "source_id": "tweedekamer",
        "source_name": "Tweede Kamer",
        "source_category": "politics",
        "url": ">>> specifieke RSS voor activiteiten/kamerstukken over wonen <<<"
    },
    {
        "source_id": "cbs",
        "source_name": "CBS",
        "source_category": "data",
        "url": ">>> CBS-nieuws- of publicatie-rss over woningmarkt <<<"
    },

    # Sector: corporaties, huurders
    {
        "source_id": "aedes",
        "source_name": "Aedes",
        "source_category": "sector",
        "url": ">>> Aedes-rss-url <<<"
    },
    {
        "source_id": "woonbond",
        "source_name": "Woonbond",
        "source_category": "sector",
        "url": "https://www.woonbond.nl/rss.xml"
    },

    # Vastgoedmedia
    {
        "source_id": "vastgoednieuws",
        "source_name": "Vastgoednieuws",
        "source_category": "vastgoed",
        "url": ">>> rss-url Vastgoednieuws <<<"
    },
    {
        "source_id": "propertynl",
        "source_name": "PropertyNL",
        "source_category": "vastgoed",
        "url": ">>> rss-url PropertyNL <<<"
    },

    # Meta-bronnen
    {
        "source_id": "google_alerts",
        "source_name": "Google Alerts",
        "source_category": "meta",
        "url": ">>> 1 of meer persoonlijke Google-Alerts-rss-links <<<"
    },
    {
        "source_id": "linkedin",
        "source_name": "LinkedIn",
        "source_category": "meta",
        "url": ">>> evt. via externe dienst om LinkedIn-updates naar rss te brengen <<<"
    }
]
HOUSING_TERMS = [
    "woning", "woningen", "woningmarkt", "wooncrisis", "huisvesting",
    "volkshuisvesting", "woningbouw", "nieuwbouw", "huur", "huurprijs",
    "huurprijzen", "huurder", "huurders", "huurwoning", "huurwoningen",
    "middenhuur", "sociale huur", "vrije sector", "koopwoning",
    "koopwoningen", "hypotheek", "woonlasten", "woondeal"
]

HOMELESS_TERMS = [
    "dakloos", "dakloosheid", "thuisloos", "thuisloosheid",
    "maatschappelijke opvang", "nachtopvang", "crisisopvang"
]

REALESTATE_TERMS = [
    "vastgoed", "vastgoedmarkt", "belegger", "beleggers",
    "woningbelegger", "woningbeleggers", "portefeuille",
    "transactie", "transacties", "projectontwikkelaar",
    "projectontwikkelaars", "ontwikkelaar", "ontwikkelaars"
]

POLICY_TERMS = [
    "woonbeleid", "huurbeleid", "regiewet", "woningwet",
    "huisvestingswet", "huurtoeslag", "betaalbaar wonen",
    "woonminister", "volkshuisvesting"
]

def clean_text(value):
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def has_term(text, terms):
    text = text.lower()
    for term in terms:
        pattern = r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, text):
            return True
    return False

def get_matches(text, terms):
    text = text.lower()
    matches = []
    for term in terms:
        pattern = r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, text):
            matches.append(term)
    return matches

def make_tags(title, summary, source_category):
    text = f"{title} {summary}"

    matched_profiles = []
    matched_angles = []
    labels = []

    housing_hits = get_matches(text, HOUSING_TERMS)
    homeless_hits = get_matches(text, HOMELESS_TERMS)
    realestate_hits = get_matches(text, REALESTATE_TERMS)
    policy_hits = get_matches(text, POLICY_TERMS)

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
    title_l = title.lower()
    summary_l = summary.lower()

    title_hits = (
        has_term(title_l, HOUSING_TERMS)
        or has_term(title_l, HOMELESS_TERMS)
        or has_term(title_l, REALESTATE_TERMS)
        or has_term(title_l, POLICY_TERMS)
        or "woon" in title_l
        or "woning" in title_l
        or "huur" in title_l
        or "dakloos" in title_l
        or "vastgoed" in title_l
        or "bouw" in title_l
        or "huisvesting" in title_l
    )

    summary_hits = (
        has_term(summary_l, HOUSING_TERMS)
        or has_term(summary_l, HOMELESS_TERMS)
        or has_term(summary_l, REALESTATE_TERMS)
        or has_term(summary_l, POLICY_TERMS)
    )

    if source_category == "policy":
        return title_hits or summary_hits

    return title_hits
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

    print(f"{len(all_items)} items geschreven naar data/latest.json")

if __name__ == "__main__":
    main()
