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

SYSTEM_PROMPT_BOSS_OSIMHEN = """
Sen X (Twitter) platformunda @Boss_Osimhen kullanıcı adıyla paylaşımlar yapan tutkulu, lafını sakınmayan, stadyum ve kahvehane sohbeti doğallığında konuşan GERÇEK BİR GALATASARAY TARAFTARISIN.

Söylem Tonu: "{tone}"
Girdi Konusu / Gündem: "{topic}"
Etkileşim Formatı: "{style}"

KURALLAR (BOT HİSSİNİ SIFIRLAMAK VE İNSAN PERSONASI OLUŞTURMAK İÇİN):
1. ASLA HABER BAŞLIĞINI VEYA MUHABİR TWEETİNİ BİREBİR KOPYALAMA!
2. Haber başlığı veya oyuncu adı hakkında kahvede arkadaştan dinlemiş gibi kendi samimi, tutkulu taraftar yorumunu yaz.
3. Kullanacağın İnsan İfadeleri:
   - "Abi valla bakıyorum da...", "Yok artık yahu!", "Net söylüyorum Osimhen bu takıma sınıf atlattı!", "Şu pozisyona penaltı demeyen voleybol izlesin abi net!", "Yine başladılar algı yapmaya kardeş..."
4. Eğer 'Organik Taraftar Ağzı' seçildiyse: Tam bir Galatasaray fanatiği gibi yaz. Gerekirse hakem kararlarına ve rakiplere tatlı-sert taraftar tepkisi ver, GS yıldızlarını göklere çıkar.
5. Eğer '💬 Alıntı & Tepki' seçildiyse: Habere verilen 1-2 cümlelik şok verici samimi insan tepkisi yaz.
6. Eğer '📊 X Anket Formatı' seçildiyse: Takipçilere soru sor ve altına A), B), C), D) şıklarını koy!
7. Karakter sınırı: Max 240 karakter. Sonuna 1-2 doğal taraftar hashtag'i koy (#Galatasaray #GS).
8. Emojiler: Tam bir insanın attığı gibi 1-3 adet doğal koy (💛❤️, 🦁, 🚨, 💣, ⚽).
"""

SYSTEM_PROMPT_LE_MARCA = """
Sen X'te 'Le Marca Sports' ve Fabrizio Romano tarzında haberler veren profesyonel bir spor yorumcususun.
Verilen konu ({topic}) hakkında 2 cümlelik vurucu, net futbol haber cümlesi yaz.
En alt satırda parantez içinde kaynak belirt (örneğin: (Nevzat Dindar), (Yağız Sabuncuoğlu) veya (GS Muhabir Bilgisi)).
"""

HUMAN_PERSONA_FALLBACKS = {
    "Organik Taraftar Ağzı (Doğal & Samimi)": [
        "Abi valla duyumları görünce şaşırmadım. {topic} konusunda yine herkes uzman kesilmiş! Şu olayın netliğini göremeyen gitsin başka spor izlesin net! 💛❤️ #Galatasaray",
        "Yok artık yahu! {topic} hakkında yapılan şu haberler tam bir akıl tutulması. Galatasaray taraftarı bu masalları yemez kardeş! 🦁🔥 #GS",
        "Net söylüyorum: {topic} konusunda yönetim masaya yumruğunu vurmalı! Bize laf değil icraat lazım abi, Osimhen ve ekibi sahada gereğini yapar! 💛❤️ #Galatasaray",
        "Şu gündeme bak yahu... {topic} konuşuluyor ama kimse Galatasaray'ın sahadaki gücünden bahsetmiyor! Biz şampiyonluğa odaklandık kardeş! 🦁💛❤️ #GS",
        "Vallahi billahi pes! {topic} hakkında ne desek az. Bu takım her engeli aşar, kimse boşuna algı yapmasın! 💛❤️ #Galatasaray"
    ],
    "💬 Alıntı & Tepki Tweeti": [
        "Şu haberin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 💛❤️ #Galatasaray",
        "Hahaha yahu şaka gibi açıklama! Güneş balçıkla sıvanmaz kardeş, Galatasaray'ın büyüklüğü ortada! 🦁🔥 #GS",
        "İşte duymak istediğimiz haber tam olarak bu! Bravo yönetim! 💛❤️ #Galatasaray",
        "Yok valla bu kadarını da beklemiyordum. Galatasaray'a karşı yapılan bu haberler tamamen hikaye! 🦁 #GS"
    ],
    "📊 X Anket Formatı": [
        "Sizce {topic} konusunda ne yapılmalı taraftar?\n\nA) Hemen Bitirilmeli 🔥\nB) Alternatif Bakılmalı ⚽\nC) Beklenmeli 🦁\n\nYorumlarda buluşalım! 💛❤️ #Galatasaray",
        "{topic} haberi hakkında ne düşünüyorsunuz sarı-kırmızılılar?\n\nA) Tamamen Doğru ✅\nB) Yanlış Haber ❌\nC) Kararsızım 🤔\n\n#Galatasaray #GS"
    ],
    "Le Marca Style (Profesyonel Muhabir)": [
        "🚨 {topic} hakkında Florya'dan sıcak bilgi ulaştı. Yönetim masadaki tüm opsiyonları değerlendiriyor.\n\n(GS Muhabir Bilgisi)",
        "⚡ {topic} konusunda kulüp yetkilileri temasları sıklaştırdı. Resmi açıklamanın yakında yapılması bekleniyor.\n\n(Nevzat Dindar)",
        "💣 {topic} için teknik heyet ve transfer komitesi ortak karar aldı. Şartlar zorlanacak.\n\n(X Transfer Duyumu)"
    ]
}

def extract_or_infer_reporter(topic: str) -> str:
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
    else:
        return "GS Muhabir Bilgisi"

def generate_tweet_content(*args, **kwargs) -> Dict[str, Any]:
    """
    Generates rich, authentic human fan tweets matching @Boss_Osimhen persona or Le Marca style.
    """
    topic = kwargs.get("topic") if "topic" in kwargs else (args[0] if len(args) > 0 else "Galatasaray Transfer Gündemi")
    category = kwargs.get("category") if "category" in kwargs else (args[1] if len(args) > 1 else "Gündem")
    tone = kwargs.get("tone") if "tone" in kwargs else (args[2] if len(args) > 2 else "Organik Taraftar Ağzı (Doğal & Samimi)")
    style = kwargs.get("style") if "style" in kwargs else (args[3] if len(args) > 3 else "Tartışma & Yorum Alıcı (Yüksek Yorum)")
    mode = kwargs.get("mode") if "mode" in kwargs else (args[4] if len(args) > 4 else "emoji")
    
    gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    content = ""
    clean_topic = str(topic).strip() if topic else "Galatasaray Transfer Gündemi"
    clean_topic = re.sub(r'(\s*-\s*|\s*\|\s*)(Fotomaç|Sözcü|Haber\s*7|Milliyet|Mynet|A\s*Spor|Fanatik|Hürriyet|TRT\s*Spor|Sabah|NTV\s*Spor).*$', '', clean_topic, flags=re.IGNORECASE)
    clean_topic = re.sub(r'^🚨 X DUYUM \| ', '', clean_topic)
    
    sys_prompt = SYSTEM_PROMPT_LE_MARCA if tone == "Le Marca Style (Profesyonel Muhabir)" else SYSTEM_PROMPT_BOSS_OSIMHEN
    
    if GEMINI_AVAILABLE and gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={"temperature": 0.9}
            )
            prompt = sys_prompt.format(topic=clean_topic, tone=tone, style=style)
            response = model.generate_content(prompt)
            content = response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            content = ""
            
    if not content or len(content) < 20:
        templates = HUMAN_PERSONA_FALLBACKS.get(tone, HUMAN_PERSONA_FALLBACKS.get(style, HUMAN_PERSONA_FALLBACKS["Organik Taraftar Ağzı (Doğal & Samimi)"]))
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
