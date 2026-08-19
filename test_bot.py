import os
import database as db
from ai_generator import generate_tweet_content
from news_fetcher import fetch_latest_football_news
from twitter_client import publish_tweet

def test_database():
    db.init_db()
    draft_id = db.create_draft(
        title="Test Maç Analizi",
        content="Galatasaray sahada inanılmaz bir hırs sergiledi. Hakem kararlarına rağmen 3 puanı aldık! #Galatasaray",
        category="Maç Analizi"
    )
    assert draft_id is not None
    drafts = db.get_drafts(status='draft')
    assert len(drafts) >= 1
    
    # Test update
    db.update_draft(draft_id, status='published', tweet_id="test_12345")
    updated = db.get_draft_by_id(draft_id)
    assert updated['status'] == 'published'
    assert updated['tweet_id'] == "test_12345"
    print("✅ Veritabanı testleri başarılı!")

def test_ai_generator_and_cards():
    res = generate_tweet_content(
        topic="Süper Lig VAR Hakem Kararları",
        category="Hakem Eleştirisi",
        tone="Sert & Eleştirel",
        include_card=True
    )
    assert "content" in res
    assert len(res["content"]) > 10
    if res.get("media_url"):
        assert os.path.exists(res["media_url"])
    print("✅ AI İçerik ve Görsel Kart Üretim testi başarılı!")

def test_publisher():
    success, res_id = publish_tweet("Test tweet metni #Galatasaray")
    assert success is True
    print(f"✅ Paylaşım (Simülasyon) testi başarılı: {res_id}")

def test_news_fetcher():
    articles = fetch_latest_football_news()
    assert len(articles) > 0
    print(f"✅ Gündem Haber Çekme testi başarılı! ({len(articles)} haber bulundu)")

if __name__ == "__main__":
    print("Starting integration tests...")
    test_database()
    test_ai_generator_and_cards()
    test_publisher()
    test_news_fetcher()
    print("\n🎉 TÜM TESTLER BAŞARIYLA TAMAMLATILDI!")
