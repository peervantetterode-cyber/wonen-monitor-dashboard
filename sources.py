# Configuration of all sources for the woonmonitor dashboard

SITE_FEEDS = {
    "FD": "https://fd.nl/?rss",
    "Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
    "NOS Algemeen": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "NOS Binnenland": "https://feeds.nos.nl/nosnieuwsbinnenland",
    "NOS Politiek": "https://feeds.nos.nl/nosnieuwspolitiek",
    "NOS Economie": "https://feeds.nos.nl/nosnieuwseconomie",
    "AD": "https://www.ad.nl/rss/overzicht/",
    "Telegraaf": "https://telegraaf.nl/rss",
    "Follow the Money (FTM)": "https://www.ftm.nl/rss",
    "RTL Nieuws": "https://www.rtlnieuws.nl/service/rss/nieuws/index.xml",
    "Officiele Bekendmakingen": "https://zoek.officielebekendmakingen.nl/rss",
}

SCRAPE_SITES = {
    "NRC": "https://www.nrc.nl/",
    "Follow the Money": "https://www.ftm.nl/",
    "Aedes": "https://www.aedes.nl/nieuws",
    "Rijksoverheid": "https://www.rijksoverheid.nl/actueel/nieuws",
    "Woonbond": "https://www.woonbond.nl/nieuws",
    "Cobouw": "https://www.cobouw.nl/",
    "Vastgoednieuws": "https://www.vastgoedmarkt.nl/",
    "PropertyNL": "https://propertynl.com/",
}

SEARCH_TERMS = [
    "\"Peer van Tetterode\"",
    "ANP AND woningmarkt",
    "corporaties",
    "FD AND huizen",
    "FD AND huizenmarkt",
    "FD AND woningmarkt",
    "hypotheek",
    "Kamervragen AND \"Follow the Money\"",
    "NRC AND huizen",
    "NRC AND woningmarkt",
    "\"sociale huur\"",
    "vastgoed",
    "woning",
    "woningmarkt",
]

RECHTSPRAAK_TERMS = [
    "vastgoed",
    "huurrecht",
    "woningcorporatie",
    "sociale huur",
]

def rechtspraak_rss_url(term: str) -> str:
    import urllib.parse
    q = urllib.parse.quote(term)
    return f"https://uitspraken.rechtspraak.nl/rss?q={q}"

def google_news_rss_url(term: str) -> str:
    import urllib.parse
    q = urllib.parse.quote(term)
    return f"https://news.google.com/rss/search?q={q}&hl=nl&gl=NL&ceid=NL:nl"
