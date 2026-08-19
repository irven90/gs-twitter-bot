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
Amacın verilen haber veya duyumu ({topic}) AYNEN LE MARCA SPORTS FORMATINDA yazmak.

LE MARCA SPORTS TWEET FORMATI ÖRNEĞİ:
🚨 Mauro Icardi, şu an itibarıyla Lazio'nun gündeminden çıktı. Lazio, tüm odağını Andrea Pinamonti'ye verdi.

(Matteo Moretto)

KURALLAR:
1. Tweet başı emoji ile başlasın: 🚨 veya 💣 veya ⚡
2. Haber cümlesi kısa, net, haber diliyle ve vurucu yazısın. Gereksiz dolgu kelimeleri kullanma!
3. Tweetin ALT SATIRINDA parantez içinde muhabir/kaynak belirt: (Yağız Sabuncuoğlu), (Nevzat Dindar), (Fabrizio Romano) veya (X Duyum).
4. Asla gazete ismi (Fotomaç, Sözcü vs) kullanma!
5. Maksimum 200 karakter olsun.
"""

REPORTERS = ["Yağız Sabuncuoğlu", "Nevzat Dindar", "Fabrizio Romano", "Matteo Moretto", "Haluk Yürekli", "X Duyum"]

def generate_le_marca_fallback(topic: str) -> str:
    clean_t = str(topic).strip()
    # Strip newspaper names from topic
    clean_t = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', clean_t, flags=re.IGNORECASE)
    clean_t = re.sub(r'^🚨 X DUYUM \| ', '', clean_t)
    
    reporter = random.choice(REPORTERS)
    return f"🚨 {clean_t}.\n\n({reporter})"

def generate_tweet_content(*args, **kwargs) -> Dict[str, Any]:
    """
    Generates tweets matching exact Le Marca Sports format.
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
                generation_config={"temperature": 0.7}
            )
            prompt = LE_MARCA_PROMPT.format(topic=clean_topic)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 15:
        content = generate_le_marca_fallback(clean_topic)
        
    media_url = None
    media_type = "none"
    
    if mode == "graphic":
        try:
            # Generate compact 800x380 graphic card
            media_url = generate_gs_card(
                text=content[:200],
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
