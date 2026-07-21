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
from sources import (
    SITE_FEEDS,
    SCRAPE_SITES,
    SEARCH_TERMS,
    google_news_rss_url,
    RECHTSPRAAK_TERMS,
    rechtspraak_rss_url,
)

# --------------------------------------------------
# Config (headers / timeouts)
# --------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WoonmonitorBot/1.0; +https://example.com)"
}
TIMEOUT = 10

# --------------------------------------------------
# Keywords: alles uit de Kingma‑tekst, geclusterd
# --------------------------------------------------

WOON_KEYWORDS = [
    # Dakloosheid / mensenrecht / woningnood
    "dakloos", "daklozen", "dakloosheid",
    "thuisloos", "thuislozen", "thuisloosheid",
    "zwerver", "zwervers", "zwerfjongeren",
    "opvang", "noodopvang", "crisisopvang",
    "nachtopvang", "winteropvang",
    "maatschappelijke opvang",
    "bed-bad-brood",
    "recht op huisvesting",
    "huisvesting als mensenrecht",
    "voldoende woongelegenheid",
    "woningnood", "huisvestingscrisis",
    "woningtekort",

    # Volkshuisvesting / sociale huur / wachttijd
    "volkshuisvesting",
    "sociale huur", "sociale huurwoning", "sociale huurwoningen",
    "betaalbare huurwoningen", "betaalbare huur",
    "huurprijs", "huurprijzen",
    "huurverhoging", "huurverlaging",
    "huurtoeslag",
    "woningvoorraad", "bestaande woningvoorraad",
    "wachtlijst", "wachttijd", "wachtrij", "inschrijfduur",

    # Woningmarkt / koop / huur / starters
    "woningmarkt", "huizenmarkt",
    "koopwoning", "koopwoningen",
    "huursector", "huurmarkt",
    "vrije sector", "vrije huursector", "middenhuur",
    "private sector", "private huurmarkt",
    "huurders", "kopers",
    "starters", "starter op de woningmarkt",
    "eenpersoonshuishoudens", "alleenstaanden",
    "woonlasten", "huurlast", "maximaal verantwoorde huurlast",
    "huizenprijzen", "huizenprijs", "koopprijzen",
    "overwaarde", "eigenwoningwaarde",

    # Financiering / hypotheken / fiscale regelingen
    "hypotheek", "hypotheken",
    "hypotheekmarkt", "hypotheekschuld",
    "hypotheekrenteaftrek",
    "leenruimte", "maximale leenbedrag", "maximale hypotheek",
    "loan-to-value", "loan to value",
    "loan-to-income", "loan to income",
    "fiscale regeling", "fiscale regelingen",
    "belastingvrij schenken", "jubelton",
    "schenking voor de eigen woning",
    "box 3", "vermogensrendementsheffing",
    "subsidieprogramma", "bouwsubsidies", "bouwsubsidie",

    # Grondbeleid / planbaten / grondprijzen
    "grondbeleid", "grondmarkt",
    "bouwgrond", "bouwlocatie", "bouwlocaties",
    "grondprijs", "grondprijzen",
    "grondexploitatie", "grondexploitatieplan",
    "grondposities", "grondpositie",
    "grondeigenaar", "grondeigenaren",
    "agrarische grond", "landbouwgrond",
    "bestemmingswijziging", "bestemmingsplanwijziging",
    "woonbestemming",
    "planbaten", "planbatenheffing",
    "grondwaardestijging", "grondwaardebelasting",
    "onbebouwde bouwgrond",
    "erfpacht", "erfpachtcanon", "canon",
    "grondbedrijf",

    # Beleggers / speculatie / tweede woningen
    "beleggers", "vastgoedbeleggers", "institutionele beleggers",
    "speculanten", "speculatie op de woningmarkt",
    "particuliere verhuur", "particuliere verhuurders",
    "tweede woning", "tweede woningen",
    "buy-to-let", "buy to let",
    "verhuurhypotheek",
    "uitponden",

    # Bouw / ontwikkeltraject / regels / nieuwe woonvormen
    "nieuwbouw", "woningbouw", "woningbouwplannen", "woningbouwproject",
    "bouwproductie", "bouwplannen", "bouwkosten",
    "ontwikkeltraject", "projectontwikkelaar", "projectontwikkelaars",
    "doorlooptijd", "omgevingsplan", "gebiedsontwikkeling",
    "bouwvergunningen", "vergunningsprocedures",
    "stikstofvergunning", "stikstofcrisis",
    "natura 2000",
    "co2-norm", "co2 normen", "duurzaam bouwen",
    "renovatie", "renoveren", "sloopnieuwbouw",
    "woningsplitsing", "splitsen van woningen",
    "verdieping bijbouwen", "optoppen",
    "tijdelijke woningen", "tijdelijke woonvoorzieningen",
    "alternatieve woonvormen", "nieuwe woonvormen",
    "eigendomsstructuren",

    # Corporaties / belastingen / financiële spagaat
    "woningcorporatie", "woningcorporaties", "corporatie", "corporaties",
    "corporatiesector",
    "woningwet", "verhuurderheffing",
    "winstbelasting corporaties", "vennootschapsbelasting corporaties",
    "speculatie in vastgoed",
    "financieel mismanagement", "wanbestuur",
    "nieuwbouwopgave", "bouwproductie corporaties",
    "onderhoud", "verduurzaming woningvoorraad",
    "huurverlaging", "inkomensafhankelijke huurverlaging",
    "schuld corporaties", "leningen corporaties",

    # Regie / politiek / oplossingen
    "wooncrisis",
    "minister voor volkshuisvesting",
    "ministerie van volkshuisvesting en ruimtelijke ordening",
    "vro", "regie terugpakken", "regie op de volkshuisvesting",
    "bouwen bouwen bouwen",
    "betaalbaarheidsgrens",
    "wet betaalbare huur", "huurprijsregulering",
    "geldkraan", "bieden op de woningmarkt",
    "banken als geldscheppende instellingen",
    "belasting op onbebouwde bouwgrond",
    "publiek financieringsplan",
    "planetaire grenzen",
    "woning als speculatief object",
    "huis weer om in te wonen",
]

# --------------------------------------------------
# Minder agressieve stopwoorden: vooral sport
# --------------------------------------------------

STOP_WORDS = [
    "eredivisie", "keuken kampioen divisie",
    "champions league", "europa league",
    "wk voetbal", "ek voetbal",
    "grand prix", "formule 1", "tour de france",

    "ajax", "psv", "feyenoord", "az alkmaar",
    "fc utrecht", "fc twente", "fc groningen",
    "sc heerenveen", "nec nijmegen", "nac breda",
    "vvv-venlo", "heracles", "sparta rotterdam",
]

# --------------------------------------------------
# Prioriteit op basis van subset van de keywords
# --------------------------------------------------

HIGH_PRIORITY_KEYWORDS = [
    # Kern van de wooncrisis
    "dakloosheid", "dakloos", "thuisloosheid",
    "volkshuisvesting", "woningnood", "wooncrisis", "woningtekort",
    "sociale huur", "sociale huurwoningen",
    "woningcorporatie", "woningcorporaties", "corporatiesector",
    "huurtoeslag", "huurprijs", "huurprijzen", "huurverhoging",
    "grondbeleid", "grondexploitatie", "grondprijs", "grondprijzen",
    "planbaten", "planbatenheffing",
    "hypotheekrenteaftrek", "hypotheekschuld",
    "beleggers", "vastgoedbeleggers", "uitponden",
]

MEDIUM_PRIORITY_KEYWORDS = [
    "huisvesting", "woningvoorraad", "bestaande woningvoorraad",
    "woonlasten", "huurlast",
    "starters", "starter op de woningmarkt",
    "middenhuur", "vrije sector", "vrije huursector",
    "koopwoning", "koopwoningen",
    "huurmarkt", "huursector",
    "woningbouw", "woningbouwplannen", "nieuwbouw",
    "bouwlocatie", "bouwlocaties", "grondmarkt",
    "projectontwikkelaar", "projectontwikkelaars",
    "woningsplitsing", "renovatie", "sloopnieuwbouw",
    "ouderenwoning", "seniorenwoning",
]


def get_priority(item: dict) -> str:
    """
    Bepaal prioriteit voor het dashboard:
    - 'skip'  : duidelijk sport / irrelevant
    - 'high'  : kern wooncrisis/dakloosheid/grond/hypotheek/corporaties
    - 'medium': woon-achtig, maar iets minder kern
    - 'low'   : raakt wonen wel, maar alleen via bredere woorden
    """
    text = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        item.get("description", ""),
        item.get("source", ""),
    ]).lower()

    if any(stop in text for stop in STOP_WORDS):
        return "skip"

    if any(kw in text for kw in HIGH_PRIORITY_KEYWORDS):
        return "high"

    if any(kw in text for kw in MEDIUM_PRIORITY_KEYWORDS):
        return "medium"

    if any(kw in text for kw in WOON_KEYWORDS):
        return "low"

    return "skip"


def is_relevant(item: dict) -> bool:
    """
    Simpele ja/nee-filter:
    - weg als 'skip'
    - houden als er überhaupt een woon-achtig keyword in zit
    """
    prio = get_priority(item)
    if prio == "skip":
        return False

    text = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        item.get("description", ""),
        item.get("source", ""),
    ]).lower()

    return any(kw in text for kw in WOON_KEYWORDS)


# --------------------------------------------------
# Fetch-functies
# --------------------------------------------------

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


# --------------------------------------------------
# HTML-generatie
# --------------------------------------------------

def generate_html(items, generated_at):
    by_source = {}
    for it in items:
        by_source.setdefault(it["source"], []).append(it)

    html = [
        "<!DOCTYPE html><html lang='nl'><head><meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        "<title>Woonmonitor Dashboard</title>",
        "<style>",
        "body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1100px;margin:0 auto;padding:24px;background:#fafafa;color:#1a1a1a;}",
        "h1{font-size:1.8rem;margin-bottom:8px;} h2{font-size:1.1rem;border-bottom:2px solid #ddd;padding-bottom:6px;margin-top:32px;}",
        "ul{list-style:none;padding:0;} li{padding:10px 0;border-bottom:1px solid #eee;}",
        "a{color:#0645ad;text-decoration:none;} a:hover{text-decoration:underline;}",
        ".meta{color:#777;font-size:0.9rem;} .ts{color:#999;font-size:0.8rem;margin-left:8px;}",
        ".toolbar{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 24px 0;}",
        ".filter-btn{border:1px solid #d1d5db;background:#fff;color:#111;padding:8px 12px;border-radius:999px;cursor:pointer;font-size:0.9rem;}",
        ".filter-btn.active{background:#111;color:#fff;border-color:#111;}",
        ".prio{display:inline-block;font-size:0.75rem;border-radius:999px;padding:2px 8px;margin-left:8px;font-weight:600;vertical-align:middle;}",
        ".prio-high{background:#b91c1c;color:#fff;}",
        ".prio-medium{background:#f59e0b;color:#111;}",
        ".prio-low{background:#e5e7eb;color:#111;}",
        ".item{display:block;}",
        ".item.hidden{display:none;}",
        ".source-block.hidden{display:none;}",
        ".count{font-size:0.9rem;color:#666;margin-bottom:12px;}",
        "</style></head><body>",
        f"<h1>Woonmonitor Dashboard</h1><p class='meta'>Laatst bijgewerkt: {generated_at}</p>",
        "<div class='toolbar' id='filters'>",
        "<button class='filter-btn active' data-filter='all'>Alles</button>",
        "<button class='filter-btn' data-filter='high'>Alleen prio</button>",
        "<button class='filter-btn' data-filter='high-medium'>Prio + middel</button>",
        "<button class='filter-btn' data-filter='low'>Alleen laag</button>",
        "</div>",
        "<p class='count' id='visible-count'></p>",
    ]

    for source, entries in by_source.items():
        html.append(f"<section class='source-block' data-source='{source}'><h2>{source}</h2><ul>")
        for e in entries:
            pub = f"<span class='ts'>{e['published']}</span>" if e.get("published") else ""
            prio = e.get("priority", "low")
            prio_class = f"prio prio-{prio}"
            prio_label = {"high": "PRIO", "medium": "MID", "low": "LAAG"}.get(prio, "LAAG")

            html.append(
                f"<li class='item' data-priority='{prio}'>"
                f"<a href='{e['link']}' target='_blank'>{e['title']}</a>"
                f"<span class='{prio_class}'>{prio_label}</span>"
                f"{pub}"
                f"</li>"
            )
        html.append("</ul></section>")

    html.append("""
<script>
(function () {
  const buttons = document.querySelectorAll('.filter-btn');
  const items = document.querySelectorAll('.item');
  const blocks = document.querySelectorAll('.source-block');
  const countEl = document.getElementById('visible-count');

  function matchesFilter(priority, filter) {
    if (filter === 'all') return true;
    if (filter === 'high') return priority === 'high';
    if (filter === 'high-medium') return priority === 'high' || priority === 'medium';
    if (filter === 'low') return priority === 'low';
    return true;
  }

  function updateCount() {
    const visibleItems = [...document.querySelectorAll('.item')].filter(
      el => !el.classList.contains('hidden')
    ).length;
    countEl.textContent = `Zichtbare artikelen: ${visibleItems}`;
  }

  function applyFilter(filter) {
    items.forEach(item => {
      const priority = item.dataset.priority;
      if (matchesFilter(priority, filter)) {
        item.classList.remove('hidden');
      } else {
        item.classList.add('hidden');
      }
    });

    blocks.forEach(block => {
      const visibleInBlock = block.querySelectorAll('.item:not(.hidden)').length;
      if (visibleInBlock === 0) {
        block.classList.add('hidden');
      } else {
        block.classList.remove('hidden');
      }
    });

    buttons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filter);
    });

    updateCount();
  }

  buttons.forEach(button => {
    button.addEventListener('click', function () {
      applyFilter(this.dataset.filter);
    });
  });

  applyFilter('all');
})();
</script>
""")

    html.append("</body></html>")

    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write("\n".join(html))

# --------------------------------------------------
# main()
# --------------------------------------------------

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

    # prioriteit toevoegen en irrelevante items skippen
    enriched = []
    for it in all_items:
        prio = get_priority(it)
        if prio == "skip":
            continue
        it = dict(it)
        it["priority"] = prio
        enriched.append(it)

    print(f"Filtered down from {len(all_items)} to {len(enriched)} relevant items.")
    all_items = enriched

    os.makedirs("output", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    with open("output/monitor_data.json", "w", encoding="utf-8") as f:
        json.dump({"generated_at": now, "items": all_items}, f, ensure_ascii=False, indent=2)

    generate_html(all_items, now)
    print(f"Done. {len(all_items)} unique relevant items collected.")


if __name__ == "__main__":
    main()
