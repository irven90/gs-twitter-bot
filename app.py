import streamlit as st
import os
import re
from PIL import Image
import database as db
import news_fetcher
from ai_generator import generate_tweet_content
from twitter_client import publish_tweet
from card_generator import generate_gs_card

# Inline Purger Function to 100% prevent AttributeError on Streamlit Cloud
NEWSPAPER_WORDS = [
    r'Fotomaç', r'Sözcü.*', r'Haber\s*7', r'Milliyet', r'Mynet', r'A\s*Spor',
    r'Fanatik', r'Hürriyet', r'TRT\s*Spor', r'Sabah', r'NTV\s*Spor', r'Gazetesi'
]

def purge_newspaper_names(text: str) -> str:
    """Rigorous inline sanitizer stripping ALL newspaper names and Google News prefixes."""
    t = str(text)
    t = re.sub(r'^Google News.*?:', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^\s*\(.*?\):\s*', '', t)
    for word in NEWSPAPER_WORDS:
        t = re.sub(r'(\s*-\s*|\s*\|\s*|\s+)' + word + r'.*$', '', t, flags=re.IGNORECASE)
        t = re.sub(r'\b' + word + r'\b', '', t, flags=re.IGNORECASE)
    return t.strip()

# Sync Streamlit Secrets to os.environ so Gemini & X API work 100% on Streamlit Cloud!
try:
    if hasattr(st, "secrets"):
        for key, val in st.secrets.items():
            os.environ[key] = str(val)
except Exception:
    pass

# Page Config
st.set_page_config(
    page_title="Galatasaray X İçerik Botu & Onay Paneli",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PIN Güvenlik Kontrolü
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h2 style='text-align: center; color: #FDB913;'>🔒 Galatasaray X Botu - Güvenli Giriş</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A90429;'>Evden veya mobilden güvenli erişim için PIN kodunuzu giriniz.</p>", unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns([1, 1, 1])
    with col_p2:
        pin_input = st.text_input("Giriş Kodu:", type="password")
        if st.button("🔓 Giriş Yap", use_container_width=True):
            target_pin = os.getenv("APP_PIN", "1905")
            if pin_input == target_pin:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı PIN Kodu!")
    st.stop()

# Safe Wrapper to 100% prevent any Streamlit red error traceback box
def safe_generate_tweet(topic, category="Gündem", tone="Le Marca Style", style="Haber Formatı", mode="emoji"):
    clean_t = purge_newspaper_names(topic)
    try:
        return generate_tweet_content(topic=clean_t, category=category, tone=tone, style=style, mode=mode)
    except Exception:
        try:
            return generate_tweet_content(clean_t, category, tone, style, mode)
        except Exception:
            return {
                "title": clean_t[:50],
                "content": f"🚨 {clean_t}.\n\n(Nevzat Dindar)",
                "category": category,
                "media_type": "none",
                "media_url": None
            }

# Custom Styling (Galatasaray Red & Gold Yellow theme)
st.markdown("""
    <style>
    .main {
        background-color: #0f1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #A90429;
        color: #FDB913;
        font-weight: bold;
        border-radius: 8px;
        border: 1px solid #FDB913;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #FDB913;
        color: #A90429;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Database
db.init_db()

# Fetch latest news upfront and purge all newspaper names completely
raw_news_items = news_fetcher.fetch_latest_football_news()
news_items = []
for item in raw_news_items:
    clean_t = purge_newspaper_names(item['title'])
    clean_s = purge_newspaper_names(item['summary'])
    news_items.append({
        "title": clean_t,
        "summary": clean_s,
        "source": item['source']
    })

default_latest_topic = news_items[0]['title'] if news_items else "🚨 Mauro Icardi transfer gündemi hakkında sıcak gelişme"

# Initialize Session State Topic Box dynamically from latest clean news
if 'topic_box' not in st.session_state or not st.session_state['topic_box']:
    st.session_state['topic_box'] = default_latest_topic
else:
    st.session_state['topic_box'] = purge_newspaper_names(st.session_state['topic_box'])

# Sidebar Setup
st.sidebar.title("💛❤️ GS Twitter Bot")
st.sidebar.markdown("**@Boss_Osimhen Le Marca Style Otomasyonu**")
st.sidebar.caption("🎯 Le Marca & Fabrizio Romano Formatında Tweetler")
st.sidebar.divider()

# Stats Widgets
stats = db.get_stats()
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric("Bekleyen Taslak", stats.get('draft', 0))
col_s2.metric("Yayınlanan", stats.get('published', 0))

st.sidebar.divider()

# API Keys Configuration in Sidebar
st.sidebar.subheader("🔑 API Yapılandırması")
gemini_key = st.sidebar.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key

x_api_key = st.sidebar.text_input("X (Twitter) API Key", value=os.getenv("X_API_KEY", ""), type="password")
if x_api_key:
    os.environ["X_API_KEY"] = x_api_key

mock_mode = not bool(os.getenv("X_API_KEY"))
if mock_mode:
    st.sidebar.info("ℹ️ **Simülasyon Modu Aktif**: Paylaşımlar gerçek X hesabına gönderilmez, test modunda simüle edilir.")

# Header
st.title("⚽ Galatasaray X Le Marca Style İçerik Botu")
st.caption("Le Marca Sports ve Fabrizio Romano formatında profesyonel futbol duyumları ve tweetler üretin!")

# Navigation Tabs
tab_create, tab_drafts, tab_history, tab_monetize = st.tabs([
    "🚀 İçerik Üret", 
    "📝 Taslak & Onay Paneli", 
    "📊 Yayınlanan Geçmiş", 
    "💰 X Para Kazanma Taktikleri"
])

# Callback function for news buttons to force update topic box & tweet generation
def trigger_news_tweet(topic_title):
    clean_title = purge_newspaper_names(topic_title)
    st.session_state['topic_box'] = clean_title
    generated = safe_generate_tweet(
        topic=clean_title,
        category="Transfer",
        tone="Le Marca Style",
        style="Haber Formatı",
        mode="emoji"
    )
    st.session_state['last_generated'] = generated

# ---------------------------------------------------------
# TAB 1: İÇERİK ÜRETİMİ
# ---------------------------------------------------------
with tab_create:
    col_news, col_gen = st.columns([1, 1])
    
    with col_news:
        st.subheader("🚨 Le Marca Style X Duyum Akışı")
        st.caption("Aşağıdaki sıcak futbol duyumlarına tıklayarak anında Le Marca tarzı tweet üretebilirsiniz.")
        
        if st.button("🔄 Gündemi Yenile"):
            st.rerun()
            
        for idx, item in enumerate(news_items):
            with st.expander(f"📌 {item['source']}: {item['title']}"):
                st.write(item['summary'])
                st.button(
                    f"⚡ Bu Konudan Anında Tweet Üret", 
                    key=f"news_btn_{idx}",
                    on_click=trigger_news_tweet,
                    args=(item['title'],)
                )
                    
    with col_gen:
        st.subheader("✏️ Le Marca Style Tweet Üretici")
        
        topic_input = st.text_area("İçerik Konusu / Oyuncu İsmi / Duyum Başlığı:", key="topic_box", height=90)
        
        c1, c2, c3 = st.columns(3)
        category_input = c1.selectbox("Kategori:", ["Transfer", "Hakem Eleştirisi", "Maç Analizi", "Gündem", "Genel"])
        tone_input = c2.selectbox("Söylem Tonu:", [
            "Le Marca Style (Profesyonel Muhabir)", 
            "Organik Taraftar Ağzı (Doğal & Samimi)", 
            "Sert & Eleştirel", 
            "Tutkulu Taraftar", 
            "Taktik Analiz"
        ])
        style_input = c3.selectbox("Etkileşim Formatı:", [
            "Haber & Kaynak Formatı (Le Marca)", 
            "Tartışma & Yorum Alıcı", 
            "💬 Alıntı & Tepki Tweeti",
            "📊 X Anket Formatı",
            "🚨 Flaş Son Dakika"
        ])
        
        st.markdown("### 🎯 İçerik Formatı Seçin:")
        btn_c1, btn_c2 = st.columns(2)
        
        if btn_c1.button("🔥 Emojili Metin Tweeti Üret (Görselsiz)", use_container_width=True):
            if not topic_input.strip():
                st.warning("Lütfen bir konu veya oyuncu ismi girin.")
            else:
                with st.spinner(f"'{topic_input}' hakkında tweet üretiliyor..."):
                    generated = safe_generate_tweet(
                        topic=topic_input,
                        category=category_input,
                        tone=tone_input,
                        style=style_input,
                        mode="emoji"
                    )
                    st.session_state['last_generated'] = generated
                    st.rerun()

        if btn_c2.button("🎨 Görselli Grafik Tweeti Üret", use_container_width=True):
            if not topic_input.strip():
                st.warning("Lütfen bir konu veya oyuncu ismi girin.")
            else:
                with st.spinner(f"'{topic_input}' hakkında görselli tweet üretiliyor..."):
                    generated = safe_generate_tweet(
                        topic=topic_input,
                        category=category_input,
                        tone=tone_input,
                        style=style_input,
                        mode="graphic"
                    )
                    st.session_state['last_generated'] = generated
                    st.rerun()
                    
        if 'last_generated' in st.session_state:
            gen_data = st.session_state['last_generated']
            st.success(f"'{gen_data['title']}' Konusunda Le Marca Style Tweet Üretildi!")
            
            st.markdown("### 📱 Tweet Önizleme")
            st.text_area("Üretilen Metin:", value=gen_data['content'], height=120, key="preview_text")
            
            if gen_data.get('media_url') and os.path.exists(gen_data['media_url']):
                st.image(gen_data['media_url'], caption="Kompakt GS Grafik Kartı (@Boss_Osimhen)", width=500)
                
            b1, b2 = st.columns(2)
            if b1.button("💾 Taslaklara Kaydet"):
                draft_id = db.create_draft(
                    title=gen_data['title'],
                    content=gen_data['content'],
                    category=gen_data['category'],
                    media_type=gen_data['media_type'],
                    media_url=gen_data['media_url']
                )
                st.success(f"Taslak kaydedildi! (ID: #{draft_id})")
                del st.session_state['last_generated']
                st.rerun()
                
            if b2.button("🚀 Anında Paylaş"):
                success, tweet_res = publish_tweet(gen_data['content'], gen_data.get('media_url'))
                if success:
                    db.create_draft(
                        title=gen_data['title'],
                        content=gen_data['content'],
                        category=gen_data['category'],
                        media_type=gen_data['media_type'],
                        media_url=gen_data['media_url']
                    )
                    st.balloons()
                    st.success(f"Paylaşıldı! (İşlem Kodu: {tweet_res})")
                    del st.session_state['last_generated']
                    st.rerun()
                else:
                    st.error(f"Paylaşım Hatası: {tweet_res}")

# ---------------------------------------------------------
# TAB 2: TASLAK VE ONAY PANELİ
# ---------------------------------------------------------
with tab_drafts:
    st.subheader("📋 Bekleyen Taslaklar ve Onay Listesi")
    st.caption("Burada biriken taslakları inceleyebilir, metnini düzenleyebilir ve X hesabınızda yayınlayabilirsiniz.")
    
    drafts = db.get_drafts(status='draft')
    
    if not drafts:
        st.info("Şu anda onay bekleyen taslak bulunmuyor. 'İçerik Üret' sekmesinden yeni taslaklar oluşturabilirsiniz.")
    else:
        for draft in drafts:
            with st.container():
                st.markdown(f"#### 🟡 Taslak #{draft['id']} - {draft['category']} ({draft['title']})")
                
                col_d_img, col_d_content = st.columns([1, 2])
                
                with col_d_img:
                    if draft['media_url'] and os.path.exists(draft['media_url']):
                        st.image(draft['media_url'], width=380)
                    else:
                        st.write("📝 *Sadece Metin Tweeti (Görselsiz)*")
                        
                with col_d_content:
                    edited_content = st.text_area(
                        "Tweet Metni (Düzenlenebilir):", 
                        value=draft['content'], 
                        height=120, 
                        key=f"draft_text_{draft['id']}"
                    )
                    
                    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                    
                    if btn_col1.button("✅ Onayla ve Paylaş", key=f"publish_{draft['id']}"):
                        success, res = publish_tweet(edited_content, draft['media_url'])
                        if success:
                            db.update_draft(draft['id'], content=edited_content, status='published', tweet_id=res)
                            st.success(f"Tweet Paylaşıldı! ({res})")
                            st.rerun()
                        else:
                            st.error(f"Paylaşım Hatası: {res}")
                            
                    if btn_col2.button("💾 Güncelle", key=f"update_{draft['id']}"):
                        db.update_draft(draft['id'], content=edited_content)
                        st.toast("Taslak güncellendi!", icon="💾")
                        
                    if btn_col3.button("🎨 Yeni Görsel Üret", key=f"reimage_{draft['id']}"):
                        new_img = generate_gs_card(text=edited_content[:200], category=draft['category'])
                        db.update_draft(draft['id'], media_url=new_img)
                        st.rerun()
                        
                    if btn_col4.button("❌ Reddet / Sil", key=f"delete_{draft['id']}"):
                        db.update_draft(draft['id'], status='rejected')
                        st.toast("Taslak reddedildi.", icon="🗑️")
                        st.rerun()
                        
            st.divider()

# ---------------------------------------------------------
# TAB 3: YAYINLANAN GEÇMİŞ
# ---------------------------------------------------------
with tab_history:
    st.subheader("📊 Yayınlanan & Geçmiş Gönderiler")
    
    status_filter = st.radio("Filtrele:", ["Tümü", "Yayınlananlar", "Reddedilenler"], horizontal=True)
    
    if status_filter == "Yayınlananlar":
        history_items = db.get_drafts(status='published')
    elif status_filter == "Reddedilenler":
        history_items = db.get_drafts(status='rejected')
    else:
        history_items = db.get_drafts()
        
    if not history_items:
        st.info("Kayıtlı geçmiş bulunamadı.")
    else:
        for item in history_items:
            status_color = "green" if item['status'] == 'published' else ("orange" if item['status'] == 'draft' else "red")
            st.markdown(f"**[{item['status'].upper()}]** #{item['id']} - {item['title']} *(Tarih: {item['updated_at'][:16]})*")
            st.code(item['content'])
            if item.get('tweet_id'):
                st.caption(f"Tweet ID: {item['tweet_id']}")
            st.divider()

# ---------------------------------------------------------
# TAB 4: X MONETIZATION & PARA KAZANMA TAKTİKLERİ
# ---------------------------------------------------------
with tab_monetize:
    st.subheader("💰 X (Twitter) Etkileşim ve Para Kazanma Rehberi")
    
    st.markdown("""
    ### 🎯 Le Marca Sports & Fabrizio Romano Tarzı Viral Tweet Taktikleri:

    #### 1. 🚨 Başta Emoji + Alt Satırda Kaynak / Muhabir Belirtme (Le Marca Stili)
    - Örnek Format:
      ```text
      🚨 Mauro Icardi, şu an itibarıyla Lazio'nun gündeminden çıktı. Lazio, tüm odağını Andrea Pinamonti'ye verdi.

      (Matteo Moretto)
      ```
    - Bu format X üzerinde %100 profesyonel haber hesabı algısı oluşturur ve en yüksek RT/Beğeni oranına sahiptir.

    #### 2. 🕒 En Yüksek Etkileşim Saatleri
    - **Maç Günleri:** Maç başlamadan 1 saat önce ve maç bittikten ilk 30 dakika içinde.
    - **Normal Günler:** Öğle 12:00 - 13:00 ve Akşam 20:30 - 22:30.
    """)
