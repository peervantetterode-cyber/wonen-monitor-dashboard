"""
Bronnenconfiguratie voor de Woonmonitor.

Hier definieer je:
- vaste RSS-feeds (SITE_FEEDS)
- sites zonder RSS die we desnoods scrapen (SCRAPE_SITES)
- Google News zoektermen (SEARCH_TERMS)
- Rechtspraak.nl zoektermen (RECHTSPRAAK_TERMS)
- helpers om de juiste RSS/zoek-URL's te bouwen
"""

from urllib.parse import quote_plus


# --------------------------------------------------
# Vaste RSS-bronnen (kranten, omroepen, belangenclubs)
# --------------------------------------------------

SITE_FEEDS = {
    # Financieel Dagblad (via hoofd-RSS of themakanaal)
    "FD": "https://fd.nl/rss",

    # Volkskrant
    "Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",

    # NRC
    "NRC": "https://www.nrc.nl/rss",

    # NOS Algemeen / Binnenland / Economie / Politiek
    "NOS Algemeen": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "NOS Binnenland": "https://feeds.nos.nl/nosnieuwsbinnenland",
    "NOS Economie": "https://feeds.nos.nl/nosnieuwseconomie",
    "NOS Politiek": "https://feeds.nos.nl/nosnieuwspolitiek",

    # Telegraaf (algemene nieuwsfeed)
    "Telegraaf": "https://www.telegraaf.nl/rss",

    # Follow the Money (nieuwsbrief/podcast feed)
    "Follow the Money": "https://www.ftm.nl/rss",

    # Woonbond
    "Woonbond": "https://www.woonbond.nl/feeds/nieuws",

    # Aedes (woningcorporaties)
    "Aedes: nieuws": "https://www.aedes.nl/rss.xml",

    # Cobouw (bouw / infra)
    "Cobouw": "https://www.cobouw.nl/feed",
}


# --------------------------------------------------
# Sites zonder duidelijke RSS: HTML-scrape fallback
# --------------------------------------------------

SCRAPE_SITES = {
    # Rijksoverheid (algemene homepage – scraper zoekt lange links)
    "Rijksoverheid": "https://www.rijksoverheid.nl/",

    # Aedes themapagina's (extra verdieping, zonder aparte RSS)
    "Aedes: volkshuisvesting": "https://www.aedes.nl/onderwerpen?field_thema_target_id=5B535D53",

    # Cobouw dossiertoegang (als extra ingang)
    "Cobouw: wonen & bouwen": "https://www.cobouw.nl/woningbouw",
}


# --------------------------------------------------
# Google News zoektermen (breed, maar gericht op wonen)
# --------------------------------------------------

SEARCH_TERMS = [
    # Algemeen wonen / volkshuisvesting
    "wooncrisis Nederland",
    "woningnood Nederland",
    "volkshuisvesting Nederland",
    "woningtekort Nederland",

    # Huur / huurtoeslag
    "sociale huur woningcorporaties",
    "huurtoeslag huurders",
    "wet betaalbare huur",
    "huurprijsregulering",

    # Corporaties / Aedes
    "woningcorporaties nieuwbouw",
    "Aedes corporatiesector",
    "verduurzaming corporatiewoningen",

    # Grondbeleid / planbaten
    "grondbeleid woningbouw",
    "planbatenheffing",
    "grondexploitatie gemeenten",

    # Dakloosheid / opvang
    "dakloosheid Nederland opvang",
    "maatschappelijke opvang woningnood",
]


def google_news_rss_url(term: str) -> str:
    """
    Bouw een Google News RSS-URL voor een zoekterm.

    Documentatie-inspiratie:
    - https://news.google.com/rss/search?q=...
    waarbij q de zoekterm bevat, plus optioneel taal/land-regio.[web:35][web:37]
    """
    q = quote_plus(term)
    # NL nieuws, Nederlands
    return f"https://news.google.com/rss/search?q={q}&hl=nl&gl=NL&ceid=NL:nl"


# --------------------------------------------------
# Rechtspraak.nl: zoektermen + RSS-helper
# --------------------------------------------------

RECHTSPRAAK_TERMS = [
    # Wonen / huur / corporaties
    "woonruimte",
    "huisvesting",
    "sociale huur",
    "huurwoning",
    "woningcorporatie",
    "dakloosheid",
    "huurtoeslag",
    "omgevingswet wonen",
]


def rechtspraak_rss_url(term: str) -> str:
    """
    Bouw een Rechtspraak.nl RSS-URL voor een zoekopdracht.

    Rechtspraak biedt RSS-feeds om nieuwe uitspraken te volgen, ook
    gefilterd op zoektermen.[web:40]
    De exacte zoek-URL kan per implementatie verschillen; hier gebruiken we
    de 'zoekterm' in de query en vragen om RSS-output.

    Als je later precieze filters wilt (rechtsgebied, instantie, datum),
    dan kun je hier de parameters uitbreiden op basis van de officiële
    documentatie 'Open Data van de Rechtspraak'.[web:19][web:36]
    """
    q = quote_plus(term)
    # Basisvorm: RSS-feed voor zoekresultaten op uitspraken.rechtspraak.nl
    # Deze URL-structuur is bewust simpel gehouden; fine-tuning kan later.
    return f"https://uitspraken.rechtspraak.nl/rss?search={q}"
