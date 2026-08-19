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

# VIRAL TWEET HOOKS & STRUCTURES (X Türkiye Futbol Etkileşim Formülleri)
VIRAL_PROMPT = """
Sen X (Twitter) Türkiye'de 100 binlerce takipçisi olan, yüksek etkileşim (beğeni, rt, yorum) alan profesyonel bir GALATASARAY yorumcususun (@Boss_Osimhen).
Amacın: X Monetization (Para kazanma) algoritmasına uygun olarak YÜKSEK ETKİLEŞİM VE VİRAL TWEETLER yazmak.

Girdi Konusu / Haber: "{topic}"
Kategori: "{category}"
Söylem Tonu: "{tone}"
Format Tarzı: "{style}"

VİRAL FORMAT KURALLARI:
1. Haberle %100 doğrudan alakalı ol! Verilen haberi/oyuncuyu ("{topic}") tam odağına al. Asla alakasız genel cümleler kurma!
2. Etkileşim Yöntemleri:
   - 'Tartışma & Yorum Alıcı': Tweetin sonuna takipçilere soru sor ("Sizce ne yapılmalı?", "Katılıyor musunuz?", "Bu karar doğru mu?") -> Yorumları uçurur!
   - 'Flaş Haber': "🚨 FLAŞ |", "💣 SON DAKİKA |" veya "💥 ÖZEL |" ile başla -> Retweet ve Beğeni çeker!
   - 'Sert Eleştiri': Hakem veya rakip algılarına karşı tavizsiz, net cümleler kur.
3. Emojiler: 💛❤️, 🦁, 🚨, 💣, ⚽, 🏆, 💥, 📊 gibi dikkat çekici emojiler kullan.
4. Maksimum 230 karakter olsun. Sonuna 2-3 Türkçe hashtag ekle (#Galatasaray #GS).
5. Asla bot gibi durmasın; gerçek hırslı bir futbol yorumcusu ağzıyla yaz!
"""

# VIRAL FALLBACK GENERATOR (Gelişmiş Mantıklı Şablon Motoru)
def generate_viral_fallback(topic: str, category: str, style: str) -> str:
    clean_topic = topic.strip()
    
    if "Transfer" in category or "transfer" in clean_topic.lower():
        if "tartışma" in style.lower() or "yorum" in style.lower():
            return f"🚨 FLAŞ | {clean_topic} gündeminde sıcak gelişmeler yaşanıyor! 💛❤️ Peki taraftar ne düşünüyor? Sizce bu transfer gerçekleşmeli mi? Yorumları alalım! 🦁👇 #Galatasaray #Transfer"
        elif "flaş" in style.lower():
            return f"💣 SON DAKİKA | {clean_topic}! Masadaki pazarlıklarda son aşamaya gelindi. Bu hamle Avrupa hedefi için kilit önemde! 💛❤️ #Galatasaray #GS"
        else:
            return f"💥 {clean_topic}! Galatasaray yönetimi bu transferde masaya yumruğunu vurmalı. Sahada formanın hakkını verecek yıldızlar şart! 💛❤️ #Galatasaray"
            
    elif "Hakem" in category or "hakem" in clean_topic.lower() or "var" in clean_topic.lower():
        return f"🚨 Açık açık soruyorum: {clean_topic} konusunda gösterilen bu çifte standart daha ne kadar sürecek? 💛❤️ Galatasaray'ın hakkı göz göre göre yeniyor! Katılıyor musunuz? 🦁💥 #Galatasaray #SüperLig"
        
    elif "Maç" in category or "maç" in clean_topic.lower():
        return f"⚽ {clean_topic}! Sahada hırs, pres ve mücadele istiyoruz. Galatasaray forması pasif futbolu kaldırmaz! 💛❤️ Bu maça dair beklentiniz nedir? 🦁🔥 #Galatasaray"
        
    else:
        return f"🚨 FLAŞ | {clean_topic}! Türkiye'nin amiral gemisi Galatasaray hakkında çıkan bu haberler tesadüf değil. Sarı-kırmızı hırsın önüne geçemezsiniz! 💛❤️ #Galatasaray #Cimbom"

def generate_tweet_content(topic: str, category: str = "Gündem", tone: str = "Sert & Eleştirel", style: str = "Tartışma & Yorum Alıcı", mode: str = "emoji") -> Dict[str, Any]:
    """
    Generates high-engagement viral tweets tailored specifically to the given news/topic.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    content = ""
    clean_topic = topic.strip() if topic else "Galatasaray Transfer Gündemi"
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.85}
            )
            prompt = VIRAL_PROMPT.format(topic=clean_topic, category=category, tone=tone, style=style)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 15:
        content = generate_viral_fallback(clean_topic, category, style)
        
    media_url = None
    media_type = "none"
    
    if mode == "graphic":
        try:
            # Generate compact 800x380 graphic card (hashtags automatically stripped inside card_generator)
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
