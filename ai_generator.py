import os
import random
from typing import Dict, Any
from card_generator import generate_gs_card

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

SYSTEM_PROMPT_EMOJI = """
Sen tutkulu, lafını esirgemeyen, futbolu ve Galatasaray'ı çok iyi bilen iddialı bir GALATASARAY yorumcususun (@Boss_Osimhen).
Sana verilen oyuncu ismi, transfer dedikodusu veya gündem konusu hakkında bol emojili (💛❤️, 🔥, ⚽, 🏆, 🦁, 💪, 🗣️, 💥, ❌), sert, dikkat çekici, yüksek etkileşim alacak Türkçe tweetler yazıyorsun.

Kuralların:
1. Bol miktarda sarı-kırmızı (💛❤️) ve futbol/taraftar emojisi kullan.
2. Üslup: Sert, net, objektif ama tutkulu bir Galatasaray savunucusu.
3. İstenen oyuncu veya konudan (Örn: Rafael Leao, Osimhen, Hakemler vb.) doğrudan bahset!
4. Tweet uzunluğu 240 karakteri geçmesin. Uygun hashtagler ekle (#Galatasaray #GS #SüperLig).
"""

SYSTEM_PROMPT_GRAPHIC = """
Sen Galatasaray yorumcusu @Boss_Osimhen olarak verilen oyuncu veya gündem konusu hakkında grafik kart üzerinde yayınlanacak kısa ve vurucu bir Türkçe açıklama yazıyorsun.
Metin resmi, kaliteli, sert ve net bir futbol yorumu olsun.
"""

FALLBACK_EMOJI_TWEETS = {
    "Transfer": [
        "Galatasaray yönetimi {topic} transferinde artık masaya yumruğunu vurmalı! 💛❤️ Avrupa'da başarı hedefliyorsak böyle kaliteli isimler şart! ⚽ İmzalar gecikmeden atılmalı! 🦁🔥 #Galatasaray #Transfer",
        "{topic} iddiası taraftarı heyecanlandırdı! 💛❤️ Bize sahada formanın hakkını verecek hırslı yıldızlar lazım! ⚽ Şampiyonlar Ligi kadrosu böyle kurulur! 💪🔥 #GS #Transfer"
    ],
    "Hakem Eleştirisi": [
        "{topic} konusunda açık ve net söylüyorum: Galatasaray'ın hakkı yeniyor! 💛❤️ VAR odasındakiler hangi maçı izliyor? 🦁 Bu camia bu oyunlara teslim olmaz! 💥 #Galatasaray #SüperLig",
        "{topic} hakkındaki çifte standart artık tahammül sınırını aştı! 💛❤️ Adalet istemiyoruz, eşitlik istiyoruz! ❌🔥 #Galatasaray #Cimbom"
    ],
    "Maç Analizi": [
        "{topic} maçında bu taktik anlayışıyla Şampiyonlar Ligi'nde tutunamayız! 💛❤️ Sahada ön alan baskısı ve hırs şart! Galatasaray forması pasif futbolu kaldırmaz! 🦁💥 #Galatasaray",
        "{topic} hırsla ve mücadeleyle kazanılır! 💛❤️ Sahaya karakter koyan bir Galatasaray görmek istiyoruz! ⚽🔥 #Galatasaray #SüperLig"
    ],
    "Gündem": [
        "{topic} hakkında üretilen ucuz algı operasyonlarına taraftar olarak prim vermeyeceğiz! 💛❤️ Türkiye'nin en büyüğü Galatasaray'dır! 🦁🏆 #Galatasaray #Cimbom",
        "{topic} gündeminde sarı-kırmızı formanın büyüklüğü sahadaki skordan bağımsızdır! 💛❤️ Armanın büyüklüğünün farkında olunmalı! 🔥💪 #Galatasaray"
    ]
}

def generate_tweet_content(topic: str, category: str = "Gündem", tone: str = "Sert & Eleştirel", mode: str = "emoji") -> Dict[str, Any]:
    """
    Generates tweet content for custom topics (e.g. 'Rafael Leao', 'Osimhen', etc.).
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    content = ""
    clean_topic = topic.strip() if topic else "Galatasaray Gündemi"
    
    sys_prompt = SYSTEM_PROMPT_EMOJI if mode == "emoji" else SYSTEM_PROMPT_GRAPHIC
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"{sys_prompt}\n\nKonu / Oyuncu: {clean_topic}\nKategori: {category}\nİstenen Ton: {tone}\n\nLütfen bu konuda max 240 karakterlik X (Twitter) gönderisi oluştur."
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content:
        # Fallback template generator with dynamic topic interpolation
        templates = FALLBACK_EMOJI_TWEETS.get(category, FALLBACK_EMOJI_TWEETS["Gündem"])
        raw_template = random.choice(templates)
        content = raw_template.format(topic=clean_topic)
        
    media_url = None
    media_type = "none"
    
    if mode == "graphic":
        try:
            # Generate compact 800x380 graphic card with @Boss_Osimhen
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
