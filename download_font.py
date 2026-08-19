import os
import urllib.request

FONTS_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)
FONT_PATH = os.path.join(FONTS_DIR, "Roboto-Bold.ttf")

def ensure_font_exists():
    if not os.path.exists(FONT_PATH) or os.path.getsize(FONT_PATH) < 1000:
        print("Downloading Roboto-Bold.ttf font...")
        url = "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/static/Roboto-Bold.ttf"
        try:
            urllib.request.urlretrieve(url, FONT_PATH)
            print("Font downloaded successfully!")
        except Exception as e:
            print(f"Error downloading font: {e}")

if __name__ == "__main__":
    ensure_font_exists()
