import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime

# --- AYARLAR ---
st.set_page_config(
    page_title="TextHero Pro", 
    page_icon="✨", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- GÜVENLİK: API ANAHTARINI GİZLİ KASADAN AL ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit panelinden 'Secrets' kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

# --- SESSION STATE (GEÇMİŞ & SIFIRLAMA İÇİN) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# --- SOL MENÜ (AYARLAR & GEÇMİŞ) ---
with st.sidebar:
    st.title("⚙️ Panel")
    
    # 1. Tema Ayarı
    theme_mode = st.toggle("🌙 Karanlık Mod", value=True)
    st.caption("Arka plan sabit kalır, kutular değişir.")
    
    st.divider()
    
    # 2. GEÇMİŞ BÖLÜMÜ
    st.subheader("📜 Geçmiş Analizler")
    if st.session_state.history:
        if st.button("🗑️ Geçmişi Temizle"):
            st.session_state.history = []
            st.rerun()
        
        # Geçmişi tersten yazdır (en yeni en üstte)
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{item['time']} - {item['mode']}"):
                st.write(item['text'])
    else:
        st.info("Henüz analiz yapılmadı.")
        
    st.divider()
    st.caption("Developed by Poyraz Dede © 2026")

# --- TEMA VE RENK TANIMLARI ---
# Arka plan her iki modda da AYNI (Koyu Gradient)
fixed_bg_gradient = "linear-gradient(to bottom right, #000000 50%, #1a1d24 100%)"

if theme_mode:
    # --- KARANLIK MOD ---
    text_color = "#ffffff"
    card_bg = "rgba(31, 34, 41, 0.9)"
    border_color = "rgba(255, 255, 255, 0.2)"
    uploader_bg = "rgba(31, 34, 41, 0.9)"
    uploader_border = "rgba(255, 255, 255, 0.2)"
    uploader_text_color = "#ffffff" # Koyu modda yazılar beyaz
    title_color = "#ffffff" 
else:
    # --- BEYAZ (LIGHT) MOD ---
    text_color = "#000000" 
    card_bg = "rgba(255, 255, 255, 0.95)" 
    border_color = "rgba(0, 0, 0, 0.2)"
    uploader_bg = "rgba(255, 255, 255, 0.95)" 
    uploader_border = "rgba(0, 0, 0, 0.3)"
    uploader_text_color = "#000000 !important" # ZORLA SİYAH YAP (Düzeltme Burası)
    title_color = "#ffffff" 

# --- CSS İLE TASARIM ---
st.markdown(f"""
    <style>
    /* 1. Arka Plan (SABİT) */
    .stApp {{
        background: {fixed_bg_gradient};
        background-attachment: fixed;
        color: {title_color};
    }}
    
    /* 2. Kartlar ve Kutular */
    .stSelectbox > div > div {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color};
    }}
    .stSelectbox div[data-baseweb="select"] > div {{
        color: {text_color} !important;
    }}

    /* 3. Dosya Yükleme Alanı (RENK DÜZELTMESİ) */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {uploader_bg};
        border-color: {uploader_border};
        border-radius: 15px;
    }}
    /* Dosya yükleme kutusunun içindeki TÜM yazıları hedefle */
    [data-testid="stFileUploaderDropzone"] div, 
    [data-testid="stFileUploaderDropzone"] span, 
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] p {{ 
        color: {uploader_text_color}; 
    }}
    
    /* 4. Başlık Butonu (TextHero Pro) */
    .reset-btn {{
        background: none!important;
        border: none;
        padding: 0!important;
        color: {title_color} !important;
        text-decoration: none;
        cursor: pointer;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    .reset-btn:hover {{
        opacity: 0.8;
    }}
    
    /* Animasyonlar */
    @keyframes slideUp {{ from {{ transform: translateY(20px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
    .element-anim {{ animation: slideUp 0.8s ease-out; }}
    
    /* MAVİ BUTON */
    .stButton button[kind="primary"] {{
        background-color: #0d6efd !important;
        border-color: #0d6efd !important;
        color: white !important;
        border-radius: 10px; font-weight: bold;
        transition: all 0.3s;
    }}
    .stButton button[kind="primary"]:hover {{
        transform: scale(1.05); box-shadow: 0 0 15px rgba(13, 110, 253, 0.6);
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

# BAŞLIK (RESET FONKSİYONU)
# Streamlit'te başlığa tıklandığında sayfayı yenilemek için özel bir buton yapısı
col1, col2 = st.columns([0.8, 0.2])
with col1:
    if st.button("✨ TextHero Pro", key="home_btn", help="Yeni işlem için tıkla"):
        # Uploader key'i değiştirerek dosya yükleyiciyi sıfırla
        st.session_state.uploader_key += 1
        st.rerun()

st.write("Profesyonel modunu seç, görseli yükle, analizi al.")
st.divider()

# 1. MOD SEÇİMİ
option = st.selectbox(
    'Yapay Zeka Modu Seçin:',
    ('🧠 Detaylı Psikolojik Analiz', '💌 Romantik & Duygusal', '✨ Cool & Kısa', '🤝 Samimi & Doğal', '🎯 İğneleyici & Keskin')
)

# 2. DOSYA YÜKLEME (Key ile sıfırlanabilir yapıldı)
uploaded_file = st.file_uploader(
    "Analiz edilecek görseli buraya bırak", 
    type=["jpg", "png", "jpeg"], 
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    # 3. BAŞLAT BUTONU
    if st.button('✨ Analizi Başlat', type="primary"):
        if not model:
            st.error("Model bağlantısı başarısız. API Key ayarlarını kontrol et.")
        else:
            with st.spinner('TextHero profesyonel analiz yapıyor...'):
                try:
                    base_prompt = "Bu görseldeki duruma Türkçe cevap ver. ÖNEMLİ KURAL: Lafı uzatmadan önce direkt vermem gereken cevabı veya tepkiyi söyle, sonra açıklamasını yap."
                    
                    if 'Psikolojik' in option: prompt = base_prompt + " Durumu psikolojik açıdan detaylı analiz et."
                    elif 'Romantik' in option: prompt = base_prompt + " Çok etkileyici, duygusal ve romantik bir dille yaz."
                    elif 'Cool' in option: prompt = base_prompt + " Çok kısa, net, umursamaz ve havalı ol."
                    elif 'Samimi' in option: prompt = base_prompt + " Çok doğal, samimi, arkadaşça bir dille yaz."
                    elif 'İğneleyici' in option: prompt = base_prompt + " Zekice laf sok, iğneleyici ve hedefi tam on ikiden vuran bir cevap yaz."
                    
                    response = model.generate_content([prompt, image])
                    
                    # --- GEÇMİŞE EKLEME ---
                    timestamp = datetime.datetime.now().strftime("%H:%M")
                    st.session_state.history.append({
                        "time": timestamp,
                        "mode": option,
                        "text": response.text
                    })

                    # --- SONUÇ KUTUSU ---
                    st.markdown(f"""
                    <div style="background-color: {card_bg}; padding: 20px; border-radius: 15px; border: 1px solid {border_color}; box-shadow: 0 5px 15px rgba(0,0,0,0.2); animation: slideUp 0.6s ease-out; backdrop-filter: blur(10px);">
                        <h3 style="margin-top:0; color:{text_color};">💡 TextHero Tavsiyesi:</h3>
                        <p style="font-size:1.1em; line-height:1.6; color:{text_color};">{response.text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")