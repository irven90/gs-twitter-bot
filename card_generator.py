import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap

CARDS_DIR = os.path.join(os.path.dirname(__file__), "assets", "generated_cards")
os.makedirs(CARDS_DIR, exist_ok=True)

def generate_gs_card(text: str, category: str = "GALATASARAY GÜNDEM", title: str = "TARAFTAR ELEŞTİRİSİ") -> str:
    """
    Generates a 1200x675 Galatasaray styled graphic card with custom text overlay.
    Returns absolute path of the generated PNG file.
    """
    width, height = 1200, 675
    
    # Base background with GS Dark Red to Gold Yellow subtle gradient effect
    img = Image.new("RGB", (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient overlay / stripes
    # Dark red (#800000 -> #A90429) to Yellow Gold (#FDB913)
    for i in range(height):
        r = int(120 - (i / height) * 80)
        g = int(10 + (i / height) * 20)
        b = int(20 + (i / height) * 20)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
        
    # Decorative GS Yellow & Red Accent Bars
    # Top bar
    draw.rectangle([0, 0, width, 18], fill=(253, 185, 19)) # Gold Yellow
    draw.rectangle([0, 18, width, 24], fill=(169, 4, 41))  # Crimson Red
    
    # Bottom bar
    draw.rectangle([0, height-24, width, height-18], fill=(169, 4, 41))
    draw.rectangle([0, height-18, width, height], fill=(253, 185, 19))
    
    # Side badge highlight
    draw.rectangle([40, 60, 48, 140], fill=(253, 185, 19))
    
    # Header Fonts & Text
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        cat_font = ImageFont.truetype("arialbd.ttf", 22)
        body_font = ImageFont.truetype("arial.ttf", 32)
        footer_font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        title_font = ImageFont.load_default()
        cat_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
        
    # Draw Category Badge
    draw.text((65, 65), category.upper(), fill=(253, 185, 19), font=cat_font)
    draw.text((65, 95), title.upper(), fill=(255, 255, 255), font=title_font)
    
    # Divider line
    draw.line([(60, 155), (width - 60, 155)], fill=(253, 185, 19), width=2)
    
    # Format Body Text
    wrapped_text = textwrap.fill(text, width=42)
    
    # Draw body quote box background
    draw.rectangle([60, 180, width - 60, height - 90], fill=(0, 0, 0, 160), outline=(253, 185, 19), width=1)
    
    # Draw Body Text inside box
    draw.text((90, 210), wrapped_text, fill=(245, 245, 245), font=body_font, spacing=10)
    
    # Draw Footer
    draw.text((65, height - 70), "💛 TR’NİN EN BÜYÜK KULÜBÜ GALATASARAY ❤️", fill=(253, 185, 19), font=footer_font)
    draw.text((width - 250, height - 70), "@GS_Elestirmeni", fill=(200, 200, 200), font=footer_font)
    
    # Save Image
    filename = f"gs_card_{os.urandom(4).hex()}.png"
    filepath = os.path.join(CARDS_DIR, filename)
    img.save(filepath, format="PNG")
    return filepath
