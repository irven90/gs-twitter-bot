import os
import random
from typing import Dict, Any
from card_generator import generate_gs_card

# Attempt to load Gemini / OpenAI if available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

SYSTEM_PROMPT = """
Sen tutkulu, lafını esirgemeyen, futbolu çok iyi bilen ve sert eleştiriler yapabilen fanatik bir GALATASARAY taraftarı ve yorumcususun.
Twitter (X) platformunda içerik üretiyorsun.

Kuralların:
1. Tonun: Sert, net, objektif ama tutkulu bir Galatasaray savunucusu. Rakiplerin algı operasyonlarına, hakem hatalarına ve takımdaki kötü futbol anlayışına asla müsamaha göstermezsin.
2. Üslup: "Açık ve net!", "Lafı dolandırmaya gerek yok!", "Galatasaray bu ülkenin amiral gemisidir!" gibi vurgulu, iddialı ifadeler kullanırsın.
3. Uygun hashtag'ler kullan (Örn: #Galatasaray #GS #SüperLig).
4. Asla hakaret ve küfür etme, ancak eleştirini en sivri dille yap.
"""

# Fallback smart templates for test/offline mode
FALLBACK_TEMPLATES = {
    "Hakem Eleştirisi": [
        "Açık ve net söylüyorum: Saha içinde Galatasaray'ın hakkı yine gasp ediliyor! VAR odasındakiler hangi maçı izliyor? Bu kaçıncı doğru pozisyonda susuşunuz? Galatasaray camiası bu oyunlara teslim olmaz! 💛❤️ #Galatasaray #SüperLig",
        "TFF ve MKYK hakemlerinin çifte standardı artık tahammül sınırını aştı! Bir tarafa rahatça verilen penaltılar, GS olunca görmezden geliniyor. Adalet istemiyoruz, eşitlik istiyoruz! #Galatasaray",
    ],
    "Transfer": [
        "Galatasaray yönetimi transferde artık masaya yumruğunu vurmalı! Avrupa'da başarı hedefliyorsak, orta sahaya ve defansa sınıf atlatacak oyuncular şart. Şampiyonlar Ligi kadrosu lafla değil, kaliteli hamleyle kurulur! 💛❤️ #Galatasaray #Transfer",
        "Bize isim değil, sahada formanın hakkını verecek hırslı oyuncular lazım! Taraftar yıldız isim bekliyor ama öncelik sistem oyuncusu. Zaman kaybetmeden imzalar atılmalı! #GS",
    ],
    "Maç Analizi": [
        "Bu taktik anlayışıyla Şampiyonlar Ligi'nde tutunamayız! Sahada ön alan baskısı yok, pas trafiği ağır. Galatasaray forması pasif futbolu kaldırmaz; hırs, pres ve dikine oyun şart! 💛❤️ #Galatasaray",
        "Derbi maçları mücadeleyle kazanılır, isimlerle değil. Sahaya karakter koyan bir Galatasaray görmek istiyoruz. İkinci yarıda hırsımızı sahaya yansıtmazsak bedelini ağır öderiz! #Galatasaray #SüperLig",
    ],
    "Gündem": [
        "Rakiplerin ve medyanın ürettiği algı operasyonlarına taraftar olarak prim vermeyeceğiz. Türkiye'nin en başarılı kulübü Galatasaray'dır ve başarılarımız kıskanılmaya devam edecek! 💛❤️ #Galatasaray #Cimbom",
        "Sarı-kırmızı formanın büyüklüğü sahadaki skordan bağımsızdır. Ama bu kulübü yönetenler de bu hırsın ve armanın büyüklüğünün farkında olmalı! #Galatasaray",
    ]
}

def generate_tweet_content(topic: str, category: str = "Gündem", tone: str = "Sert & Eleştirel", include_card: bool = True) -> Dict[str, Any]:
    """
    Generates tweet content and optionally creates a Galatasaray graphic card.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    content = ""
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"{SYSTEM_PROMPT}\n\nKonu: {topic}\nKategori: {category}\nİstenen Ton: {tone}\n\nLütfen bu konuda max 260 karakterlik sert, dikkat çekici ve etkileşim alacak bir X (Twitter) gönderisi yaz."
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}, falling back to template engine.")
            content = ""
            
    if not content:
        # Fallback template generation
        templates = FALLBACK_TEMPLATES.get(category, FALLBACK_TEMPLATES["Gündem"])
        base_text = random.choice(templates)
        content = f"{topic}: {base_text}" if len(topic) < 40 else base_text
        
    media_url = None
    media_type = "none"
    
    if include_card:
        # Generate GS graphic card image
        try:
            media_url = generate_gs_card(
                text=content[:220],
                category=category.upper(),
                title="TARAFTAR SÖZLÜĞÜ"
            )
            media_type = "image"
        except Exception as e:
            print(f"Error generating card: {e}")
            media_url = None
            media_type = "none"
            
    return {
        "title": topic[:50],
        "content": content,
        "category": category,
        "media_type": media_type,
        "media_url": media_url
    }
