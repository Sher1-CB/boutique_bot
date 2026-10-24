import streamlit as st
import requests
import random
import io
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ==========================================
# 1. YOUR API KEY (PASTE YOUR KEY HERE!)
# ==========================================
PIXABAY_API_KEY = "58198183-064b4494b86b7907c82011ee6"

st.set_page_config(page_title="Boutique Daily Post", page_icon="✨", layout="centered")

# ==========================================
# 2. CAPTION & FILTER LOGIC
# ==========================================
US_SPECIAL_OCCASIONS = {
    (1, 1): "New Year's Day", (2, 14): "Valentine's Day", (3, 17): "St. Patrick's Day",
    (7, 4): "Independence Day", (10, 31): "Halloween", (11, 28): "Thanksgiving Week",
    (12, 24): "Christmas Eve", (12, 25): "Christmas Day", (12, 31): "New Year's Eve"
}

FB_RESTRICTED_WORDS = [
    "like and share", "tag a friend", "comment below", "click here",
    "giveaway", "free", "buy now", "discount", "cheap", "guaranteed",
    "dm for price", "follow us for more"
]

def sanitize_for_facebook(text: str) -> str:
    for word in FB_RESTRICTED_WORDS:
        if word.lower() in text.lower():
            text = text.replace(word, "[curated pick]")
    return text

def get_daily_caption():
    today = datetime.now()
    formatted_date = today.strftime("%B %d")
    day_name = today.strftime("%A").upper()
    
    holiday = US_SPECIAL_OCCASIONS.get((today.month, today.day), None)
    tag = f" — Celebrating {holiday} vibes!" if holiday else ""

    templates = {
        "MONDAY": (
            f"[{formatted_date}] Boutique Discoveries ✨{tag}\n\n"
            f"Catch our finds landing faster over on our TG during peak hours! 📲\n"
            f"Look up TCB Finds over there to follow along with new arrivals.\n\n"
            f"🤫 This space is kept quiet so today's list stays quick and easy to browse.\n"
            f"Keep this post saved so our updates remain easy to find on your home screen. ✅\n"
            f"Looking for something specific? Add your requests to the Wishlist thread pinned up top! 🏹"
        ),
        "TUESDAY": (
            f"[{formatted_date}] Boutique Daily Digest 💎{tag}\n\n"
            f"We share finds more often on our TG throughout the day! 🏃‍♀️\n"
            f"Look up TCB over there to catch everything the second it lands. ✨\n\n"
            f"This wall is kept simple and organized to help you browse without clutter.\n"
            f"Stay tuned here so our community roundups remain part of your daily view. 🎯\n"
            f"📝 Have a request today? Head over to the Featured section and let us know! 💖"
        ),
        "WEDNESDAY": (
            f"✨ The Daily List: [{formatted_date}]{tag}\n\n"
            f"Everything moves fast! 📲 We post live finds on TG all afternoon. 🚀\n"
            f"Look up TCB over there to join the rest of the crew!\n\n"
            f"🤫 This overview stays organized so your daily list is clean and effortless to read.\n"
            f"Check in with us daily to stay in the loop whenever new items go live. ✅\n"
            f"Want us to hunt for an item? Add your requests to our pinned Wishlist post! 🎁"
        ),
        "THURSDAY": (
            f"💎 Boutique Highlights — [{formatted_date}]{tag}\n\n"
            f"Want first dibs? 👟 Head over to our TG for real-time additions all day long! 🚀\n"
            f"Look up TCB Finds over there to browse along with the community.\n\n"
            f"🤫 This board stays uncluttered so nothing gets lost in the shuffle.\n"
            f"Keep visiting the group to make sure you see our newest posts first. 🎯\n"
            f"Tell us what to look for next inside the Wishlist thread pinned at the front! 🌈"
        ),
        "FRIDAY": (
            f"The Friday Scout List — [{formatted_date}] ✨{tag}\n\n"
            f"Catch the biggest rush of the week over on our TG! ✈️\n"
            f"Look up TCB over there to spot updates the second they roll in. 🏃‍♀️\n\n"
            f"🤫 Keeping this board clear so the weekend list stays simple to scroll.\n"
            f"Pin this group to your favorites to keep our daily rounds in your main view. 📌\n"
            f"Planning your weekend? Add your asks to our pinned Wishlist board! 🏹"
        ),
        "SATURDAY": (
            f"Weekend Edition — [{formatted_date}] 🌟{tag}\n\n"
            f"Finds are rolling out quickly today! 📲 Head over to our TG for rapid posts. ⚡\n"
            f"Look up TCB Finds over there to catch every item right as it arrives.\n\n"
            f"🤫 A quiet space dedicated to today's list so you can easily spot what is new.\n"
            f"Keep interacting with the group to ensure community posts stay front and center. ✅\n"
            f"Tell us what to hunt for this weekend in the Featured Wishlist thread! 🎯"
        ),
        "SUNDAY": (
            f"Sunday Showcase — [{formatted_date}] 🛋️{tag}\n\n"
            f"Relax and browse along! ☕ We keep things moving all evening over on our TG. 📲\n"
            f"Look up TCB over there to catch the latest gems before the new week starts.\n\n"
            f"🤫 This post remains a dedicated showcase to give you a smooth, clean overview.\n"
            f"Check back tomorrow so the new week's finds show up right away. 🎯\n"
            f"Share what you need for the upcoming week in our pinned Wishlist post! 💌"
        )
    }
    return sanitize_for_facebook(templates.get(day_name, templates["MONDAY"]))

# ==========================================
# 3. IMAGE FINDER & BOLD OVERLAY
# ==========================================
def calculate_visual_occupancy(image: Image.Image) -> float:
    gray = image.convert('L')
    edges = gray.filter(ImageFilter.FIND_EDGES)
    return float(np.sum(np.array(edges) > 40) / image.size[0] / image.size[1])

def fetch_clean_image():
    queries = [
        "pastel geometric 3d copy space",
        "pastel spheres minimal background copy space",
        "clean pastel flat lay empty space",
        "minimalist pastel aesthetic copy space"
    ]
    query = random.choice(queries)
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&orientation=all&safesearch=true&per_page=20"
    
    res = requests.get(url).json()
    hits = res.get("hits", [])
    if not hits:
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q=minimalist+pastel+background&image_type=photo&per_page=15"
        hits = requests.get(url).json().get("hits", [])

    for item in hits:
        img_url = item.get("largeImageURL") or item.get("webformatURL")
        img = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")
        if calculate_visual_occupancy(img) <= 0.65:
            return img
            
    first_url = hits[0].get("largeImageURL") or hits[0].get("webformatURL")
    return Image.open(requests.get(first_url, stream=True).raw).convert("RGB")

def apply_clean_bold_text(img: Image.Image) -> Image.Image:
    # Resize to square 1080x1080
    target = 1080
    img = img.resize((target, target), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    date_str = datetime.now().strftime("%B %d").upper() # e.g. "OCTOBER 23"
    
    # Try bold modern fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "arialbd.ttf", "arial.ttf"
    ]
    font_title, font_date = None, None
    for p in font_paths:
        try:
            font_title = ImageFont.truetype(p, 54)
            font_date = ImageFont.truetype(p, 130)
            break
        except:
            continue
            
    if not font_title:
        font_title = font_date = ImageFont.load_default()

    # Crisp bold black typography centered directly on image
    black = (17, 17, 17)
    draw.text((540, 480), "TODAY'S PICKS", fill=black, font=font_title, anchor="mm")
    draw.text((540, 580), date_str, fill=black, font=font_date, anchor="mm")
    
    return img

# ==========================================
# 4. WEB INTERFACE (WHAT COWORKER SEES)
# ==========================================
st.title("✨ Daily Boutique Post Generator")

col1, col2 = st.columns([1, 1])

if "current_image" not in st.session_state:
    with st.spinner("Finding today's photo..."):
        st.session_state.current_image = apply_clean_bold_text(fetch_clean_image())

with col1:
    st.subheader("📸 Today's Image")
    st.image(st.session_state.current_image, use_container_width=True)
    
    buf = io.BytesIO()
    st.session_state.current_image.save(buf, format="JPEG", quality=95)
    st.download_button(
        label="📥 Download Photo",
        data=buf.getvalue(),
        file_name=f"post_{datetime.now().strftime('%Y-%m-%d')}.jpg",
        mime="image/jpeg",
        use_container_width=True
    )
    
    if st.button("🔄 Try Another Background", use_container_width=True):
        st.session_state.current_image = apply_clean_bold_text(fetch_clean_image())
        st.rerun()

with col2:
    st.subheader("📝 Today's Caption")
    caption = get_daily_caption()
    st.text_area("Copy Caption Below:", value=caption, height=350)
