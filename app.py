import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- AYARLAR ---
API_KEY = "AIzaSyA89yPg93ZrDYh5FkweAPfBL2Dqg19uC4s"

# Sayfa Ayarları
st.set_page_config(
    page_title="TextHero", 
    page_icon="✨", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# Gemini Kurulumu
genai.configure(api_key=API_KEY)

# --- SOL MENÜ ---
with st.sidebar:
    st.title("⚙️ Panel")
    theme_mode = st.toggle("🌙 Karanlık Mod", value=True)
    st.divider()
    option = st.selectbox(
        'Yapay Zeka Modu',
        ('Detaylı Analiz', 'Romantik & Etkileyici', 'Cool & Esprili', 'Kanka Modu', 'Laf Sokucu')
    )
    st.info("Modu buradan değiştirebilirsin.")

# --- ARKA PLAN VE TEMA AYARLARI ---
# Bulutlu duvar kağıdı linki (Modern ve sade bir görsel)
bg_img_url = "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?q=80&w=2000&auto=format&fit=crop"

if theme_mode:
    overlay_color = "rgba(14, 17, 23, 0.85)" # Siyah bulutlu efekt için
    text_color = "#ffffff"
    card_bg = "rgba(31, 34, 41, 0.9)"
    uploader_border = "rgba(255, 255, 255, 0.3)"
else:
    overlay_color = "rgba(255, 255, 255, 0.85)" # Beyaz bulutlu efekt için
    text_color = "#000000"
    card_bg = "rgba(240, 242, 246, 0.9)"
    uploader_border = "rgba(0, 0, 0, 0.3)"

# --- CSS İLE DUVAR KAĞIDI ENTEGRASYONU ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient({overlay_color}, {overlay_color}), url("{bg_img_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: {text_color};
    }}
    
    /* Dosya Yükleme Alanı */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {card_bg};
        border-color: {uploader_border};
        border-radius: 15px;
    }}
    [data-testid="stFileUploaderDropzone"] div, [data-testid="stFileUploaderDropzone"] small {{
        color: {text_color} !important;
    }}

    /* Alt Çizgileri ve Gereksiz Menüleri Gizle */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Başlık Stilini Parlat */
    h1 {{
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- MODEL SEÇİCİ ---
def get_auto_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in available_models if 'flash' in m), 
                            next((m for m in available_models if 'vision' in m), 
                            available_models[0] if available_models else None))
        return genai.GenerativeModel(chosen_model) if chosen_model else None, chosen_model
    except: return None, None

model, _ = get_auto_model()

# --- ANA EKRAN ---
st.title("✨ TextHero")
st.write("Görseli bulutların arasına bırak, gerisini ben hallederim.")

uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    if st.button('✨ Analizi Başlat', type="primary"):
        if not model:
            st.error("Bağlantı hatası.")
        else:
            with st.spinner('TextHero bulutların arasında düşünüyor...'):
                try:
                    prompt = f"Bu görseldeki duruma Türkçe {option.lower()} tarzında bir cevap ver."
                    response = model.generate_content([prompt, image])
                    
                    st.markdown(f"""
                    <div style="background-color: {card_bg}; padding: 20px; border-radius: 15px; color: {text_color}; border: 1px solid {uploader_border}; backdrop-filter: blur(5px);">
                        <h4>💡 TextHero Tavsiyesi:</h4>
                        <p>{response.text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

st.divider()
st.caption("Developed by Poyraz Dede © 2026")