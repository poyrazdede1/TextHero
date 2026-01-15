import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- AYARLAR & KONFİGÜRASYON ---
API_KEY = "AIzaSyA89yPg93ZrDYh5FkweAPfBL2Dqg19uC4s"

# Sayfa Ayarları (Sekme ismi, ikon ve genişlik)
st.set_page_config(
    page_title="TextHero - Poyraz Edition",
    page_icon="🔥",
    layout="centered"
)

# Gemini Kurulumu
genai.configure(api_key=API_KEY)

# --- MODEL BULUCU FONKSİYON ---
def get_auto_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            return None, "Hiç model bulunamadı."

        # Öncelik sırası: Flash -> Vision -> İlk bulduğu
        chosen = next((m for m in available_models if 'flash' in m), None)
        if not chosen:
            chosen = next((m for m in available_models if 'vision' in m), None)
        if not chosen:
            chosen = available_models[0]

        return genai.GenerativeModel(chosen), chosen

    except Exception as e:
        return None, str(e)

model, model_status = get_auto_model()

# --- YAN MENÜ (SIDEBAR) TASARIMI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=100)
    st.title("⚙️ Kontrol Paneli")
    
    # Mod Seçimi Yan Tarafta
    st.write("Hangi modda cevap istersin?")
    option = st.selectbox(
        'Mod Seç:',
        ('Durum Analizi 🧐', 'Romantik / Flört 🌹', 'Cool / Komik 😎', 'Arkadaşça / Kanka 👊', 'Laf Sok / Kapak Yap 💥')
    )
    
    st.markdown("---")
    # YAN MENÜ İMZASI
    st.markdown("### 👨‍💻 Developer")
    st.info("**Poyraz Dede** tarafından geliştirildi.")
    st.caption("© 2026 TextHero | v2.0")

# --- ANA EKRAN TASARIMI ---
st.title("🦸‍♂️ TextHero")
st.markdown("**Mesajlaşırken tıkandın mı? Ekran görüntüsünü at, gerisini bana bırak.**")

if not model:
    st.error(f"❌ Bağlantı Hatası: {model_status}")
else:
    # Model ismini gizli tutalım, sadece çalıştığını bilsinler
    st.success("✅ Yapay Zeka Sistemi Aktif")

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Ekran görüntüsünü buraya sürükle...", type=["jpg", "png", "jpeg"])

# --- İŞLEM ---
if uploaded_file is not None:
    # Resmi göster
    image = Image.open(uploaded_file)
    st.image(image, caption='Analiz Edilecek Görsel', use_column_width=True)
    
    # Butonu daha belirgin yapalım
    if st.button('🔥 Sihri Başlat ve Cevapla', type="primary"):
        with st.spinner('Yapay zeka en iyi cevabı düşünüyor...'):
            try:
                # Prompt hazırlama
                prompt = "Bu görseldeki mesajlaşmaya Türkçe cevap ver."
                if 'Analiz' in option: prompt += " Durumu analiz et, kim ne demek istemiş özetle."
                elif 'Romantik' in option: prompt += " Karşı tarafı etkileyecek, romantik ve 'Rizz' dolu 3 farklı cevap önerisi yaz."
                elif 'Cool' in option: prompt += " Çok kasmayan, havalı, esprili ve cool 3 cevap önerisi yaz."
                elif 'Arkadaşça' in option: prompt += " Bir arkadaşa yazılabilecek samimi, doğal 3 cevap önerisi sun."
                elif 'Laf Sok' in option: prompt += " Taşı gediğine koyacak, laf sokan, kapak eden 3 cevap yaz."
                
                response = model.generate_content([prompt, image])
                
                st.markdown("---")
                st.subheader("💡 Tavsiyelerim:")
                st.markdown(response.text)
                st.balloons() # Konfeti patlatır!
                
            except Exception as e:
                st.error(f"Bir şeyler ters gitti: {e}")

# --- ALT BİLGİ (FOOTER) ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: grey;'>
    Made with by <b>Poyraz Dede</b> | İstanbul, 2026
    </div>
    """, 
    unsafe_allow_html=True
)