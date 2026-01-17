import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- AYARLAR ---
st.set_page_config(
    page_title="TextHero Pro", 
    page_icon="✨", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- GÜVENLİK: API ANAHTARINI GİZLİ KASADAN AL ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit panelinden 'Secrets' kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

# --- SOL MENÜ (AYARLAR) ---
with st.sidebar:
    st.title("⚙️ Ayarlar")
    theme_mode = st.toggle("🌙 Karanlık Mod", value=True)
    st.divider()
    st.caption("Developed by Poyraz Dede")

# --- TEMA VE RENK TANIMLARI ---
if theme_mode:
    # Koyu Mod Renkleri (Çoğunluğu Siyah Gradient)
    bg_gradient = "linear-gradient(to bottom right, #000000 50%, #1a1d24 100%)"
    text_color = "#ffffff"
    card_bg = "rgba(31, 34, 41, 0.9)"
    border_color = "rgba(255, 255, 255, 0.2)"
    button_color = "#0d6efd" # Profesyonel Mavi
    button_hover_glow = "rgba(13, 110, 253, 0.6)" # Mavi parlama
else:
    # Aydınlık Mod Renkleri (Temiz Beyaz Gradient)
    bg_gradient = "linear-gradient(to bottom right, #ffffff 50%, #f0f2f6 100%)"
    text_color = "#000000"
    card_bg = "rgba(255, 255, 255, 0.9)"
    border_color = "rgba(0, 0, 0, 0.2)"
    button_color = "#0d6efd" # Profesyonel Mavi
    button_hover_glow = "rgba(13, 110, 253, 0.4)"

# --- CSS İLE TASARIM VE ANİMASYONLAR ---
st.markdown(f"""
    <style>
    /* 1. Arka Plan ve Genel Stil */
    .stApp {{
        background: {bg_gradient};
        background-attachment: fixed;
        color: {text_color};
    }}
    .stTextInput, .stSelectbox, .stFileUploader {{ color: {text_color}; }}
    
    /* 2. Animasyonlar */
    @keyframes slideUp {{ from {{ transform: translateY(20px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}

    /* 3. Eleman Stilleri */
    h1 {{ animation: slideUp 0.8s ease-out; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
    .stMarkdown p {{ animation: slideUp 1s ease-out; }}
    
    /* Mod Seçim Kutusu */
    .stSelectbox > div > div {{
        animation: slideUp 1.2s ease-out;
        border-radius: 10px;
        background-color: {card_bg};
        border: 1px solid {border_color};
    }}

    /* Dosya Yükleme Alanı */
    [data-testid="stFileUploaderDropzone"] {{
        animation: slideUp 1.4s ease-out;
        border-color: {border_color}; background-color: {card_bg};
        border-radius: 15px; transition: all 0.3s;
    }}
    [data-testid="stFileUploaderDropzone"]:hover {{ border-color: {button_color}; transform: scale(1.01); }}
    [data-testid="stFileUploaderDropzone"] div, [data-testid="stFileUploaderDropzone"] small {{ color: {text_color} !important; }}

    /* MAVİ BAŞLAT BUTONU */
    .stButton button[kind="primary"] {{
        animation: slideUp 1.6s ease-out;
        background-color: {button_color} !important;
        border-color: {button_color} !important;
        color: white !important;
        border-radius: 10px; transition: all 0.3s; font-weight: bold;
    }}
    .stButton button[kind="primary"]:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 20px {button_hover_glow};
    }}
    
    /* Gizlemeler */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- MODEL SEÇİMİ ---
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = next((m for m in models if 'flash' in m), models[0] if models else None)
        return genai.GenerativeModel(model_name) if model_name else None
    except: return None

model = get_model()

# --- ANA EKRAN ---
st.title("✨ TextHero Pro")
st.write("Profesyonel modunu seç, görseli yükle, analizi al.")
st.divider()

# 1. MOD SEÇİMİ (Yeni Profesyonel Emojiler)
option = st.selectbox(
    'Yapay Zeka Modu Seçin:',
    ('🧠 Detaylı Psikolojik Analiz', '💌 Romantik & Duygusal', '✨ Cool & Kısa', '🤝 Samimi & Doğal', '🎯 İğneleyici & Keskin')
)

# 2. DOSYA YÜKLEME
uploaded_file = st.file_uploader("Analiz edilecek görseli buraya bırak", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    # 3. MAVİ BAŞLAT BUTONU
    if st.button('✨ Analizi Başlat', type="primary"):
        if not model:
            st.error("Model bağlantısı başarısız. API Key ayarlarını kontrol et.")
        else:
            with st.spinner('TextHero profesyonel analiz yapıyor...'):
                try:
                    base_prompt = "Bu görseldeki duruma Türkçe cevap ver. ÖNEMLİ KURAL: Lafı uzatmadan önce direkt vermem gereken cevabı veya tepkiyi söyle, sonra açıklamasını yap."
                    
                    if 'Psikolojik' in option: prompt = base_prompt + " Durumu psikolojik açıdan detaylı analiz et, alt metinleri oku."
                    elif 'Romantik' in option: prompt = base_prompt + " Çok etkileyici, duygusal ve romantik bir dille yaz."
                    elif 'Cool' in option: prompt = base_prompt + " Çok kısa, net, umursamaz ve havalı ol."
                    elif 'Samimi' in option: prompt = base_prompt + " Çok doğal, samimi, arkadaşça bir dille yaz."
                    elif 'İğneleyici' in option: prompt = base_prompt + " Zekice laf sok, iğneleyici ve hedefi tam on ikiden vuran bir cevap yaz."
                    
                    response = model.generate_content([prompt, image])
                    
                    # Sonuç Kutusu (Mavi Gölgeli)
                    st.markdown(f"""
                    <div style="background-color: {card_bg}; padding: 20px; border-radius: 15px; border: 1px solid {border_color}; box-shadow: 0 5px 15px rgba(0,0,0,0.2); animation: slideUp 0.6s ease-out; backdrop-filter: blur(10px);">
                        <h3 style="margin-top:0; color:{text_color};">💡 TextHero Tavsiyesi:</h3>
                        <p style="font-size:1.1em; line-height:1.6; color:{text_color};">{response.text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

st.divider()
st.caption("Developed by Poyraz Dede © 2026")