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

def get_active_gemini_key() -> str:
    """Retrieves Gemini API key from os.environ or Streamlit secrets safely."""
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if "GEMINI_API_KEY" in st.secrets:
                    key = str(st.secrets["GEMINI_API_KEY"]).strip()
                elif "gemini_api_key" in st.secrets:
                    key = str(st.secrets["gemini_api_key"]).strip()
        except Exception:
            pass
    return key

PERSONA_PROMPTS = {
    "Organik Taraftar Ağzı (@Boss_Osimhen)": """
Sen X (Twitter) platformunda @Boss_Osimhen adıyla bilinen tutkulu, lafını sakınmayan, stadyum ve kahvehane sohbeti doğallığında konuşan GERÇEK BİR GALATASARAY TARAFTARISIN.
Gündem / Konu: "{topic}"

KURALLAR:
1. Konuyu bir Galatasaray taraftarı olarak samimi, vurucu kelimelerle yorumla.
2. "Osimhen bu lige sınıf atlattı net!", "Yine başladılar hakem kararlarını tartışmaya!", "Biz şampiyonluğa kilitlendik kardeş!" gibi samimi ifadeler kullan.
3. Sonuna 1-2 doğal taraftar hashtag'i koy (#Galatasaray #GS).
4. Karakter sınırı: Max 220 karakter.
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
    "Sert & Eleştirel": """
Sen Galatasaray haklarını savunan, rakiplere ve hakem hatalarına karşı tavizsiz, sert ve eleştirel bir taraftarsın (@Boss_Osimhen).
Gündem / Konu: "{topic}"

KURALLAR:
1. Hakem kararlarına ve rakiplerin algı operasyonlarına sert taraftar tepkisi ver.
2. "Sahada kazanamayanlar masada oyun peşinde ama bu taraftar yemez kardeş!", "Kimse Galatasaray'ın hakkını yiyemez!" gibi vurucu tepki ver.
3. #Galatasaray #GS
""",
    "Tutkulu Taraftar": """
Sen sarı-kırmızı renklere aşık, coşkulu ve GS sevgisiyle dolu bir taraftarsın (@Boss_Osimhen).
Gündem / Konu: "{topic}"

KURALLAR:
1. Sarı-kırmızı tutkuyu, şampiyonluk coşkusunu ve arma sevgisini anlatan hırslı 2 cümlelik tweet yaz.
2. 💛❤️ #Galatasaray #GS
""",
    "Taktik Analiz": """
Sen Okan Buruk'un taktiklerini ve oyuncu performanslarını değerlendiren analist bir taraftarsın (@Boss_Osimhen).
Gündem / Konu: "{topic}"

KURALLAR:
1. Ön alan presi, çift forvet uyumu gibi detaylarla 2 cümlelik samimi analiz tweeti yaz.
2. ⚽ #GS #Galatasaray
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

# Distinct Procedural Generators Per Mode (No duplicate phrases!)
MODE_FALLBACKS = {
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
    ],
    "Le Marca Style (Haber & Kaynak)": [
        "🚨 {topic} hakkında Florya'dan sıcak bilgi ulaştı. Sarı-kırmızı yönetim masadaki tüm detayları inceliyor.\n\n(Nevzat Dindar)",
        "⚡ {topic} konusunda resmi temaslar başladı. Kulüp yetkilileri imzalar için görüşmeleri sürdürüyor.\n\n(GS Muhabir Bilgisi)"
    ],
    "📊 X Anket Formatı": [
        "Sizce {topic} konusunda yönetim nasıl bir adım atmalı taraftar?\n\nA) Anlaşma Sağlanmalı 🔥\nB) Alternatif İsim Bakılmalı ⚽\nC) Beklenmeli 🦁\nD) İptal Edilmeli ❌\n\n#Galatasaray #GS",
        "{topic} gelişmesi hakkında fikriniz nedir sarı-kırmızılılar?\n\nA) Çok Doğru Karar ✅\nB) Hatalı Adım ❌\nC) Kararsızım 🤔\n\n#Galatasaray #GS"
    ],
    "💬 Alıntı & Tepki Tweeti": [
        "Şu haberin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 🦁 #GS #Galatasaray",
        "Hahaha yahu şaka gibi açıklama! Güneş balçıkla sıvanmaz kardeş, Galatasaray'ın büyüklüğü ortada! 💛❤️ #Galatasaray"
    ],
    "🚨 Flaş Son Dakika": [
        "💣 FLAŞ GÜNDEM: {topic} konusunda sıcak saatler yaşanıyor! Detaylar ve gelişmeler yolda. 💛❤️ #Galatasaray",
        "🚨 SON DAKİKA: {topic} hakkında sarı-kırmızılı cepheden ilk hamle geldi! 🦁🔥 #GS"
    ],
    "Organik Taraftar Ağzı (@Boss_Osimhen)": [
        "Osimhen ve ekibi sahaya çıktı mı rakiplerin stoper hattı tamamen çöküyor abi! {topic} hakkında konuşanlar sahadaki gücü görsün 💛❤️ #Galatasaray #GS",
        "Net söylüyorum: {topic} konusunda Okan Hoca ve yönetim gerekeni yapacaktır. Biz şampiyonluğa kilitlendik kardeş! 💛❤️ #GS",
        "Şu pozisyonları ve kararları gördükçe çıldırmamak elde değil! {topic} konusunda adalet şart abi net! 🦁 #Galatasaray"
    ]
}

def clean_topic_str(topic: str) -> str:
    t = str(topic).strip()
    t = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor|Futbol|Spor\s*Haberleri).*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^🚨 X DUYUM \| ', '', t)
    return t.strip()

def generate_tweet_content(*args, **kwargs) -> Dict[str, Any]:
    """
    Generates rich, authentic human fan tweets matching @Boss_Osimhen persona or Le Marca style.
    """
    topic = kwargs.get("topic") if "topic" in kwargs else (args[0] if len(args) > 0 else "Galatasaray Transfer Gündemi")
    category = kwargs.get("category") if "category" in kwargs else (args[1] if len(args) > 1 else "Gündem")
    tone = kwargs.get("tone") if "tone" in kwargs else (args[2] if len(args) > 2 else "Organik Taraftar Ağzı (@Boss_Osimhen)")
    style = kwargs.get("style") if "style" in kwargs else (args[3] if len(args) > 3 else "Tartışma & Yorum Alıcı")
    mode = kwargs.get("mode") if "mode" in kwargs else (args[4] if len(args) > 4 else "emoji")
    
    clean_topic = clean_topic_str(topic)
    gemini_key = get_active_gemini_key()
    content = ""
    
    # Pick prompt matching tone or style
    raw_prompt_template = PERSONA_PROMPTS.get(tone, PERSONA_PROMPTS.get(style, PERSONA_PROMPTS["Organik Taraftar Ağzı (@Boss_Osimhen)"]))
    
    if GEMINI_AVAILABLE and gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.95}
            )
            # Safe replacement instead of .format() to avoid KeyError on braces
            prompt = raw_prompt_template.replace("{topic}", clean_topic)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Execution Error: {e}")
            content = ""
            
    # Varied procedural fallback if Gemini API is missing or fails
    if not content or len(content) < 20:
        fallback_list = MODE_FALLBACKS.get(tone, MODE_FALLBACKS.get(style, MODE_FALLBACKS["Organik Taraftar Ağzı (@Boss_Osimhen)"]))
        template = random.choice(fallback_list)
        content = template.replace("{topic}", clean_topic)
        
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
