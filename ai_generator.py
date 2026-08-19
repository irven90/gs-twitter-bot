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

SYSTEM_PROMPT_HUMAN_EMOJI = """
Sen X (Twitter) Türkiye'de takılan, futbol duyumlarını, transferleri ve Galatasaray'ı tutkuyla takip eden GERÇEK BİR İNSAN VE GS TARAFTARISIN (@Boss_Osimhen).
ASLA BOT GİBİ VEYA RESMİ GAZETE GİBİ YAZMA! X muhabirlerinin ve duyumcuların tarzında, arkadaşlarınla futbol konuşurken kullandığın doğal, samimi, vurucu dili kullan.

Söylem Tonu: "{tone}"
Girdi Konusu / Duyum: "{topic}"
Etkileşim Formatı: "{style}"

KURALLAR (BOT HİSSİNİ YOK ETMEK İÇİN):
1. Doğal Günlük Konuşma Dili Kullan: "Abi valla duyumları görünce şaşırmadım...", "Yok artık yahu!", "Şu pozisyona net penaltı demeyen gitsin voleybol izlesin net!", "Osimhen bu lige çok fazla abi..." gibi samimi kalıplar kullanabilirsin.
2. Eğer 'Organik Taraftar Ağzı' seçildiyse; resmiyetten tamamen uzaklaş, stadyum sohbeti sıcaklığında yaz.
3. Eğer '💬 Alıntı & Tepki' formatı seçildiyse; duyuma verilen 1-2 cümlelik kısa, şok verici ve çok doğal bir insan tepkisi yaz.
4. Eğer '📊 X Anket Formatı' seçildiyse; haber hakkında takipçilere 1 soru sor ve altına A), B), C), D) şıklarını ekle!
5. Karakter sınırı: Max 240 karakter. Sonuna 1-2 doğal hashtag ekle (#Galatasaray #GS).
6. Emojileri tam bir insanın attığı gibi 1-3 adet doğal koy (💛❤️, 🦁, 🚨, 💣, ⚽).
"""

SYSTEM_PROMPT_GRAPHIC = """
Sen Galatasaray yorumcusu @Boss_Osimhen olarak verilen duyum veya gündem konusu ({topic}) hakkında grafik kart üzerinde yayınlanacak kısa ve vurucu bir Türkçe yorum yazıyorsun.
Metin resmi, kaliteli, hırslı ve net bir futbol yorumu olsun.
İstenen ton: {tone}.
"""

HUMAN_FALLBACKS = {
    "Organik Taraftar Ağzı (Doğal & Samimi)": [
        "Abi valla duyumları görünce şaşırmadım. {topic} konusunda yine herkes uzman kesilmiş. Şu olayın netliğini göremeyen gitsin başka spor izlesin net! 💛❤️ #Galatasaray",
        "Yok artık yahu! {topic} hakkında yapılan bu yorumlar tam akıl tutulması. Galatasaray taraftarı bu masalları yemez kardeş! 🦁🔥 #GS",
        "Net söylüyorum: {topic} konusunda yönetim masaya yumruğunu vurmazsa bu iş uzar. Bize laf değil icraat lazım abi! 💛❤️ #Galatasaray"
    ],
    "💬 Alıntı & Tepki Tweeti": [
        "Şu haberin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 💛❤️ #Galatasaray",
        "Hahaha yahu şaka gibi açıklama! Güneş balçıkla sıvanmaz kardeş, Galatasaray'ın büyüklüğü ortada! 🦁🔥 #GS",
        "İşte duymak istediğimiz duyum haber tam olarak bu! Bravo! 💛❤️ #Galatasaray"
    ],
    "📊 X Anket Formatı": [
        "Sizce {topic} konusunda ne yapılmalı?\n\nA) Hemen Bitirilmeli 🔥\nB) Alternatif Bakılmalı ⚽\nC) Beklenmeli 🦁\n\nYorumlarda buluşalım! 💛❤️ #Galatasaray",
        "{topic} haberi hakkında ne düşünüyorsunuz taraftar?\n\nA) Tamamen Doğru ✅\nB) Yanlış Haber ❌\nC) Kararsızım 🤔\n\n#Galatasaray #GS"
    ]
}

def generate_tweet_content(
    topic: str = "Galatasaray Transfer Gündemi",
    category: str = "Gündem",
    tone: str = "Organik Taraftar Ağzı (Doğal & Samimi)",
    style: str = "Tartışma & Yorum Alıcı (Yüksek Yorum)",
    mode: str = "emoji",
    *args,
    **kwargs
) -> Dict[str, Any]:
    """
    Bulletproof tweet content generator accepting positional OR keyword arguments safely.
    """
    # Overwrite if passed in kwargs or args
    if "topic" in kwargs: topic = kwargs["topic"]
    elif len(args) > 0: topic = args[0]
    
    if "category" in kwargs: category = kwargs["category"]
    elif len(args) > 1: category = args[1]
    
    if "tone" in kwargs: tone = kwargs["tone"]
    elif len(args) > 2: tone = args[2]
    
    if "style" in kwargs: style = kwargs["style"]
    elif len(args) > 3: style = args[3]
    
    if "mode" in kwargs: mode = kwargs["mode"]
    elif len(args) > 4: mode = args[4]
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    content = ""
    clean_topic = str(topic).strip() if topic else "Galatasaray Transfer Gündemi"
    
    sys_prompt = SYSTEM_PROMPT_HUMAN_EMOJI if mode == "emoji" else SYSTEM_PROMPT_GRAPHIC
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.92}
            )
            prompt = sys_prompt.format(topic=clean_topic, tone=tone, style=style)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 15:
        templates = HUMAN_FALLBACKS.get(tone, HUMAN_FALLBACKS.get(style, HUMAN_FALLBACKS["Organik Taraftar Ağzı (Doğal & Samimi)"]))
        raw_template = random.choice(templates)
        content = raw_template.format(topic=clean_topic)
        
    media_url = None
    media_type = "none"
    
    if mode == "graphic":
        try:
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
