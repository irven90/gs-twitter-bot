import os
import random
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

CARDS_DIR = os.path.join(os.path.dirname(__file__), "assets", "generated_cards")
FONTS_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")
os.makedirs(CARDS_DIR, exist_ok=True)

REGULAR_FONT_PATH = os.path.join(FONTS_DIR, "font.ttf")
BOLD_FONT_PATH = os.path.join(FONTS_DIR, "font_bold.ttf")

def load_custom_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Loads bundled TTF font supporting full Turkish character set."""
    target_path = BOLD_FONT_PATH if bold else REGULAR_FONT_PATH
    if os.path.exists(target_path):
        try:
            return ImageFont.truetype(target_path, size)
        except Exception as e:
            print(f"Font load error: {e}")
            
    system_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in system_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def clean_text_for_card(text: str) -> str:
    """Strips emojis AND hashtags from the text so graphic card contains ONLY pure text statements."""
    text_no_emoji = re.sub(r'[\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF]', '', text)
    text_no_hashtag = re.sub(r'#\w+', '', text_no_emoji)
    return text_no_hashtag.strip()

DYNAMIC_BADGES = ["SON DAKİKA", "GÜNDEM", "FLAŞ HABER", "TARAFTAR SESİ", "MAÇ ANALİZİ", "TRANSFER GÜNDEMİ"]

THEMES = [
    {
        "bg_top": (120, 10, 30),     # Deep GS Red
        "bg_bottom": (15, 15, 20),   # Midnight Dark
        "accent": (253, 185, 19),    # GS Gold
        "badge_bg": (253, 185, 19),
        "badge_fg": (10, 10, 10),
        "text_color": (255, 255, 255),
        "border_color": (253, 185, 19)
    },
    {
        "bg_top": (15, 20, 35),      # Neon Dark Blue
        "bg_bottom": (8, 8, 12),
        "accent": (255, 215, 0),     # Neon Gold
        "badge_bg": (180, 10, 35),    # Red Badge
        "badge_fg": (255, 255, 255),
        "text_color": (245, 245, 250),
        "border_color": (255, 215, 0)
    },
    {
        "bg_top": (175, 15, 45),     # Crimson Red
        "bg_bottom": (40, 20, 10),
        "accent": (255, 220, 90),
        "badge_bg": (0, 0, 0),
        "badge_fg": (253, 185, 19),
        "text_color": (255, 255, 255),
        "border_color": (253, 185, 19)
    },
    {
        "bg_top": (25, 25, 30),      # Modern Dark Gold Accent
        "bg_bottom": (10, 10, 12),
        "accent": (230, 35, 55),
        "badge_bg": (230, 35, 55),
        "badge_fg": (255, 255, 255),
        "text_color": (255, 255, 255),
        "border_color": (230, 35, 55)
    }
]

def generate_gs_card(text: str, category: str = None, title: str = None) -> str:
    """
    Generates a compact 800x380 graphic card.
    Returns absolute file path.
    """
    width, height = 800, 380
    clean_text = clean_text_for_card(text)
    
    badge_label = category.upper() if category else random.choice(DYNAMIC_BADGES)
    theme = random.choice(THEMES)
    
    img = Image.new("RGBA", (width, height), color=(15, 15, 20, 255))
    draw = ImageDraw.Draw(img)
    
    t_top = theme["bg_top"]
    t_bot = theme["bg_bottom"]
    for y in range(height):
        ratio = y / float(height)
        r = int(t_top[0] * (1 - ratio) + t_bot[0] * ratio)
        g = int(t_top[1] * (1 - ratio) + t_bot[1] * ratio)
        b = int(t_top[2] * (1 - ratio) + t_bot[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    draw.rectangle([0, 0, width, 8], fill=theme["accent"])
    draw.rectangle([0, height - 8, width, height], fill=theme["accent"])
    
    # Sol Üst: Badge Pill
    badge_font = load_custom_font(18, bold=True)
    badge_text = f"  {badge_label}  "
    bbox = badge_font.getbbox(badge_text)
    b_width = bbox[2] - bbox[0] + 20
    b_height = 34
    
    draw.rectangle([35, 25, 35 + b_width, 25 + b_height], fill=theme["badge_bg"])
    draw.text((45, 32), badge_label, fill=theme["badge_fg"], font=badge_font)
    
    # Center Container Box
    card_x1, card_y1 = 35, 75
    card_x2, card_y2 = width - 35, height - 55
    
    draw.rectangle([card_x1, card_y1, card_x2, card_y2], fill=(15, 18, 25, 220), outline=theme["border_color"], width=2)
    draw.rectangle([card_x1, card_y1, card_x1 + 6, card_y2], fill=theme["accent"])
    
    # Dynamic Text Wrap
    char_len = len(clean_text)
    if char_len < 100:
        font_size = 23
        wrap_w = 48
    elif char_len < 180:
        font_size = 19
        wrap_w = 58
    else:
        font_size = 16
        wrap_w = 66
        
    main_font = load_custom_font(font_size, bold=True)
    wrapped_lines = textwrap.wrap(clean_text, width=wrap_w)
    wrapped_text = "\n".join(wrapped_lines)
    
    draw.multiline_text((card_x1 + 25, card_y1 + 20), f"“{wrapped_text}”", fill=theme["text_color"], font=main_font, spacing=8)
    
    # Sağ Alt: @Boss_Osimhen
    footer_font = load_custom_font(18, bold=True)
    draw.text((width - 200, height - 42), "@Boss_Osimhen", fill=theme["accent"], font=footer_font)
    
    final_img = Image.new("RGB", (width, height), (15, 15, 20))
    final_img.paste(img, mask=img.split()[3])
    
    filename = f"gs_card_{os.urandom(4).hex()}.png"
    filepath = os.path.abspath(os.path.join(CARDS_DIR, filename))
    final_img.save(filepath, format="PNG")
    return filepath
