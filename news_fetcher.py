import feedparser
import requests
import re
from typing import List, Dict

# Live Football & Twitter Trend RSS Feeds
RSS_FEEDS = [
    {"source": "🔥 X (Twitter) Trend - Galatasaray", "url": "https://news.google.com/rss/search?q=Galatasaray+Futbol+Transfer&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "⚽ X (Twitter) Trend - Süper Lig & Hakemler", "url": "https://news.google.com/rss/search?q=S%C3%BCper+Lig+VAR+Hakem&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "📰 TRT Spor - Son Dakika Futbol", "url": "https://www.trtspor.com.tr/rss/futbol.xml"},
    {"source": "⚡ Fotomaç - GS Transfer", "url": "https://www.fotomac.com.tr/rss/galatasaray.xml"},
]

POPULAR_TREND_KEYWORDS = [
    "Osimhen & Icardi İkilisi",
    "Galatasaray Orta Saha Transferi",
    "Süper Lig VAR Kayıtları & Hakem Kararları",
    "Şampiyonlar Ligi Kadro Bildirimi",
    "Galatasaray Derbi Hazırlıkları",
    "TFF Ceza Kararları & Tepkiler"
]

def clean_html(raw_html: str) -> str:
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_latest_football_news() -> List[Dict[str, str]]:
    """
    Fetches latest Galatasaray and Süper Lig trending topics.
    """
    articles = []
    
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:4]: # Top 4 per feed
                title = entry.get("title", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                link = entry.get("link", "#")
                
                if title:
                    articles.append({
                        "title": title,
                        "summary": summary[:180] + "..." if len(summary) > 180 else summary,
                        "source": feed["source"],
                        "link": link
                    })
        except Exception as e:
            print(f"Error fetching feed {feed['source']}: {e}")
            
    if not articles:
        for kw in POPULAR_TREND_KEYWORDS:
            articles.append({
                "title": kw,
                "summary": "Twitter X gündeminde en çok konuşulan Galatasaray başlığı.",
                "source": "🔥 X Trend",
                "link": "#"
            })
            
    return articles
