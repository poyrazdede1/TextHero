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

# --- SOL MENÜ (KONTROL PANELİ) ---
with st.sidebar:
    st.title("⚙️ Panel")
    
    # 1. Tema Seçeneği
    theme_mode = st.toggle("🌙 Karanlık Mod", value=True)
    
    st.divider() # Çizgi
    
    # 2. Yanıt Tarzı Seçimi
    option = st.selectbox(
        'Yapay Zeka Modu',
        ('Detaylı Analiz', 'Romantik & Etkileyici', 'Cool & Esprili', 'Kanka Modu', 'Laf Sokucu')
    )
    
    st.info("💡 Modu buradan değiştirebilirsin.")

# --- TEMA RENKLERİ ---
if theme_mode:
    bg_color = "#0e1117"
    text_color = "white"
    card_bg = "#1f2229"
else:
    bg_color = "#ffffff"
    text_color = "black"
    card_bg = "#f0f2f6"

# CSS (Menü tuşunu geri getirdik!)
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    /* Sadece "Deploy" ve gereksiz footer yazılarını gizle, ama Üst Çubuğu (Header) KORU */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    /* header {{visibility: hidden;}}  <-- BURAYI İPTAL ETTİK Kİ MENÜ GELSİN */
    
    .stTextInput, .stSelectbox, .stFileUploader {{
        color: {text_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- MODEL SEÇİCİ ---
def get_auto_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        chosen_model = next((m for m in available_models if 'flash' in m), None)
        if not chosen_model:
            chosen_model = next((m for m in available_models if 'vision' in m), None)
        if not chosen_model:
            chosen_model = available_models[0] if available_models else None

        return genai.GenerativeModel(chosen_model) if chosen_model else None, chosen_model

    except Exception as e:
        return None, str(e)

model, model_status = get_auto_model()

# --- ANA EKRAN ---
st.title("TextHero")
st.write("Görseli yükle, gerisini yapay zekaya bırak.")

# Dosya Yükleme
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    if st.button('✨ Analizi Başlat', type="primary"):
        if not model:
            st.error("Model bağlantı hatası.")
        else:
            with st.spinner('TextHero düşünüyor...'):
                try:
                    prompt = "Bu görseldeki duruma Türkçe cevap ver."
                    if 'Detaylı' in option: prompt += " Detaylı analiz et."
                    elif 'Romantik' in option: prompt += " Romantik ve etkileyici ol."
                    elif 'Cool' in option: prompt += " Cool, kısa ve havalı ol."
                    elif 'Kanka' in option: prompt += " Samimi ve arkadaşça ol."
                    elif 'Laf Sokucu' in option: prompt += " İğneleyici ve kapak edici ol."
                    
                    response = model.generate_content([prompt, image])
                    
                    st.markdown(f"""
                    <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; color: {text_color}; border: 1px solid rgba(128, 128, 128, 0.2);">
                        <h4>💡 TextHero Tavsiyesi:</h4>
                        <p>{response.text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Hata: {e}")

# --- ALT BİLGİ (FOOTER) ---
st.divider()
st.caption("Developed by Poyraz Dede © 2026")