import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- AYARLAR ---
# Buraya kendi API Key'ini yapıştır
API_KEY = "AIzaSyA89yPg93ZrDYh5FkweAPfBL2Dqg19uC4s"

# Sayfa Ayarları (Apple/Google Tarzı Sade Başlık)
st.set_page_config(
    page_title="AI Asistan", 
    page_icon="✨", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Gemini Kurulumu
genai.configure(api_key=API_KEY)

# --- CSS İLE TASARIM MAKYAJI ---
# Bu kısım o tepedeki renkli çizgileri ve "Deploy" butonunu gizler, daha temiz görünür.
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {background-color: #0e1117;} 
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- AKILLI MODEL SEÇİCİ (Arkada Çalışan Beyin) ---
def get_auto_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            return None, "Model bulunamadı."

        # Öncelik sırası: Flash -> Vision -> İlk Bulunan
        chosen_model = next((m for m in available_models if 'flash' in m), None)
        if not chosen_model:
            chosen_model = next((m for m in available_models if 'vision' in m), None)
        if not chosen_model:
            chosen_model = available_models[0]

        return genai.GenerativeModel(chosen_model), chosen_model

    except Exception as e:
        return None, str(e)

model, model_status = get_auto_model()

# --- ARAYÜZ TASARIMI ---
# Google Gemini gibi sadece başlık ve alt açıklama
st.title("✨ AI Görsel Analiz")
st.caption("Gelişmiş yapay zeka destekli mesaj ve durum analiz sistemi.")

st.divider() # İnce, şık bir çizgi

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Analiz edilecek görseli seçin", type=["jpg", "png", "jpeg"])

# Mod Seçimi (Daha kurumsal isimler)
option = st.selectbox(
    'Yanıt Tarzı Seçin',
    ('Detaylı Durum Analizi', 'Etkileyici & Romantik', 'Cool & Esprili', 'Samimi & Arkadaşça', 'Eleştirel & İğneleyici')
)

# --- İŞLEM ---
if uploaded_file is not None:
    # Resmi göster (Kenarları yuvarlatılmış gibi temiz durur)
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    
    # Butonu biraz daha şık yapalım
    if st.button('Analizi Başlat', type="primary"):
        if not model:
            st.error("Bağlantı hatası: Model bulunamadı.")
        else:
            with st.spinner('Yapay zeka yanıtı oluşturuyor...'):
                try:
                    prompt = "Bu görseldeki mesajlaşmaya veya duruma Türkçe cevap ver."
                    if 'Detaylı' in option: prompt += " Olayı detaylıca analiz et, psikolojik çıkarımlar yap."
                    elif 'Romantik' in option: prompt += " Çok etkileyici, romantik ve duygusal bir cevap yaz."
                    elif 'Cool' in option: prompt += " Umursamaz, havalı ve kısa bir cevap yaz."
                    elif 'Arkadaşça' in option: prompt += " Çok samimi, kanka tarzı doğal bir cevap yaz."
                    elif 'Eleştirel' in option: prompt += " Zekice laf sokan, iğneleyici bir cevap yaz."
                    
                    response = model.generate_content([prompt, image])
                    
                    st.markdown("### 💡 AI Önerisi")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")