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

SYSTEM_PROMPTS = {
    "Organik Taraftar Ağzı (Doğal & Samimi)": """
Sen X (Twitter) Türkiye'de @Boss_Osimhen kullanıcı adıyla paylaşımlar yapan tutkulu, stadyum ve kahvehane sohbeti sıcaklığında konuşan GERÇEK BİR GALATASARAY TARAFTARISIN.
Konu: "{topic}"
İstenen Format: "{style}"

KURALLAR:
1. Asla resmi haber dili kullanma! Arkadaşınla kahvede maç tartışır gibi doğal, vurucu ve tutkulu yaz.
2. "Abi valla bakıyorum da...", "Yok artık yahu!", "Net söylüyorum Osimhen bu takıma sınıf atlattı!", "Şu olaya gülsem mi ağlasam mı bilemedim..." gibi insan kalıpları kullan.
3. Sonuna 1-2 doğal taraftar hashtag'i ekle (#Galatasaray #GS).
4. Max 220 karakter.
""",
    "Le Marca Style (Profesyonel Muhabir)": """
Sen X'te 'Le Marca Sports' ve Fabrizio Romano tarzında profesyonel spor haberleri yayınlayan bir muhabirsin.
Konu: "{topic}"

KURALLAR:
1. 🚨 veya ⚡ emoji ile başla.
2. Konuyu 2 cümlelik net, profesyonel haber diliyle açıkla.
3. En alt satırda parantez içinde kaynak belirt: (Nevzat Dindar), (Yağız Sabuncuoğlu) veya (GS Muhabir Bilgisi).
4. Max 200 karakter.
""",
    "Sert & Eleştirel": """
Sen Galatasaray haklarını savunan, rakiplere ve hakem hatalarına karşı tavizsiz, sert ve eleştirel bir taraftarsın (@Boss_Osimhen).
Konu: "{topic}"

KURALLAR:
1. Hakem hatalarına, TFF kararlarına veya rakiplerin algı operasyonlarına sert taraftar tepkisi ver.
2. "Yine başladılar oyunlara!", "Kimse Galatasaray'ın hakkını yiyemez kardeş!", "Sahada kazanamayanlar masada oyun peşinde!" gibi vurucu tepki ver.
3. Max 220 karakter.
""",
    "Tutkulu Taraftar": """
Sen sarı-kırmızı renklere aşık, coşkulu ve GS sevgisiyle dolu bir taraftarsın (@Boss_Osimhen).
Konu: "{topic}"

KURALLAR:
1. Galatasaray sevgisini, şampiyonluk inancını ve takıma olan tutkuyu en üst seviyede yaşat.
2. "Bu forma için son ana kadar mücadele!", "Şampiyonluk meşalesi yandı!", "Armanın peşinde ölümüne!" gibi hırslı yaz.
3. Max 220 karakter.
""",
    "Taktik Analiz": """
Sen Galatasaray'ın saha içi oyununu, oyuncu performanslarını ve Okan Buruk'un taktiklerini inceleyen analist bir taraftarsın (@Boss_Osimhen).
Konu: "{topic}"

KURALLAR:
1. Ön alan presi, çift forvet uyumu, kanat organizasyonları gibi futbol terimleriyle samimi analiz yaz.
2. "Saha içi alan paylaşımı mükemmel!", "Okan Hoca'nın 4-4-2 hamlesi rakip savunmayı felç etti!" gibi analizler yap.
3. Max 220 karakter.
"""
}

# Dedicated Fallback Generators per Tone
FALLBACK_GENERATORS = {
    "Organik Taraftar Ağzı (Doğal & Samimi)": [
        "Abi valla {topic} duyumunu görünce şaşırmadım. Herkes yine bilip bilmeden konuşuyor! Galatasaray sahada cevabını net verir kardeş 💛❤️ #Galatasaray",
        "Yok artık yahu! {topic} hakkında yapılan bu yorumlar tam akıl tutulması. Kimse boşuna heveslenmesin, biz şampiyonluğa kilitlendik! 🦁🔥 #GS",
        "Net söylüyorum: {topic} konusunda bizim uşaklar sahaya çıktımı kimsede laf kalmaz! Osimhen ve ekibi gereğini yapar abi! 💛❤️ #Galatasaray"
    ],
    "Le Marca Style (Profesyonel Muhabir)": [
        "🚨 {topic} hakkında Florya'dan sıcak bilgi ulaştı. Sarı-kırmızı yönetim masadaki tüm detayları inceliyor.\n\n(Nevzat Dindar)",
        "⚡ {topic} konusunda resmi temaslar başladı. Kulüp yetkilileri imzalar için görüşmeleri sürdürüyor.\n\n(GS Muhabir Bilgisi)"
    ],
    "Sert & Eleştirel": [
        "Yine başladılar algı operasyonlarına! {topic} bahanesiyle Galatasaray'ın önünü kesebileceğinizi mi sanıyorsunuz? Yemezler kardeş! 🦁🔥 #GS",
        "Kimse Galatasaray'ın hakkını yiyemez! {topic} konusunda yapılan bu haksızlıklara karşı yönetim sesini yükseltmeli net! 💛❤️ #Galatasaray"
    ],
    "Tutkulu Taraftar": [
        "Armanın peşinde tek yürek! {topic} ne olursa olsun biz bu takıma sonuna kadar güveniyoruz! Sarı kırmızı şampiyon yazdıracağız! 💛❤️ #Galatasaray",
        "Şampiyonluk ateşi yandı bir kere! {topic} bizi yolumuzdan döndüremez! Zafer yine bizim olacak 🦁🔥 #GS"
    ],
    "Taktik Analiz": [
        "Saha içi taktik disiplin harika! {topic} hamlesiyle Okan Hoca rakibin geçiş hücumlarını tamamen kilitledi. Barış Alper ve Sara kilit rol oynuyor ⚽ #GS",
        "Çift forvet presi meyvelerini veriyor. {topic} konusundaki alan paylaşımı rakip stoperleri hataya zorladı. Taktik deha! ⚽💛❤️ #Galatasaray"
    ]
}

FORMAT_SPECIFIC_ADDONS = {
    "💬 Alıntı & Tepki Tweeti": "\n\nŞu haberin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 🦁 #GS",
    "📊 X Anket Formatı": "\n\nSizce bu konuda ne yapılmalı taraftar?\nA) Tamamen Doğru 🔥\nB) Yanlış Haber ❌\nC) Kararsızım 🤔",
    "🚨 Flaş Son Dakika": "\n\n💣 FLAŞ GÜNDEM: Sıcak gelişmeler peş peşe geliyor! 💛❤️ #GS"
}

def clean_topic_str(topic: str) -> str:
    t = str(topic).strip()
    t = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^🚨 X DUYUM \| ', '', t)
    return t

def generate_tweet_content(*args, **kwargs) -> Dict[str, Any]:
    """
    Generates tweets strictly adhering to selected tone and style options.
    """
    topic = kwargs.get("topic") if "topic" in kwargs else (args[0] if len(args) > 0 else "Galatasaray Transfer Gündemi")
    category = kwargs.get("category") if "category" in kwargs else (args[1] if len(args) > 1 else "Gündem")
    tone = kwargs.get("tone") if "tone" in kwargs else (args[2] if len(args) > 2 else "Organik Taraftar Ağzı (Doğal & Samimi)")
    style = kwargs.get("style") if "style" in kwargs else (args[3] if len(args) > 3 else "Tartışma & Yorum Alıcı (Yüksek Yorum)")
    mode = kwargs.get("mode") if "mode" in kwargs else (args[4] if len(args) > 4 else "emoji")
    
    gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    content = ""
    clean_topic = clean_topic_str(topic)
    
    sys_prompt = SYSTEM_PROMPTS.get(tone, SYSTEM_PROMPTS["Organik Taraftar Ağzı (Doğal & Samimi)"])
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.9}
            )
            prompt = sys_prompt.format(topic=clean_topic, style=style)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 20:
        templates = FALLBACK_GENERATORS.get(tone, FALLBACK_GENERATORS["Organik Taraftar Ağzı (Doğal & Samimi)"])
        raw_template = random.choice(templates)
        content = raw_template.format(topic=clean_topic)
        
        # Add format-specific addon if selected
        if style in FORMAT_SPECIFIC_ADDONS and len(content) < 180:
            content += FORMAT_SPECIFIC_ADDONS[style]
            
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
