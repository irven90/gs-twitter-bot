import feedparser
import requests
import re
from typing import List, Dict

RSS_FEEDS = [
    {"source": "Google News (Galatasaray)", "url": "https://news.google.com/rss/search?q=Galatasaray&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "Google News (Süper Lig)", "url": "https://news.google.com/rss/search?q=S%C3%BCper+Lig+Futbol&hl=tr&gl=TR&ceid=TR:tr"},
    {"source": "TRT Spor Futbol", "url": "https://www.trtspor.com.tr/rss/futbol.xml"},
]

def clean_html(raw_html: str) -> str:
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_latest_football_news() -> List[Dict[str, str]]:
    """
    Fetches latest Galatasaray and Süper Lig news articles from RSS feeds.
    Returns list of dicts: {'title': str, 'summary': str, 'source': str, 'link': str}
    """
    articles = []
    
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:5]: # Top 5 per feed
                title = entry.get("title", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                link = entry.get("link", "#")
                
                if title:
                    articles.append({
                        "title": title,
                        "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                        "source": feed["source"],
                        "link": link
                    })
        except Exception as e:
            print(f"Error fetching feed {feed['source']}: {e}")
            
    # Add default fallback topics if feeds fail
    if not articles:
        articles = [
            {
                "title": "Galatasaray Şampiyonlar Ligi ve Lig Hazırlıklarına Devam Ediyor",
                "summary": "Sarı-kırmızılı ekip taktik antrenmanla hazırlıklarını sürdürdü. Transfer çalışmaları hız kazandı.",
                "source": "Gündem Özel",
                "link": "#"
            },
            {
                "title": "Süper Lig Hakem Kararları ve VAR Tartışmaları",
                "summary": "Son haftada yaşanan hakem kararları ve tartışmalı pozisyonlar hakkında taraftar tepkili.",
                "source": "Gündem Özel",
                "link": "#"
            },
            {
                "title": "Galatasaray Transfer Gündemi: Flaş İsimler Masada",
                "summary": "Yönetim orta saha ve hücum hattını güçlendirmek için temasları sıklaştırdı.",
                "source": "Gündem Özel",
                "link": "#"
            }
        ]
        
    return articles
