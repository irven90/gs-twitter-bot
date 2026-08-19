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
Twitter (X) platformu için bol emojili (💛❤️, 🔥, ⚽, 🏆, 🦁, 💪, 🗣️, 💥, ❌), sert, dikkat çekici, yüksek etkileşim alacak Türkçe tweetler yazıyorsun.

Kuralların:
1. Bol miktarda sarı-kırmızı (💛❤️) ve futbol/taraftar emojisi kullan.
2. Üslup: Sert, net, objektif ama tutkulu bir Galatasaray savunucusu. Algı operasyonlarına ve hakem hatalarına karşı tavizsiz!
3. Tweet uzunluğu 240 karakteri geçmesin. Uygun hashtagler ekle (#Galatasaray #GS #SüperLig).
"""

SYSTEM_PROMPT_GRAPHIC = """
Sen Galatasaray yorumcusu @Boss_Osimhen olarak grafik kart üzerinde yayınlanacak kısa ve vurucu bir Türkçe açıklama yazıyorsun.
Metin resmi, kaliteli, sert ve net bir futbol eleştirisi olsun.
"""

FALLBACK_EMOJI_TWEETS = {
    "Hakem Eleştirisi": [
        "Açık ve net söylüyorum: Saha içinde Galatasaray'ın hakkı yine gasp ediliyor! 💛❤️ VAR odasındakiler hangi maçı izliyor? Bu kaçıncı doğru pozisyonda susuşunuz? 🦁 Bu camia sizin oyunlarınıza teslim olmaz! 💥 #Galatasaray #SüperLig",
        "TFF ve hakemlerin çifte standardı artık tahammül sınırını aştı! 💛❤️ Bir tarafa rahatça verilen penaltılar, GS olunca görmezden geliniyor! ❌ Adalet istemiyoruz, eşitlik istiyoruz! 🔥 #Galatasaray #Cimbom"
    ],
    "Transfer": [
        "Galatasaray yönetimi transferde artık masaya yumruğunu vurmalı! 💛❤️ Avrupa'da başarı hedefliyorsak, orta sahaya ve defansa sınıf atlatacak isimler şart! ⚽ Şampiyonlar Ligi kadrosu lafla değil hırsla kurulur! 🦁 #Galatasaray #Transfer",
        "Bize isim değil, sahada sarı-kırmızı formanın hakkını verecek yürekli oyuncular lazım! 💛❤️ Taraftar yıldız bekliyor, zaman kaybetmeden imzalar atılmalı! 💪🔥 #GS #Transfer"
    ],
    "Maç Analizi": [
        "Bu taktik anlayışıyla Şampiyonlar Ligi'nde tutunamayız! 💛❤️ Sahada ön alan baskısı yok, pas trafiği ağır. Galatasaray forması pasif futbolu kaldırmaz; hırs ve dikine oyun şart! 🦁💥 #Galatasaray",
        "Derbi maçları hırsla ve mücadeleyle kazanılır! 💛❤️ Sahaya karakter koyan bir Galatasaray görmek istiyoruz. İkinci yarıda ruhumuzu sahaya yansıtmalıyız! ⚽🔥 #Galatasaray #SüperLig"
    ],
    "Gündem": [
        "Rakiplerin ve medyanın ürettiği ucuz algı operasyonlarına taraftar olarak prim vermeyeceğiz! 💛❤️ Türkiye'nin amiral gemisi Galatasaray'dır ve kıskanılmaya devam edecek! 🦁🏆 #Galatasaray #Cimbom",
        "Sarı-kırmızı formanın büyüklüğü sahadaki skordan bağımsızdır! 💛❤️ Ama bu kulübü yönetenler de armanın büyüklüğünün farkında olmalı! 🔥💪 #Galatasaray"
    ]
}

def generate_tweet_content(topic: str, category: str = "Gündem", tone: str = "Sert & Eleştirel", mode: str = "emoji") -> Dict[str, Any]:
    """
    Generates tweet content.
    mode = 'emoji': Generates text-only tweet rich with emojis (NO image).
    mode = 'graphic': Generates text + compact graphic card with @Boss_Osimhen.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    content = ""
    
    sys_prompt = SYSTEM_PROMPT_EMOJI if mode == "emoji" else SYSTEM_PROMPT_GRAPHIC
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"{sys_prompt}\n\nKonu: {topic}\nKategori: {category}\nİstenen Ton: {tone}\n\nLütfen bu konuda max 240 karakterlik X (Twitter) gönderisi oluştur."
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content:
        # Fallback template generator
        templates = FALLBACK_EMOJI_TWEETS.get(category, FALLBACK_EMOJI_TWEETS["Gündem"])
        content = random.choice(templates)
        
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
        "title": topic[:50],
        "content": content,
        "category": category,
        "media_type": media_type,
        "media_url": media_url
    }
