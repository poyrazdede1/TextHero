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

# --- GÜVENLİK ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit panelinden 'Secrets' kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

# --- SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# --- SOL MENÜ ---
with st.sidebar:
    st.title("⚙️ Panel")
    theme_mode = st.toggle("🌙 Karanlık Mod", value=True)
    st.caption("Arka plan sabit kalır, kutular değişir.")
    st.divider()
    
    st.subheader("📜 Geçmiş Analizler")
    if st.session_state.history:
        # Bu buton bozulmaz, çünkü CSS sadece ana ekranı hedefliyor
        if st.button("🗑️ Geçmişi Temizle"):
            st.session_state.history = []
            st.rerun()
        
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{item['time']} - {item['mode']}"):
                st.write(item['text'])
    else:
        st.info("Henüz analiz yapılmadı.")
    st.divider()
    st.caption("Developed by Poyraz Dede © 2026")

# --- RENK TANIMLARI ---
fixed_bg_gradient = "linear-gradient(to bottom right, #000000 50%, #1a1d24 100%)"

if theme_mode:
    # --- KARANLIK MOD ---
    text_color = "#ffffff"
    card_bg = "rgba(31, 34, 41, 0.9)"
    border_color = "rgba(255, 255, 255, 0.2)"
    uploader_bg = "rgba(31, 34, 41, 0.9)"
    uploader_border = "rgba(255, 255, 255, 0.2)"
    uploader_text_color = "#ffffff"
    title_color = "#ffffff" 
else:
    # --- BEYAZ MOD ---
    text_color = "#000000" 
    card_bg = "rgba(255, 255, 255, 0.95)" 
    border_color = "rgba(0, 0, 0, 0.2)"
    uploader_bg = "rgba(255, 255, 255, 0.95)" 
    uploader_border = "rgba(0, 0, 0, 0.3)"
    uploader_text_color = "#000000 !important"
    title_color = "#ffffff" 

# --- CSS SİHİRBAZLIĞI ---
st.markdown(f"""
    <style>
    .stApp {{
        background: {fixed_bg_gradient};
        background-attachment: fixed;
        color: {title_color};
    }}
    
    .stSelectbox > div > div {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color};
    }}
    .stSelectbox div[data-baseweb="select"] > div {{ color: {text_color} !important; }}

    [data-testid="stFileUploaderDropzone"] {{
        background-color: {uploader_bg};
        border-color: {uploader_border};
        border-radius: 15px;
    }}
    [data-testid="stFileUploaderDropzone"] div, 
    [data-testid="stFileUploaderDropzone"] span, 
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] p {{ color: {uploader_text_color}; }}
    
    /* --- GİZLİ BAŞLIK BUTONU AYARI --- */
    /* Sadece ana ekrandaki (stMain) birincil olmayan butonları hedefler */
    [data-testid="stMain"] .stButton button:not([kind="primary"]) {{
        background-color: transparent !important;
        border: none !important;
        color: {title_color} !important;
        font-size: 3rem !important; /* H1 Başlık Boyutu */
        font-weight: 700 !important;
        padding: 0 !important;
        text-align: left !important;
        box-shadow: none !important;
        display: block !important;
        width: 100%;
        margin-bottom: 0px !important;
    }}
    /* Üzerine gelince (Hover) hafif parlasın ki tıklanabilir olduğu hissedilsin */
    [data-testid="stMain"] .stButton button:not([kind="primary"]):hover {{
        color: #e0e0e0 !important;
        background-color: transparent !important;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }}
    /* Tıklanınca (Active) */
    [data-testid="stMain"] .stButton button:not([kind="primary"]):active,
    [data-testid="stMain"] .stButton button:not([kind="primary"]):focus {{
        background-color: transparent !important;
        border: none !important;
        color: {title_color} !important;
        box-shadow: none !important;
    }}

    /* MAVİ BAŞLAT BUTONU */
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

# 1. GİZLİ BAŞLIK BUTONU
# Kullanıcı bunu sadece "TextHero Pro" yazısı sanacak ama aslında bir buton
if st.button("✨ TextHero Pro", key="home_btn", help="Ekranı temizlemek için tıkla"):
    st.session_state.uploader_key += 1
    st.rerun()

st.write("Profesyonel modunu seç, görseli yükle, analizi al.")
st.divider()

# 2. MOD SEÇİMİ
option = st.selectbox(
    'Yapay Zeka Modu Seçin:',
    ('🧠 Detaylı Psikolojik Analiz', '💌 Romantik & Duygusal', '✨ Cool & Kısa', '🤝 Samimi & Doğal', '🎯 İğneleyici & Keskin')
)

# 3. DOSYA YÜKLEME
uploaded_file = st.file_uploader(
    "Analiz edilecek görseli buraya bırak", 
    type=["jpg", "png", "jpeg"], 
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    # 4. BAŞLAT BUTONU
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
                    
                    # --- GEÇMİŞE KAYDET ---
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