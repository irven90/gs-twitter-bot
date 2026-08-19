import os
import random
import re
from typing import Dict, Any
from card_generator import generate_gs_card

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

LE_MARCA_PROMPT = """
Sen X (Twitter) platformunda 'Le Marca Sports' ve Fabrizio Romano tarzında profesyonel spor haberleri yayınlayan bir futbol muhabirisin.
Amacın verilen haber başlığından ({topic}) AYNEN LE MARCA SPORTS FORMATINDA 2-3 CÜMLELİK DETAYLI KISA FUTBOL HABERİ YAZMAK.

LE MARCA SPORTS TWEET FORMATI ÖRNEKLERİ:

Örnek 1:
🚨 Galatasaray, Lucas Torreira için Avrupa'dan gelen 15 milyon Euro'luk teklifi reddetti. Yönetim ve teknik heyet oyuncunun satılmasına onay vermedi.

(Nevzat Dindar)

Örnek 2:
⚡ Mauro Icardi, Lazio'nun transfer listesinden tamamen çıktı. İtalyan kulübü odağını alternatif isimlere çevirdi.

(Matteo Moretto)

KURALLAR:
1. Tweet başı dikkat çekici emoji ile başlasın: 🚨 veya 💣 veya ⚡
2. Sadece başlığı tekrarlama! Başlıktaki olayı 2 cümlelik net, profesyonel haber diliyle açıkla.
3. Tweetin EN ALT SATIRINDA parantez içinde gerçek kaynak/muhabir belirt: Eğer haberde muhabir varsa onu yaz (ör: Nevzat Dindar, Yağız Sabuncuoğlu), yoksa (GS Muhabir Bilgisi), (Florya Haber) veya (X Duyum) yaz.
4. Asla gazete ismi (Fotomaç, Sözcü vs) kullanma!
5. Maksimum 220 karakter olsun.
"""

RICH_LE_MARCA_TEMPLATES = [
    "🚨 {topic}.\n\nGalatasaray yönetimi ve teknik heyet konu hakkında kararını verdi. Sıcak gelişmeler takip ediliyor.\n\n(GS Muhabir Bilgisi)",
    "⚡ {topic}.\n\nSarı-kırmızı yönetim masadaki şartları değerlendirmeye aldı. İmzaların kısa sürede atılması bekleniyor.\n\n(X Transfer Duyumu)",
    "💣 {topic}.\n\nFlorya'dan alınan bilgilere göre kulüp yetkilileri temasları sıklaştırdı. Resmi açıklama yakın.\n\n(Florya Haber)"
]

def extract_or_infer_reporter(topic: str) -> str:
    """Extracts known reporter from topic text or returns clean authentic insider credit."""
    t_lower = topic.lower()
    if "yağız" in t_lower or "yagiz" in t_lower:
        return "Yağız Sabuncuoğlu"
    elif "nevzat" in t_lower:
        return "Nevzat Dindar"
    elif "fabrizio" in t_lower or "romano" in t_lower:
        return "Fabrizio Romano"
    elif "haluk" in t_lower:
        return "Haluk Yürekli"
    elif "transfer" in t_lower:
        return "X Transfer Duyumu"
    elif "taraftar" in t_lower or "yorum" in t_lower:
        return "Taraftar Sesi"
    else:
        return "GS Muhabir Bilgisi"

def generate_le_marca_fallback(topic: str) -> str:
    clean_t = str(topic).strip()
    clean_t = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', clean_t, flags=re.IGNORECASE)
    clean_t = re.sub(r'^🚨 X DUYUM \| ', '', clean_t)
    
    reporter = extract_or_infer_reporter(clean_t)
    
    if len(clean_t) < 30:
        return f"🚨 {clean_t} konusunda Galatasaray kulübünde sıcak saatler yaşanıyor. Yönetim şartları değerlendiriyor.\n\n({reporter})"
    else:
        return f"🚨 {clean_t}.\n\n(Nevzat Dindar)"

def generate_tweet_content(*args, **kwargs) -> Dict[str, Any]:
    """
    Generates rich, authentic tweets matching exact Le Marca Sports format.
    """
    topic = kwargs.get("topic") if "topic" in kwargs else (args[0] if len(args) > 0 else "Galatasaray Transfer Gündemi")
    category = kwargs.get("category") if "category" in kwargs else (args[1] if len(args) > 1 else "Gündem")
    tone = kwargs.get("tone") if "tone" in kwargs else (args[2] if len(args) > 2 else "Le Marca Style")
    style = kwargs.get("style") if "style" in kwargs else (args[3] if len(args) > 3 else "Haber Formatı")
    mode = kwargs.get("mode") if "mode" in kwargs else (args[4] if len(args) > 4 else "emoji")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    content = ""
    clean_topic = str(topic).strip() if topic else "Galatasaray Transfer Gündemi"
    clean_topic = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', clean_topic, flags=re.IGNORECASE)
    clean_topic = re.sub(r'^🚨 X DUYUM \| ', '', clean_topic)
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.8}
            )
            prompt = LE_MARCA_PROMPT.format(topic=clean_topic)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 20:
        content = generate_le_marca_fallback(clean_topic)
        
    media_url = None
    media_type = "none"
    
    if mode == "graphic":
        try:
            # Generate compact 800x380 graphic card
            media_url = generate_gs_card(
                text=content[:220],
                category=category,
                title="TARAFTAR SESİ"
            )
            media_type = "image"
        except Exception as e:
            print(f"Card error: {e}")
            media_url = None
            media_type = "none"
            
    return {
        "title": clean_topic[:50],
        "content": content,
        "category": category,
        "media_type": media_type,
        "media_url": media_url
    }
