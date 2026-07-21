from pathlib import Path
import json
import datetime as dt

import feedparser  # zorg dat dit in requirements.txt staat
import requests    # ook in requirements.txt


# === 1. MEDIA- EN NIEUWSFEEDS VIA RSS =======================================

RSS_FEEDS = [
    # NOS
    {
        "source_id": "nos_binnenland",
        "source_name": "NOS",
        "source_category": "media",
        "url": "https://feeds.nos.nl/nosnieuwsbinnenland"
    },
    # Rijksoverheid algemeen nieuws
    {
        "source_id": "rijksoverheid_nieuws",
        "source_name": "Rijksoverheid",
        "source_category": "policy",
        "url": "https://feeds.rijksoverheid.nl/nieuws.rss"
    },
    # RTL Nieuws – voorbeeld, controleer of deze feed werkt en pas zonodig aan
    {
        "source_id": "rtl_nieuws",
        "source_name": "RTL Nieuws",
        "source_category": "media",
        "url": "https://www.rtlnieuws.nl/service/rss/nieuws/index.xml"
    },

    # === HIER KOMEN JOUW OVERIGE RSS-BRONNEN ================================
    # Vul deze URLs later in zodra je de echte RSS-links hebt of Google Alerts maakt.

    # Google Alerts (door jou in te vullen)
    # {"source_id": "google_alerts_wonen", "source_name": "Google Alerts", "source_category": "alerts", "url": "HIER_JOUW_ALERT_RSS_URL"},

    # FD, NRC, Volkskrant, Telegraaf, Cobouw, Vastgoednieuws, PropertyNL
    # {"source_id": "fd", "source_name": "FD", "source_category": "media", "url": "HIER_RSS_URL"},
    # {"source_id": "nrc", "source_name": "NRC", "source_category": "media", "url": "HIER_RSS_URL"},
    # {"source_id": "vk", "source_name": "Volkskrant", "source_category": "media", "url": "HIER_RSS_URL"},
    # {"source_id": "telegraaf", "source_name": "Telegraaf", "source_category": "media", "url": "HIER_RSS_URL"},
    # {"source_id": "cobouw", "source_name": "Cobouw", "source_category": "media", "url": "HIER_RSS_URL"},
    # {"source_id": "vastgoednieuws", "source_name": "Vastgoednieuws", "source_category": "media", "url": "HIER_RSS_URL"},
    # {"source_id": "propertynl", "source_name": "PropertyNL", "source_category": "media", "url": "HIER_RSS_URL"},

    # Aedes, Woonbond – vaak nieuwssectie, soms RSS
    # {"source_id": "aedes", "source_name": "Aedes", "source_category": "stakeholder", "url": "HIER_RSS_URL"},
    # {"source_id": "woonbond", "source_name": "Woonbond", "source_category": "stakeholder", "url": "HIER_RSS_URL"},
]


def normalize_rss_entry(feed_conf, entry):
    """Vertaal een RSS-entry naar jouw JSON-structuur."""
    title = getattr(entry, "title", "")
    link = getattr(entry, "link", "")
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
    published = getattr(entry, "published", "") or getattr(entry, "updated", "")

    text_lower = f"{title} {summary}".lower()

    matched_profiles = []
    matched_angles = []

    # simpele keywords – later kun je dit vervangen door jouw scoringslogica
    if any(w in text_lower for w in ["woning", "huur", "hypotheek", "koopwoning"]):
        matched_profiles.append("woningmarkt")
    if any(w in text_lower for w in ["dakloos", "opvang", "maatschappelijke opvang"]):
        matched_profiles.append("dakloosheid")
    if any(w in text_lower for w in ["belegger", "vastgoed", "portefeuille", "portefeuille"]):
        matched_profiles.append("vastgoedmarkt_en_transacties")
    if any(w in text_lower for w in ["minister", "kamer", "wet", "wetsvoorstel", "beleid"]):
        matched_angles.append("beleid")

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
        "matched_profiles": matched_profiles,
        "matched_angles": matched_angles,
        "score": 10 + len(matched_profiles) * 2 + len(matched_angles) * 2,
        "labels": ["priority"] if "woningmarkt" in matched_profiles or "dakloosheid" in matched_profiles else [],
        "entity_type": None,
        "political_context": None,
    }
    return item


def fetch_rss_feeds():
    items = []
    for feed_conf in RSS_FEEDS:
        url = feed_conf["url"]
        if "HIER_RSS_URL" in url:
            # placeholder, sla deze feed over tot je de echte URL invult
            continue
        print(f"RSS ophalen: {feed_conf['source_id']} ({url})")
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:30]:
            try:
                items.append(normalize_rss_entry(feed_conf, entry))
            except Exception as e:
                print("Fout bij entry in", feed_conf["source_id"], e)
    return items


# === 2. TWEEDE KAMER – OPEN DATA (PLACEHOLDER VOOR LATER UITBREIDEN) ========

def fetch_tweede_kamer():
    """
    Placeholder: haal later via OData/SyncFeed activiteiten & stukken op.
    Voor nu geven we een leeg lijstje terug zodat de code niet breekt.
    """
    # TODO: gebruik bv. https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Activiteit
    # met filters op onderwerp wonen/volkshuisvesting.
    return []


# === 3. CBS – OPEN DATA (Cijfers, geen nieuws) ==============================

def fetch_cbs():
    """
    Placeholder voor CBS-open data (cijfers over woningmarkt/dakloosheid).
    Deze zou je later kunnen gebruiken om bijvoorbeeld KPI-tiles te vullen.
    """
    return []


# === 4. GOOGLE ALERTS / LINKEDIN / OVERIGE ================================

def fetch_google_alerts():
    """
    Als jij Google Alerts als RSS maakt, kun je die hier ook via feedparser lezen.
    Voeg de RSS-URLs dan gewoon toe aan RSS_FEEDS of maak hier aparte logica.
    """
    return []


def main():
    all_items = []

    # 1) Media + RSS
    all_items.extend(fetch_rss_feeds())

    # 2) Tweede Kamer
    all_items.extend(fetch_tweede_kamer())

    # 3) CBS (cijfers -> eventueel later omzetten naar 'items')
    all_items.extend(fetch_cbs())

    # 4) Google Alerts / LinkedIn (indirect via alerts)
    all_items.extend(fetch_google_alerts())

    # sorteer op published_at als string
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
