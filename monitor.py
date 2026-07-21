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
        "source_id": "min_vro_nieuws",
        "source_name": "Ministerie VRO",
        "source_category": "policy",
        "url": "https://feeds.rijksoverheid.nl/ministeries/ministerie-van-volkshuisvesting-en-ruimtelijke-ordening/nieuws.rss"
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
            
