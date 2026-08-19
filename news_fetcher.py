import feedparser
import requests
import re
import random
from typing import List, Dict

# Twitter / X Football Reporter & Insider Trending Feeds
RSS_FEEDS = [
    {"source": "🚨 X Transfer Duyumcuları", "url": "https://news.google.com/rss/search?q=Galatasaray+Transfer+Duyum+S%C4%B1cak+Geli%C5%9Fme&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "⚡ GS Futbol Muhabirleri", "url": "https://news.google.com/rss/search?q=Galatasaray+Muhabir+Haberleri+S%C3%BCperLig&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "🔥 X Twitter Canlı Trendler", "url": "https://news.google.com/rss/search?q=Galatasaray+VAR+Hakem+Derbi+G%C3%BCndem&hl=tr&gl=TR&ceid=TR:tr"},
]

NEWSPAPER_PATTERNS = [
    r'\s*-\s*Fotomaç.*$', r'\s*-\s*Sözcü.*$', r'\s*-\s*Haber\s*7.*$', r'\s*-\s*Milliyet.*$',
    r'\s*-\s*Mynet.*$', r'\s*-\s*A\s*Spor.*$', r'\s*-\s*Fanatik.*$', r'\s*-\s*Hurriyet.*$',
    r'\s*-\s*TRT\s*Spor.*$', r'\s*-\s*Sabah.*$', r'\s*-\s*NTV\s*Spor.*$', r'Google News.*'
]

INSIDER_FOOTBALL_TOPICS = [
    {"title": "🚨 X DUYUM | Galatasaray Orta Saha Transferinde Son Aşamaya Geldi!", "summary": "X transfer duyumcularının özel haberine göre yönetim oyuncu ve kulübüyle 3 yıllık prensip anlaşmasına vardı.", "source": "🚨 X Transfer Duyumcuları"},
    {"title": "⚡ GS MUHABİRİ | Osimhen ve Icardi İkilisi İçin Özel Taktik Hazırlığı!", "summary": "Sarı-kırmızı muhabirlerin tesislerden bildirdiğine göre teknik heyet çift forvetli sisteme geçiyor.", "source": "⚡ GS Futbol Muhabirleri"},
    {"title": "🔥 X TREND | Hakem ve VAR Odası Kararlarına Sosyal Medyada Büyük Tepki!", "summary": "Son maçtaki tartışmalı pozisyonlar X gündeminde 1. sıraya yerleşti.", "source": "🔥 X Twitter Canlı Trendler"},
    {"title": "💣 FLAŞ DUYUM | Galatasaray Avrupa Listesi İçin İki Yıldızla Görüşüyor!", "summary": "Duyumculara göre yönetim gece yarısına kadar transferleri bitirmeyi hedefliyor.", "source": "🚨 X Transfer Duyumcuları"},
    {"title": "⚡ GS MUHABİRİ | Lucas Torreira ve Barış Alper İçin Teklifler Reddedildi!", "summary": "Muhabirlerin aktardığı bilgiye göre yönetim ana kadroyu koruma kararı aldı.", "source": "⚡ GS Futbol Muhabirleri"}
]

def clean_title_for_x_insiders(raw_title: str) -> str:
    """Strips all newspaper/media suffixes and prefixes to make titles look like authentic Twitter insider posts."""
    title = raw_title
    for pattern in NEWSPAPER_PATTERNS:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    return title.strip()

def clean_html(raw_html: str) -> str:
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_latest_football_news() -> List[Dict[str, str]]:
    """
    Fetches X Football Reporter & Insider trending topics with NO newspaper names.
    """
    articles = []
    
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:3]:
                raw_title = entry.get("title", "")
                clean_title = clean_title_for_x_insiders(raw_title)
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                
                if clean_title and len(clean_title) > 10:
                    articles.append({
                        "title": clean_title,
                        "summary": summary[:160] + "..." if len(summary) > 160 else summary,
                        "source": feed["source"],
                        "link": "#"
                    })
        except Exception as e:
            print(f"Error fetching feed {feed['source']}: {e}")
            
    if not articles or len(articles) < 3:
        articles = INSIDER_FOOTBALL_TOPICS
        
    return articles
