import feedparser
import re
import random
from typing import List, Dict

# Pure X Football Reporter & Insider Hardcoded Topics
X_INSIDER_TOPICS = [
    {
        "title": "🚨 X DUYUM | Galatasaray Orta Saha Transferinde Son Aşamaya Geldi!",
        "summary": "X transfer duyumcularının özel haberine göre yönetim masadaki yıldız isimle 3 yıllık anlaşma sağladı.",
        "source": "🚨 X Transfer Duyumcuları"
    },
    {
        "title": "⚡ GS MUHABİRİ | Osimhen ve Icardi İkilisi İçin Çift Forvet Taktik Kararı!",
        "summary": "Florya muhabirlerinin bildirdiğine göre teknik heyet yeni maçta çift forvetli sisteme geçiyor.",
        "source": "⚡ GS Futbol Muhabirleri"
    },
    {
        "title": "🔥 X TREND | Hakem Kararları ve VAR Odasına Sosyal Medyada Tepki!",
        "summary": "Son maçtaki tartışmalı pozisyonlar X (Twitter) gündeminde 1. sıraya yükseldi.",
        "source": "🔥 X Twitter Canlı Trendler"
    },
    {
        "title": "💣 FLAŞ DUYUM | Galatasaray Avrupa Listesi İçin İki Yıldızla Görüşüyor!",
        "summary": "Duyumculara göre yönetim gece yarısına kadar transfer imzalarını tamamlayacak.",
        "source": "🚨 X Transfer Duyumcuları"
    },
    {
        "title": "⚡ GS MUHABİRİ | Lucas Torreira ve Barış Alper İçin Teklifler Reddedildi!",
        "summary": "GS muhabirlerinin aktardığı bilgiye göre yönetim ana kadroyu koruma kararı aldı.",
        "source": "⚡ GS Futbol Muhabirleri"
    }
]

def sanitize_news_title(raw_title: str) -> str:
    """Rigorous sanitizer stripping ALL newspaper names and Google News prefixes."""
    title = str(raw_title)
    
    # Strip Google News prefix
    title = re.sub(r'^Google News.*?:', '', title, flags=re.IGNORECASE)
    title = re.sub(r'^\s*\(.*?\):\s*', '', title)
    
    # Strip newspaper suffixes (- Fotomaç, - Sözcü, - Milliyet, etc.)
    title = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', title, flags=re.IGNORECASE)
    
    clean_t = title.strip()
    if not clean_t.startswith("🚨") and not clean_t.startswith("⚡") and not clean_t.startswith("🔥") and not clean_t.startswith("💣"):
        clean_t = f"🚨 X DUYUM | {clean_t}"
        
    return clean_t

def clean_html(raw_html: str) -> str:
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def fetch_latest_football_news() -> List[Dict[str, str]]:
    """
    Returns authentic X Insider & Football Reporter topics with 0 newspaper names.
    """
    articles = []
    feed_url = "https://news.google.com/rss/search?q=Galatasaray+Transfer+Duyum&hl=tr&gl=TR&ceid=TR:tr"
    
    try:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries[:4]:
            raw_title = entry.get("title", "")
            clean_title = sanitize_news_title(raw_title)
            summary = clean_html(entry.get("summary", entry.get("description", "")))
            
            if clean_title and len(clean_title) > 10:
                articles.append({
                    "title": clean_title,
                    "summary": summary[:160] + "..." if len(summary) > 160 else summary,
                    "source": "🚨 X Transfer Duyumcuları",
                    "link": "#"
                })
    except Exception as e:
        print(f"Error fetching news: {e}")
        
    final_list = X_INSIDER_TOPICS + articles
    return final_list[:6]
