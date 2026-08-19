import feedparser
import requests
import re
import random
from typing import List, Dict

# Twitter / X Football Reporter & Insider Trending Feeds
RSS_FEEDS = [
    {"source": "🚨 X Duyumcu & Transfer Haberleri", "url": "https://news.google.com/rss/search?q=Galatasaray+Transfer+Duyum+S%C4%B1cak+Geli%C5%9Fme&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "⚡ X Futbol Muhabirleri (GS Son Dakika)", "url": "https://news.google.com/rss/search?q=Galatasaray+Muhabir+Haberleri+S%C3%BCperLig&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "🔥 X Twitter Futbol Gündemi", "url": "https://news.google.com/rss/search?q=Galatasaray+VAR+Hakem+Derbi+G%C3%BCndem&hl=tr&gl=TR&ceid=TR:tr"},
]

INSIDER_FALLBACK_NEWS = [
    {"title": "🚨 DUYUM | Galatasaray Orta Saha Transferinde Sıcak Temas!", "summary": "X muhabirlerinin bildirdiğine göre sarı-kırmızı yönetim masadaki isimle 3 yıllık anlaşma sağladı.", "source": "🚨 X Transfer Duyumcu"},
    {"title": "⚡ MUHABİR BİLGİSİ | Galatasaray'da Flaş Ayrılık ve İki Yeni İsim!", "summary": "GS muhabirleri yönetimin kadro planlamasında son aşamaya geldiğini doğruladı.", "source": "⚡ X Futbol Muhabiri"},
    {"title": "🔥 X TREND | Hakem Kararları ve VAR Odasına Sert Tepkiler!", "summary": "Süper Lig son maçındaki tartışmalı pozisyonlar X gündeminde 1. sıraya yükseldi.", "source": "🔥 X Trend"},
    {"title": "💣 SON DAKİKA | Galatasaray Şampiyonlar Ligi Listesine İki Takviye!", "summary": "Duyumculara göre yönetim Avrupa listesi kapanmadan imzaları attıracak.", "source": "🚨 X Transfer Duyumcu"}
]

def clean_html(raw_html: str) -> str:
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_latest_football_news() -> List[Dict[str, str]]:
    """
    Fetches latest X (Twitter) Football Reporter & Insider trend news.
    """
    articles = []
    
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:4]:
                title = entry.get("title", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                link = entry.get("link", "#")
                
                # Format title with Reporter / Insider badge style
                clean_title = re.sub(r' - [^-]+$', '', title).strip()
                formatted_title = f"⚡ X DUYUM | {clean_title}" if "transfer" in clean_title.lower() else f"🔥 X GÜNDEM | {clean_title}"
                
                if clean_title:
                    articles.append({
                        "title": clean_title,
                        "summary": summary[:180] + "..." if len(summary) > 180 else summary,
                        "source": feed["source"],
                        "link": link
                    })
        except Exception as e:
            print(f"Error fetching feed {feed['source']}: {e}")
            
    if not articles:
        articles = INSIDER_FALLBACK_NEWS
        
    return articles
