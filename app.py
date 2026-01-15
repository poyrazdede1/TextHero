import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- AYARLAR ---
API_KEY = "AIzaSyA89yPg93ZrDYh5FkweAPfBL2Dqg19uC4s"

st.set_page_config(page_title="TextHero", page_icon="🦸‍♂️")
genai.configure(api_key=API_KEY)

# --- AKILLI MODEL BULUCU ---
# Bu fonksiyon, Google'dan senin hesabına tanımlı modelleri ister
# ve içlerinden resim okuyabilen (vision) İLK modeli seçer.
def get_auto_model():
    try:
        # Hesabındaki tüm modelleri listele
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Eğer liste boşsa
        if not available_models:
            return None, "Listenizde hiç model bulunamadı."

        # Öncelik: Adında 'flash' geçen en yeni model
        chosen_model_name = next((m for m in available_models if 'flash' in m), None)
        
        # Flash yoksa, adında 'vision' geçen modele bak
        if not chosen_model_name:
            chosen_model_name = next((m for m in available_models if 'vision' in m), None)
            
        # O da yoksa listenin ilkini al (Son çare)
        if not chosen_model_name:
            chosen_model_name = available_models[0]

        return genai.GenerativeModel(chosen_model_name), chosen_model_name

    except Exception as e:
        return None, str(e)

# Modeli başlat
model, model_status = get_auto_model()

# --- ARAYÜZ ---
st.title("🦸‍♂️ TextHero")

# Durum Bilgilendirmesi (Hangi model bulundu?)
if model:
    st.caption(f"✅ Bağlanılan Model: {model_status}")
else:
    st.error(f"❌ Model Bulunamadı Hata: {model_status}")

st.write("Ekran görüntüsünü yükle, gerisini bana bırak.")

uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])

option = st.selectbox(
    'Mod Seç:',
    ('Analiz Et', 'Romantik', 'Cool/Komik', 'Arkadasca', 'Laf Sok')
)

# --- İŞLEM ---
if uploaded_file is not None and st.button('Cevapla 🚀'):
    if not model:
        st.error("Çalışan bir model bulunamadığı için işlem yapılamıyor.")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption='Görsel', use_column_width=True)
        
        with st.spinner('Yapay zeka düşünüyor...'):
            try:
                # Prompt
                prompt = "Bu görseldeki mesajlaşmaya Türkçe cevap ver."
                if 'Analiz' in option: prompt += " Durumu analiz et."
                elif 'Romantik' in option: prompt += " Romantik ve etkileyici 3 cevap yaz."
                elif 'Cool' in option: prompt += " Cool ve komik 3 cevap yaz."
                elif 'Arkadasca' in option: prompt += " Arkadaşça 3 cevap yaz."
                elif 'Laf Sok' in option: prompt += " Kapak edecek, iğneleyici 3 cevap yaz."
                
                response = model.generate_content([prompt, image])
                st.success("Tavsiyeler:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Beklenmedik bir hata: {e}")