# 💛❤️ Galatasaray & Futbol X (Twitter) İçerik Botu ve Taslak Paneli

Bu proje, Galatasaray ve Türk futbolu gündemini takip eden, tutkulu, sert ve eleştirel tonda tweet'ler ile sarı-kırmızı grafik kartları üreten ve **Streamlit tabanlı bir Taslak & Onay Paneli** üzerinden kontroller sunan tam kapsamlı bir Python uygulamasıdır.

---

## 🌟 Öne Çıkan Özellikler

1. **📰 Canlı Gündem Takibi:** RSS beslemeleri üzerinden güncel Galatasaray ve Süper Lig haberlerini çeker, tek tıkla haberden tweet üretir.
2. **🔥 GS Taraftarı & Eleştirmen Persona:** Sert, net ve tutkulu Galatasaray tonunda özelleştirilmiş AI prompt yapısı (Gemini / OpenAI uyumlu veya çevrimdışı şablon motoru).
3. **🎨 Sarı-Kırmızı Grafik Kartı Üreteci:** Üretilen tweet için otomatik olarak Galatasaray renklerinde ve tipografisinde yüksek çözünürlüklü sosyal medya görseli tasarlar.
4. **📝 Taslak ve Onay Paneli:** Üretilen tüm tweet'leri biriktirir. Yayınlamadan önce metni düzenlemenize, yeni görsel oluşturmanıza veya reddetmenize olanak tanır.
5. **🚀 X (Twitter) Paylaşım & Simülasyon Modu:** X API anahtarlarınız varsa doğrudan X'te paylaşır. Anahtar olmasa dahi **Simülasyon Modu** ile güvenle test edilir.

---

## 🛠️ Hızlı Kurulum ve Çalıştırma

### 1. Gerekli Paketlerin Yüklenmesi
```bash
pip install -r requirements.txt
```

### 2. Uygulamanın Başlatılması
```bash
streamlit run app.py
```

Uygulama tarayıcınızda otomatik olarak açılacaktır (`http://localhost:8501`).

---

## 📂 Proje Yapısı

- `app.py`: Streamlit web arayüzü ve onay paneli
- `ai_generator.py`: GS taraftarı üslubunda tweet ve grafik prompt üreticisi
- `card_generator.py`: Sarı-kırmızı grafik kartı oluşturan PIL modülü
- `news_fetcher.py`: Canlı futbol ve GS gündem haberleri çekici
- `database.py`: SQLite veritabanı (Taslak, Yayınlanan, Reddedilen yönetimi)
- `twitter_client.py`: Tweepy/X API paylaşım ve simülasyon istemcisi
- `test_bot.py`: Entegrasyon test senaryoları
