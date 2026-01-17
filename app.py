import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- AYARLAR ---
st.set_page_config(
    page_title="TextHero Ultra", 
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

# --- TEMA, RENK VE ANİMASYON AYARLARI ---
# Kullanıcının görseline benzer, bulanık siyah-beyaz arka plan
bg_img_url = "https://images.unsplash.com/photo-1557682250-33bd709cbe85?q=80&w=2000&auto=format&fit=crop"

if theme_mode:
    overlay_color = "rgba(0, 0, 0, 0.7)" # Karanlık mod için kaplama
    bg_color, text_color, card_bg, border_color = "#0e1117", "#ffffff", "rgba(31, 34, 41, 0.8)", "rgba(255, 255, 255, 0.3)"
    button_hover_glow = "rgba(255,255,255,0.5)"
else:
    overlay_color = "rgba(255, 255, 255, 0.85)" # Aydınlık mod için kaplama
    bg_color, text_color, card_bg, border_color = "#ffffff", "#000000", "rgba(240, 242, 246, 0.8)", "rgba(0, 0, 0, 0.3)"
    button_hover_glow = "rgba(0,0,0,0.5)"

st.markdown(f"""
    <style>
    /* 1. Arka Plan ve Genel Stil */
    .stApp {{
        background: linear-gradient({overlay_color}, {overlay_color}), url("{bg_img_url}");
        background-size: cover; background-position: center; background-attachment: fixed;
        color: {text_color};
    }}
    .stTextInput, .stSelectbox, .stFileUploader {{ color: {text_color}; }}
    
    /* 2. Animasyon Tanımları */
    @keyframes slideUp {{ from {{ transform: translateY(20px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
    @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.02); }} 100% {{ transform: scale(1); }} }}

    /* 3. Elemanlara Animasyon ve Stil Uygulama */
    h1 {{ animation: slideUp 0.8s ease-out; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
    .stMarkdown p {{ animation: slideUp 1s ease-out; }}
    
    /* Mod Seçim Kutusu */
    .stSelectbox > div > div {{
        animation: slideUp 1.2s ease-out;
        transition: transform 0.3s, box-shadow 0.3s;
        border-radius: 10px;
    }}
    .stSelectbox > div > div:hover {{ transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }}

    /* Dosya Yükleme Alanı */
    [data-testid="stFileUploaderDropzone"] {{
        animation: slideUp 1.4s ease-out;
        border-color: {border_color}; background-color: {card_bg};
        border-radius: 15px; transition: all 0.3s;
    }}
    [data-testid="stFileUploaderDropzone"]:hover {{ border-color: {text_color}; transform: scale(1.01); }}
    [data-testid="stFileUploaderDropzone"] div, [data-testid="stFileUploaderDropzone"] small {{ color: {text_color} !important; }}

    /* Buton Efektleri */
    .stButton button {{
        animation: slideUp 1.6s ease-out;
        border-radius: 10px; transition: all 0.3s; font-weight: bold;
    }}
    .stButton button:hover {{
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
st.title("✨ TextHero")
st.write("Modunu seç, görseli yükle, cevabı al.")
st.divider()

# 1. MOD SEÇİMİ (En Başta)
option = st.selectbox(
    'Yapay Zeka Modu Seçin:',
    ('🔍 Detaylı Analiz', '❤️ Romantik & Etkileyici', '😎 Cool & Esprili', '👊 Kanka Modu', '🔥 Laf Sokucu')
)

# 2. DOSYA YÜKLEME
uploaded_file = st.file_uploader("Analiz edilecek görseli buraya bırak", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    # 3. BAŞLAT BUTONU
    if st.button('✨ Analizi Başlat', type="primary"):
        if not model:
            st.error("Model bağlantısı başarısız. API Key ayarlarını kontrol et.")
        else:
            with st.spinner('TextHero cevabı hazırlıyor...'):
                try:
                    base_prompt = "Bu görseldeki duruma Türkçe cevap ver. ÖNEMLİ: Önce direkt verilmesi gereken cevabı söyle, sonra açıklama yap."
                    if 'Detaylı' in option: prompt = base_prompt + " Psikolojik analiz yap."
                    elif 'Romantik' in option: prompt = base_prompt + " Çok etkileyici ve romantik ol."
                    elif 'Cool' in option: prompt = base_prompt + " Kısa, havalı ve gizemli ol."
                    elif 'Kanka' in option: prompt = base_prompt + " Samimi, kanka ağzıyla konuş."
                    elif 'Laf Sokucu' in option: prompt = base_prompt + " İğneleyici konuş, laf sok."
                    
                    response = model.generate_content([prompt, image])
                    
                    # Sonuç Kutusu (Animasyonlu)
                    st.markdown(f"""
                    <div style="background-color: {card_bg}; padding: 20px; border-radius: 15px; border: 1px solid {border_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); animation: slideUp 0.6s ease-out; backdrop-filter: blur(5px);">
                        <h3 style="margin-top:0; color:{text_color};">💡 TextHero Tavsiyesi:</h3>
                        <p style="font-size:1.1em; line-height:1.6; color:{text_color};">{response.text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

st.divider()
st.caption("Developed by Poyraz Dede © 2026")