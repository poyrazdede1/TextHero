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
    initial_sidebar_state="collapsed"
)

# Gemini Kurulumu
genai.configure(api_key=API_KEY)

# --- SOL MENÜ (AYARLAR) ---
with st.sidebar:
    st.title("⚙️ Ayarlar")
    # Tema Seçeneği
    theme_mode = st.toggle("🌙 Karanlık Mod", value=True)
    st.info("Mod seçimini kolay olsun diye ana ekrana taşıdık! 👉")
    st.divider()
    st.caption("Developed by Poyraz Dede")

# --- TEMA & RENK AYARLARI (SİYAH/BEYAZ DÖNÜŞÜ) ---
if theme_mode:
    # Karanlık Mod (Dark)
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "#1f2229"
    uploader_border = "rgba(255, 255, 255, 0.3)" 
else:
    # Aydınlık Mod (Light)
    bg_color = "#ffffff"
    text_color = "#000000"
    card_bg = "#f0f2f6"
    uploader_border = "rgba(0, 0, 0, 0.3)" 

# --- CSS İLE TASARIM ---
st.markdown(f"""
    <style>
    /* Genel Arka Plan */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Inputlar ve Menüler */
    .stTextInput, .stSelectbox, .stFileUploader, .stButton {{
        color: {text_color};
    }}

    /* Dosya Yükleme Alanı */
    [data-testid="stFileUploaderDropzone"] {{
        border-color: {uploader_border};
        color: {text_color};
        background-color: {card_bg};
    }}
    [data-testid="stFileUploaderDropzone"] div, [data-testid="stFileUploaderDropzone"] small {{
        color: {text_color} !important;
    }}
    
    /* Gereksiz Footer Gizleme */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
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
st.write("Görseli yükle, modunu seç, cevabı al.")

# 1. Dosya Yükleme
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    # Görseli biraz küçülterek gösterelim ki cevap yukarıda kalsın
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    st.divider()

    # 2. Mod Seçimi (ANA EKRANDA VE EMOJİLİ)
    option = st.selectbox(
        'Yapay Zeka Modu Seçin:',
        ('🔍 Detaylı Analiz', '❤️ Romantik & Etkileyici', '😎 Cool & Esprili', '👊 Kanka Modu', '🔥 Laf Sokucu')
    )

    # 3. Başlat Butonu
    if st.button('✨ Analizi Başlat', type="primary"):
        if not model:
            st.error("Model bağlantısı kurulamadı.")
        else:
            with st.spinner('TextHero cevabı hazırlıyor...'):
                try:
                    # Prompt Ayarı: "Önce Cevap" kuralı eklendi
                    base_prompt = "Bu görseldeki mesajlaşmaya veya duruma Türkçe cevap ver. ÖNEMLİ KURAL: Lafı uzatmadan önce direkt vermem gereken cevabı veya tepkiyi söyle, sonra açıklamasını yap."
                    
                    if 'Detaylı' in option: prompt = base_prompt + " Durumu psikolojik olarak detaylı analiz et."
                    elif 'Romantik' in option: prompt = base_prompt + " Çok etkileyici, şairane ve romantik ol."
                    elif 'Cool' in option: prompt = base_prompt + " Çok kısa, umursamaz, havalı ve gizemli ol."
                    elif 'Kanka' in option: prompt = base_prompt + " Çok samimi, sokak ağzıyla, kanka gibi konuş."
                    elif 'Laf Sokucu' in option: prompt = base_prompt + " Zekice laf sok, iğneleyici ve kapak edici ol."
                    
                    response = model.generate_content([prompt, image])
                    
                    # Sonuç Kutusu
                    st.markdown(f"""
                    <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; color: {text_color}; border: 1px solid {uploader_border}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h3 style="margin-top:0;">💡 TextHero Tavsiyesi:</h3>
                        <p style="font-size:1.1em; line-height:1.6;">{response.text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

# --- İMZA ---
st.divider()
st.caption("Developed by Poyraz Dede © 2026")