import os
import random
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CARDS_DIR = os.path.join(os.path.dirname(__file__), "assets", "generated_cards")
os.makedirs(CARDS_DIR, exist_ok=True)

# System Font Finder for Windows / Linux
FONT_PATHS = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/tahomabd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Loads a high-quality system truetype font supporting Turkish characters."""
    font_candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahomabd.ttf" if bold else "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    # Fallback search
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()

def strip_emojis(text: str) -> str:
    """Strips emojis that PIL default fonts cannot render to avoid square replacement boxes."""
    return re.sub(r'[\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF]', '', text).strip()

# 5 Professional Design Themes (Fabrizio Romano & Modern Sports Graphic Style)
THEMES = [
    {
        "name": "GS Red & Gold Classic",
        "bg_top": (115, 6, 28),      # Deep Crimson Red
        "bg_bottom": (18, 18, 22),   # Midnight Black
        "accent": (253, 185, 19),    # Gold Yellow
        "badge_bg": (253, 185, 19),
        "badge_fg": (15, 15, 15),
        "text_color": (255, 255, 255),
        "card_bg": (28, 28, 36, 220),
        "border_color": (253, 185, 19)
    },
    {
        "name": "Night Football Neon",
        "bg_top": (10, 15, 28),      # Dark Navy
        "bg_bottom": (5, 5, 8),      # Deep Dark
        "accent": (255, 215, 0),     # Neon Yellow
        "badge_bg": (169, 4, 41),    # Crimson Red
        "badge_fg": (255, 255, 255),
        "text_color": (240, 240, 245),
        "card_bg": (18, 22, 34, 230),
        "border_color": (255, 215, 0)
    },
    {
        "name": "Parçalı Gold Luxury",
        "bg_top": (169, 4, 41),      # GS Red
        "bg_bottom": (130, 80, 0),   # GS Gold
        "accent": (255, 230, 100),
        "badge_bg": (0, 0, 0),
        "badge_fg": (253, 185, 19),
        "text_color": (255, 255, 255),
        "card_bg": (15, 15, 20, 240),
        "border_color": (253, 185, 19)
    },
    {
        "name": "Flaş Haber Dark",
        "bg_top": (25, 25, 30),
        "bg_bottom": (10, 10, 12),
        "accent": (230, 30, 50),     # Bright Red
        "badge_bg": (230, 30, 50),
        "badge_fg": (255, 255, 255),
        "text_color": (255, 255, 255),
        "card_bg": (32, 32, 40, 220),
        "border_color": (230, 30, 50)
    },
    {
        "name": "Minimalist Champion",
        "bg_top": (15, 15, 18),
        "bg_bottom": (35, 10, 15),
        "accent": (253, 185, 19),
        "badge_bg": (253, 185, 19),
        "badge_fg": (0, 0, 0),
        "text_color": (245, 245, 245),
        "card_bg": (22, 22, 28, 230),
        "border_color": (253, 185, 19)
    }
]

def generate_gs_card(text: str, category: str = "GALATASARAY GÜNDEM", title: str = "TARAFTAR ELEŞTİRİSİ", theme_index: int = None) -> str:
    """
    Generates a ultra-professional 1200x675 graphic quote card with dynamic themes & Turkish character support.
    """
    width, height = 1200, 675
    clean_text = strip_emojis(text)
    
    # Pick theme
    if theme_index is not None and 0 <= theme_index < len(THEMES):
        theme = THEMES[theme_index]
    else:
        theme = random.choice(THEMES)
        
    # Base Image & Canvas
    img = Image.new("RGBA", (width, height), color=(15, 15, 20, 255))
    draw = ImageDraw.Draw(img)
    
    # Create Smooth Background Gradient
    t_top = theme["bg_top"]
    t_bot = theme["bg_bottom"]
    for y in range(height):
        ratio = y / float(height)
        r = int(t_top[0] * (1 - ratio) + t_bot[0] * ratio)
        g = int(t_top[1] * (1 - ratio) + t_bot[1] * ratio)
        b = int(t_top[2] * (1 - ratio) + t_bot[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Top & Bottom Accent Lines
    draw.rectangle([0, 0, width, 12], fill=theme["accent"])
    draw.rectangle([0, height - 12, width, height], fill=theme["accent"])
    
    # Large Decorative Watermark Quote Mark “ in background
    quote_font = load_font(280, bold=True)
    draw.text((width - 240, 40), "“", fill=(255, 255, 255, 20), font=quote_font)
    
    # Category Badge (Pill Badge Style)
    badge_font = load_font(22, bold=True)
    category_text = f"  {category.upper()}  "
    bbox = badge_font.getbbox(category_text)
    b_width = bbox[2] - bbox[0] + 30
    b_height = 42
    
    # Draw Badge Background
    badge_x, badge_y = 70, 50
    draw.rectangle([badge_x, badge_y, badge_x + b_width, badge_y + b_height], fill=theme["badge_bg"])
    draw.text((badge_x + 15, badge_y + 8), category.upper(), fill=theme["badge_fg"], font=badge_font)
    
    # Title / Handle Sub-header
    sub_font = load_font(20, bold=True)
    draw.text((badge_x + b_width + 20, badge_y + 10), title.upper(), fill=theme["accent"], font=sub_font)
    
    # Main Card Box Container (Glassmorphism style with rounded border)
    card_x1, card_y1 = 70, 125
    card_x2, card_y2 = width - 70, height - 90
    
    # Inner dark box fill
    draw.rectangle([card_x1, card_y1, card_x2, card_y2], fill=theme["card_bg"], outline=theme["border_color"], width=2)
    
    # Left Accent Bar inside Card Box
    draw.rectangle([card_x1, card_y1, card_x1 + 8, card_y2], fill=theme["accent"])
    
    # Dynamic Text Sizing & Auto-wrapping based on content length
    char_len = len(clean_text)
    if char_len < 100:
        font_size = 36
        wrap_width = 38
    elif char_len < 180:
        font_size = 30
        wrap_width = 46
    else:
        font_size = 24
        wrap_width = 54
        
    main_font = load_font(font_size, bold=True)
    wrapped_lines = textwrap.wrap(clean_text, width=wrap_width)
    wrapped_text = "\n".join(wrapped_lines)
    
    # Draw Main Text Inside Card
    text_x = card_x1 + 45
    text_y = card_y1 + 35
    draw.multiline_text((text_x, text_y), f"“{wrapped_text}”", fill=theme["text_color"], font=main_font, spacing=12)
    
    # Footer Section (Watermark & Handle)
    footer_font = load_font(20, bold=True)
    draw.text((70, height - 60), "GALATASARAY İÇERİK MERKEZİ", fill=theme["accent"], font=footer_font)
    draw.text((width - 260, height - 60), "@GS_TARAFTAR_BOT", fill=(200, 200, 200), font=footer_font)
    
    # Convert RGBA to RGB for JPEG/PNG output
    final_img = Image.new("RGB", (width, height), (20, 20, 20))
    final_img.paste(img, mask=img.split()[3])
    
    # Save Image
    filename = f"gs_card_{os.urandom(4).hex()}.png"
    filepath = os.path.join(CARDS_DIR, filename)
    final_img.save(filepath, format="PNG")
    return filepath
