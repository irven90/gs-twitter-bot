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

# High-Engagement Gemini Prompts per Persona/Tone Mode
PERSONA_PROMPTS = {
    "Organik Taraftar Ağzı (@Boss_Osimhen)": """
Sen X (Twitter) platformunda @Boss_Osimhen adıyla bilinen tutkulu, lafını sakınmayan, stadyum ve kahvehane sohbeti doğallığında konuşan GERÇEK BİR GALATASARAY TARAFTARISIN.
Gündem / Konu: "{topic}"

KURALLAR:
1. Kesinlikle gazete veya muhabir haberini kopyalama! Kendi samimi insan yorumunu yaz.
2. "Abi valla bakıyorum da...", "Yok artık yahu!", "Net söylüyorum Osimhen bu takıma sınıf atlattı!", "Şu olaya gülsem mi ağlasam mı bilemedim..." gibi doğal insan kalıpları kullan.
3. Hakem kararlarına veya rakiplere taraftar tepkisi ver, GS yıldızlarını göklere çıkar!
4. Sonuna 1-2 doğal hashtag ekle (#Galatasaray #GS).
5. Karakter sınırı: Max 220 karakter.
""",
    "Le Marca Style (Haber & Kaynak)": """
Sen X'te 'Le Marca Sports' ve Fabrizio Romano tarzında profesyonel spor haberleri veren bir futbol muhabirisin.
Gündem / Konu: "{topic}"

KURALLAR:
1. 🚨 veya ⚡ emoji ile başla.
2. Konuyu 2 cümlelik net, profesyonel haber diliyle açıkla.
3. En alt satırda parantez içinde kaynak belirt: (Nevzat Dindar), (Yağız Sabuncuoğlu) veya (GS Muhabir Bilgisi).
4. Max 200 karakter.
""",
    "📊 X Anket Formatı": """
Sen @Boss_Osimhen olarak verilen konu ({topic}) hakkında takipçilerinin oy kullanacağı viralliği yüksek bir X Anketi hazırlıyorsun.

FORMAT:
[Vurucu Anket Sorusu]

A) [Seçenek 1] 🔥
B) [Seçenek 2] ⚽
C) [Seçenek 3] 🦁
D) [Seçenek 4] 💛❤️

#Galatasaray #GS
""",
    "💬 Alıntı & Tepki Tweeti": """
Sen @Boss_Osimhen olarak verilen habere ({topic}) 1-2 cümlelik şok verici, samimi ve doğal bir insan tepkisi yazıyorsun.
Örnek: "Şu haberin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 🦁 #GS"
""",
    "🚨 Flaş Son Dakika": """
Sen @Boss_Osimhen olarak Galatasaray gündemindeki bu konu ({topic}) hakkında yüksek Retweet alacak bir Son Dakika haber tweeti yazıyorsun.
"""
}

# Rich Fallback Database (Never repeats raw title!)
RICH_FALLBACKS = {
    "Organik Taraftar Ağzı (@Boss_Osimhen)": [
        "Abi valla {topic} konusunu görünce gülüyorum artık. Kimse boşuna heveslenmesin, bu takım şampiyonluğa odaklandı kardeş! 💛❤️ #Galatasaray",
        "Yok artık yahu! {topic} hakkında yapılan şu yorumlar tam bir akıl tutulması. Galatasaray taraftarı bu masalları yemez! 🦁🔥 #GS",
        "Net söylüyorum: {topic} konusunda Osimhen ve ekibi sahaya çıktı mı kimsede laf kalmaz! Bize laf değil icraat lazım abi! 💛❤️ #Galatasaray",
        "Vallahi billahi pes! {topic} hakkında konuşanlar Galatasaray'ın sahadaki gücünü görmezden geliyor. Şampiyon biz olacağız! 🦁💛❤️ #GS"
    ],
    "Le Marca Style (Haber & Kaynak)": [
        "🚨 {topic} hakkında Florya'dan sıcak bilgi ulaştı. Sarı-kırmızı yönetim masadaki tüm şartları inceliyor.\n\n(Nevzat Dindar)",
        "⚡ {topic} konusunda kulüp yetkilileri temasları sıklaştırdı. Resmi açıklamanın yakında yapılması bekleniyor.\n\n(GS Muhabir Bilgisi)"
    ],
    "📊 X Anket Formatı": [
        "Sizce {topic} konusunda yönetim ne yapmalı taraftar?\n\nA) Hemen Bitirmeli 🔥\nB) Alternatif Bakmalı ⚽\nC) Beklemeli 🦁\nD) İptal Edilmeli ❌\n\nYorumlarda buluşalım! 💛❤️ #Galatasaray",
        "{topic} haberi hakkında görüşünüz nedir sarı-kırmızılılar?\n\nA) Tamamen Doğru ✅\nB) Yanlış Haber ❌\nC) Kararsızım 🤔\n\n#Galatasaray #GS"
    ],
    "💬 Alıntı & Tepki Tweeti": [
        "Şu haberin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 🦁 #GS",
        "Hahaha yahu şaka gibi açıklama! Güneş balçıkla sıvanmaz kardeş, Galatasaray'ın büyüklüğü ortada! 💛❤️ #Galatasaray"
    ],
    "🚨 Flaş Son Dakika": [
        "💣 FLAŞ GÜNDEM: {topic} konusunda sıcak saatler yaşanıyor! Detaylar ve gelişmeler yolda. 💛❤️ #Galatasaray",
        "🚨 SON DAKİKA: {topic} hakkında sarı-kırmızılı cepheden ilk hamle geldi! 🦁🔥 #GS"
    ]
}

def clean_topic_str(topic: str) -> str:
    t = str(topic).strip()
    t = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^🚨 X DUYUM \| ', '', t)
    return t

def generate_tweet_content(*args, **kwargs) -> Dict[str, Any]:
    """
    Generates rich, authentic human fan tweets matching @Boss_Osimhen persona or Le Marca style.
    """
    topic = kwargs.get("topic") if "topic" in kwargs else (args[0] if len(args) > 0 else "Galatasaray Transfer Gündemi")
    category = kwargs.get("category") if "category" in kwargs else (args[1] if len(args) > 1 else "Gündem")
    tone = kwargs.get("tone") if "tone" in kwargs else (args[2] if len(args) > 2 else "Organik Taraftar Ağzı (@Boss_Osimhen)")
    style = kwargs.get("style") if "style" in kwargs else (args[3] if len(args) > 3 else "Tartışma & Yorum Alıcı")
    mode = kwargs.get("mode") if "mode" in kwargs else (args[4] if len(args) > 4 else "emoji")
    
    gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    content = ""
    clean_topic = clean_topic_str(topic)
    
    # Pick prompt matching selected tone/persona
    sys_prompt = PERSONA_PROMPTS.get(tone, PERSONA_PROMPTS.get(style, PERSONA_PROMPTS["Organik Taraftar Ağzı (@Boss_Osimhen)"]))
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.95}
            )
            prompt = sys_prompt.format(topic=clean_topic)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 20:
        templates = RICH_FALLBACKS.get(tone, RICH_FALLBACKS.get(style, RICH_FALLBACKS["Organik Taraftar Ağzı (@Boss_Osimhen)"]))
        raw_template = random.choice(templates)
        content = raw_template.format(topic=clean_topic)
        
    media_url = None
    media_type = "none"
    
    if mode == "graphic":
        try:
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
