import streamlit as st
import os
import re
import random
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
    page_title="Galatasaray X Botu & Onay Paneli",
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

# Safe Tweet Generation Engine with Tone-Specific Fallbacks (Zero Static Duplicates!)
def run_tweet_engine(topic, category, tone, style, mode):
    clean_t = purge_newspaper_names(topic)
    try:
        res = generate_tweet_content(topic=clean_t, category=category, tone=tone, style=style, mode=mode)
        if res and res.get('content'):
            return res
    except Exception as e:
        print(f"Engine error: {e}")
        
    # Distinct fallback content matching selected tone/style
    if tone == "Sert & Eleştirel":
        fallback_text = f"Yine başladılar hakem oyunlarına! {clean_t} konusundaki bu haksızlıklara karşı duracağız! 🦁🔥 #Galatasaray #GS"
    elif tone == "Tutkulu Taraftar":
        fallback_text = f"Armanın peşinde tek yürek! {clean_t} ne olursa olsun Hedef 25. Şampiyonluk! 💛❤️ #Galatasaray #GS"
    elif tone == "Taktik Analiz":
        fallback_text = f"Okan Hoca'nın saha içi taktik hamlesi mükemmel! {clean_t} sürecinde pres ve alan paylaşımı kusursuz. ⚽ #GS"
    elif tone == "Le Marca Style (Haber & Kaynak)" or style == "Haber & Kaynak Formatı (Le Marca)":
        fallback_text = f"🚨 {clean_t} hakkında Florya'dan sıcak bilgi ulaştı. Yönetim gelişmeleri takip ediyor.\n\n(Nevzat Dindar)"
    elif style == "📊 X Anket Formatı":
        fallback_text = f"📊 Sizce {clean_t} konusunda yönetim nasıl adım atmalı taraftar?\n\nA) Doğru Karar 🔥\nB) Yanlış Karar ❌\nC) Kararsızım 🤔\n\n#Galatasaray #GS"
    elif style == "💬 Alıntı & Tepki Tweeti":
        fallback_text = f"💬 {clean_t} haberinin neresinden tutsan elinde kalıyor valla. Şaşırdık mı? Tabii ki hayır! 🦁 #GS"
    else:
        fallback_text = f"Osimhen ve ekibi sahaya çıktı mı kimsede laf kalmaz! {clean_t} duyumu hakkında biz şampiyonluğa kilitlendik kardeş! 💛❤️ #Galatasaray #GS"

    media_url = None
    media_type = "none"
    if mode == "graphic":
        try:
            media_url = generate_gs_card(text=fallback_text[:220], category=category)
            media_type = "image"
        except Exception:
            pass
            
    return {
        "title": clean_t[:50],
        "content": fallback_text,
        "category": category,
        "media_type": media_type,
        "media_url": media_url
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

# Fetch news items
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

default_topic = news_items[0]['title'] if news_items else "🚨 Mauro Icardi transfer gündemi hakkında sıcak gelişme"

# Initialize Session State Variables
if 'topic_box' not in st.session_state:
    st.session_state['topic_box'] = default_topic

# Sidebar Setup
st.sidebar.title("💛❤️ GS Twitter Bot")
st.sidebar.markdown("**@Boss_Osimhen Organik Otomasyonu**")
st.sidebar.caption("🎯 @Boss_Osimhen Taraftar Personası & Viral Akış")
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
st.title("⚽ Galatasaray X @Boss_Osimhen Taraftar Botu")
st.caption("Kahve ve stadyum sohbeti sıcaklığında organik tweetler üretin, taslak onay paneliyle yayınlayın!")

# Navigation Tabs
tab_create, tab_drafts, tab_history, tab_monetize = st.tabs([
    "🚀 İçerik Üret", 
    "📝 Taslak & Onay Paneli", 
    "📊 Yayınlanan Geçmiş", 
    "💰 X Para Kazanma Taktikleri"
])

# ---------------------------------------------------------
# TAB 1: İÇERİK ÜRETİMİ
# ---------------------------------------------------------
with tab_create:
    col_news, col_gen = st.columns([1, 1])
    
    with col_news:
        st.subheader("🚨 Sıcak Futbol & Transfer Akışı")
        st.caption("Aşağıdaki sıcak futbol gündemlerine tıklayarak anında @Boss_Osimhen taraftar ağzıyla tweet üretebilirsiniz.")
        
        if st.button("🔄 Gündemi Yenile", use_container_width=True):
            st.rerun()
            
        for idx, item in enumerate(news_items):
            with st.expander(f"📌 {item['source']}: {item['title']}"):
                st.write(item['summary'])
                if st.button(f"⚡ Bu Konudan Tweet Üret", key=f"btn_news_{idx}"):
                    st.session_state['topic_box'] = item['title']
                    gen = run_tweet_engine(
                        topic=item['title'],
                        category="Transfer",
                        tone="Organik Taraftar Ağzı (@Boss_Osimhen)",
                        style="Tartışma & Yorum Alıcı",
                        mode="emoji"
                    )
                    st.session_state['last_generated'] = gen
                    st.session_state['preview_text'] = gen['content']
                    st.rerun()
                    
    with col_gen:
        st.subheader("✏️ @Boss_Osimhen Taraftar Tweet Üretici")
        
        topic_input = st.text_area("İçerik Konusu / Oyuncu İsmi / Duyum Başlığı:", key="topic_box", height=90)
        
        c1, c2, c3 = st.columns(3)
        category_input = c1.selectbox("Kategori:", ["Transfer", "Hakem Eleştirisi", "Maç Analizi", "Gündem", "Genel"])
        tone_input = c2.selectbox("Söylem Tonu:", [
            "Organik Taraftar Ağzı (@Boss_Osimhen)", 
            "Le Marca Style (Haber & Kaynak)", 
            "Sert & Eleştirel", 
            "Tutkulu Taraftar", 
            "Taktik Analiz"
        ])
        style_input = c3.selectbox("Etkileşim Formatı:", [
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
                with st.spinner("Organik tweet üretiliyor..."):
                    gen = run_tweet_engine(
                        topic=topic_input,
                        category=category_input,
                        tone=tone_input,
                        style=style_input,
                        mode="emoji"
                    )
                    st.session_state['last_generated'] = gen
                    st.session_state['preview_text'] = gen['content']
                    st.rerun()

        if btn_c2.button("🎨 Görselli Grafik Tweeti Üret", use_container_width=True):
            if not topic_input.strip():
                st.warning("Lütfen bir konu veya oyuncu ismi girin.")
            else:
                with st.spinner("Görselli grafik tweeti üretiliyor..."):
                    gen = run_tweet_engine(
                        topic=topic_input,
                        category=category_input,
                        tone=tone_input,
                        style=style_input,
                        mode="graphic"
                    )
                    st.session_state['last_generated'] = gen
                    st.session_state['preview_text'] = gen['content']
                    st.rerun()
                    
        if 'last_generated' in st.session_state:
            gen_data = st.session_state['last_generated']
            st.session_state['preview_text'] = gen_data['content']
            
            st.success(f"'{gen_data['title']}' Konusunda ({tone_input}) Tweeti Üretildi!")
            
            st.markdown("### 📱 Tweet Önizleme")
            st.text_area("Üretilen Metin:", key="preview_text", height=130)
            
            if gen_data.get('media_url') and os.path.exists(gen_data['media_url']):
                st.image(gen_data['media_url'], caption="Kompakt GS Grafik Kartı (@Boss_Osimhen)", width=500)
                
            b1, b2 = st.columns(2)
            if b1.button("💾 Taslaklara Kaydet", use_container_width=True):
                draft_id = db.create_draft(
                    title=gen_data['title'],
                    content=gen_data['content'],
                    category=gen_data['category'],
                    media_type=gen_data['media_type'],
                    media_url=gen_data['media_url']
                )
                st.success(f"Taslak kaydedildi! (ID: #{draft_id})")
                del st.session_state['last_generated']
                if 'preview_text' in st.session_state:
                    del st.session_state['preview_text']
                st.rerun()
                
            if b2.button("🚀 Anında Paylaş", use_container_width=True):
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
                    if 'preview_text' in st.session_state:
                        del st.session_state['preview_text']
                    st.rerun()
                else:
                    st.error(tweet_res)

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
                            st.error(res)
                            
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
    ### 🎯 @Boss_Osimhen Organik Taraftar Personası & Viral Taktikler:

    #### 1. 🗣️ "Organik Taraftar Ağzı" Söylemini Kullanın
    - Kuru muhabir haberi değil; stadyum ve kahvehane sohbeti sıcaklığında (*"Abi valla bakıyorum da...", "Yok artık yahu!", "Net söylüyorum..."*) ifadeler kullanın.

    #### 2. 🔑 Twitter API Hataları Çözüm Rehberi
    - **402 Payment Required (Credits Depleted):** Twitter Developer hesabınızın bu ayki 1,500 ücretsiz tweet kotası tükenmiştir. Ürettiğiniz içerikleri **💾 Taslaklara Kaydet** butonuna basarak kaydedebilir ve istediğiniz zaman kopyalayıp manuel veya API yenilenince paylaşabilirsiniz.
    - **401 Unauthorized Hatası:** Access Token ile Consumer Key eşleşmiyordur. [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard) adresinde hem API Key hem de Access Token'ı REGENERATE edin.
    """)
