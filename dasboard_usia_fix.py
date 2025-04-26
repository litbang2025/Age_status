import streamlit as st
from fpdf import FPDF
from datetime import datetime
import qrcode
from PIL import Image
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt

# -------------------------------
# Fungsi: Hitung Berat Ideal (Indeks Broca)
# -------------------------------
def hitung_berat_ideal(tinggi_cm, jenis_kelamin):
    if tinggi_cm <= 0:
        return 0
    dasar = tinggi_cm - 100
    if jenis_kelamin == "Laki-laki":
        return dasar - (0.10 * dasar)
    else:
        return dasar - (0.15 * dasar)

# -------------------------------
# Fungsi: Hitung IMT dan Kategori
# -------------------------------
def hitung_imt(berat, tinggi_cm):
    if tinggi_cm == 0:
        return 0, "Tidak Valid"
    tinggi_m = tinggi_cm / 100
    imt = berat / (tinggi_m ** 2)
    if imt < 14:
        kategori = "Sangat Kurus"
    elif imt < 17:
        kategori = "Kurus"
    elif imt < 20:
        kategori = "Normal"
    elif imt < 25:
        kategori = "Berlebih"
    else:
        kategori = "Obesitas"
    return imt, kategori

# -------------------------------
# Fungsi: Saran berdasarkan perbandingan
# -------------------------------
def saran_perbandingan(berat, berat_ideal, tinggi, tinggi_ideal):
    def banding(nilai, ideal):
        if abs(nilai - ideal) < 1.0:
            return "ideal"
        elif nilai < ideal:
            return "kurang"
        else:
            return "berlebih"

    status_berat = banding(berat, berat_ideal)
    status_tinggi = banding(tinggi, tinggi_ideal)
    return status_berat, status_tinggi

# -------------------------------
# Fungsi: Membuat PDF Sertifikat
# -------------------------------
def buat_pdf(nama, usia, berat, tinggi, berat_ideal, status_berat, status_tinggi):
    # Buat QR Code (misal link ke situs app atau ID unik)
    qr_data = f"Nama: {nama}, Usia: {usia}, Berat: {berat}, Tinggi: {tinggi}"
    qr_img = qrcode.make(qr_data)
    qr_path = "qr_temp.png"
    qr_img.save(qr_path)

    # PDF
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "SERTIFIKAT PERKEMBANGAN ANAK", ln=True, align='C')
    pdf.ln(5)
    pdf.set_line_width(0.5)
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)

    # Isi
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 8, f"""
Dengan ini menyatakan bahwa:

Nama              : {nama}
Usia              : {usia} tahun
Berat Badan       : {berat} kg
Tinggi Badan      : {tinggi} cm

Berat ideal berdasarkan Indeks Broca adalah {berat_ideal:.2f} kg.

Status Berat      : {status_berat}
Status Tinggi     : {status_tinggi}
""")

    # Tanggal
    tanggal = datetime.today().strftime('%d %B %Y')
    pdf.ln(10)
    pdf.cell(0, 10, f"Diterbitkan pada: {tanggal}", ln=True)

    # Tanda tangan
    pdf.ln(15)
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 6, "________________________", ln=True, align='R')
    pdf.cell(0, 6, "Berbagi itu indah", ln=True, align='R')

    # Tambahkan QR Code
    pdf.image(qr_path, x=10, y=230, w=30)

    # Simpan
    pdf.output("hasil_perkembangan.pdf")

# -------------------------
# Konfigurasi halaman
# -------------------------
st.set_page_config(page_title="Kalkulator Perkembangan Anak", layout="centered", page_icon="🧒")

# -------------------------------
# Sidebar Navigasi
# -------------------------------
with st.sidebar:
    selected = option_menu(
        "Navigasi",
        ["Kalkulator", "Grafik", "IMT", "Saran Gizi", "Tentang"],
        icons=["calculator", "bar-chart-line", "activity", "emoji-smile", "info-circle"],
        menu_icon="heart-fill",
        default_index=0
    )

# -------------------------------
# Halaman: Kalkulator
# -------------------------------
if selected == "Kalkulator":
    st.markdown("""<h2 style='text-align: center; color: #4CAF50;'>📏 Kalkulator Perkembangan Anak</h2>""", unsafe_allow_html=True)
    st.text("Masukkan data anak Anda, dan dapatkan hasil berat & tinggi ideal lengkap dengan rekomendasi!")

    nama = st.text_input("👤 Nama Anak")
    usia = st.number_input("📅 Usia Anak (tahun)", 5, 60, 5)
    jenis_kelamin = st.selectbox("⚧️ Jenis Kelamin", ["Laki-laki", "Perempuan"])
    berat = st.number_input("⚖️ Berat Badan (kg)", 0.0, 100.0, 25.0)
    tinggi = st.number_input("📏 Tinggi Badan (cm)", 0.0, 200.0, 150.0)

    if st.button("🔍 Cek Ideal"):
        berat_ideal = hitung_berat_ideal(tinggi, jenis_kelamin)
        tinggi_ideal = tinggi
        status_berat, status_tinggi = saran_perbandingan(berat, berat_ideal, tinggi, tinggi_ideal)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("Berat Ideal", f"{berat_ideal:.2f} kg", f"{berat - berat_ideal:+.2f} kg")
        with col2:
            st.metric("Tinggi Sekarang", f"{tinggi:.1f} cm")
        st.subheader("📝 Kesimpulan")
        st.markdown(f"**{nama}**, usia **{usia} tahun**, memiliki berat badan **{status_berat}** dan tinggi badan **{status_tinggi}** dibandingkan dengan nilai ideal berdasarkan Indeks Broca.")
        st.session_state.hasil_input = {"nama": nama, "usia": usia, "berat": berat, "tinggi": tinggi, "jenis_kelamin": jenis_kelamin, "berat_ideal": berat_ideal}
        
    if "hasil_input" in st.session_state:
        buat_pdf(
            st.session_state.hasil_input["nama"],
            st.session_state.hasil_input["usia"],
            st.session_state.hasil_input["berat"],
            st.session_state.hasil_input["tinggi"],
            st.session_state.hasil_input["berat_ideal"],
            saran_perbandingan(
                st.session_state.hasil_input["berat"],
                st.session_state.hasil_input["berat_ideal"],
                st.session_state.hasil_input["tinggi"],
                st.session_state.hasil_input["tinggi"]
            )[0],
            saran_perbandingan(
                st.session_state.hasil_input["berat"],
                st.session_state.hasil_input["berat_ideal"],
                st.session_state.hasil_input["tinggi"],
                st.session_state.hasil_input["tinggi"]
            )[1]
        )
        with open("hasil_perkembangan.pdf", "rb") as f:
            st.download_button(
                label="🔽 Unduh Sertifikat PDF",
                data=f,
                file_name="hasil_perkembangan.pdf",
                mime="application/pdf"
            )

# -------------------------------
# Halaman: Grafik
# -------------------------------
elif selected == "Grafik":
    st.title("📊 Grafik Perbandingan Berat Anak")
    if "hasil_input" in st.session_state:
        hasil = st.session_state.hasil_input
        x = ["Ideal", "Anak"]
        y = [hasil["berat_ideal"], hasil["berat"]]
        fig, ax = plt.subplots()
        ax.bar(x, y, color=["#90caf9", "#f06292"])
        ax.set_ylabel("Berat Badan (kg)")
        ax.set_title(f"Perbandingan Berat Badan: {hasil['nama']}")
        st.pyplot(fig)
    else:
        st.warning("Silakan isi data terlebih dahulu di menu Kalkulator.")

# -------------------------------
# Halaman: IMT
# -------------------------------
elif selected == "IMT":
    st.title("⚖️ Indeks Massa Tubuh (IMT) Anak")
    if "hasil_input" in st.session_state:
        hasil = st.session_state.hasil_input
        imt, kategori = hitung_imt(hasil["berat"], hasil["tinggi"])
        st.metric("IMT", f"{imt:.2f}", kategori)
    else:
        st.warning("Silakan isi data terlebih dahulu di menu Kalkulator.")

# -------------------------------
# Halaman: Saran Gizi
# -------------------------------
elif selected == "Saran Gizi":
    st.title("🍎 Rekomendasi Gizi Anak")
    if "hasil_input" in st.session_state:
        berat, berat_ideal = st.session_state.hasil_input["berat"], st.session_state.hasil_input["berat_ideal"]
        status, _ = saran_perbandingan(berat, berat_ideal, 0, 0)
        if status == "ideal":
            st.success("Berat anak sudah ideal. Pertahankan pola makan dan aktivitasnya!")
        elif status == "kurang":
            st.warning("Berat anak kurang. Disarankan menambah asupan gizi seperti protein, susu, dan vitamin.")
        else:
            st.error("Berat anak berlebih. Kurangi makanan tinggi gula dan lemak, serta perbanyak aktivitas fisik.")
    else:
        st.warning("Silakan isi data terlebih dahulu di menu Kalkulator.")

# -------------------------------
# Halaman: Tentang

# -------------------------------
# Halaman: Tentang
# -------------------------------
elif selected == "Tentang":
    st.markdown("## 👨‍💻 Tentang Aplikasi")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhoTgZMww3u6FbEKItTceIEl9lUsURHdCYaaO2UBeCCBkSzV95EG8C2_ORVciYYIOuznK_S49bGyDtMQbUXn0em-NJAYmrzFvdQpvIGxceTS1ThI9BzvNqf-nfBFO3m8Zyft6U9YDKo4DqCDLR3gTcit9h9kSsePOr_3dwrTUG9fX8RFDyWVYvqz04ExVkp/s320/IMG_4209.JPG", width=150, caption="Mr. Zuzawa")  # Ganti dengan foto pribadi jika ada
    
    with col2:
        st.markdown("""
        **Kalkulator Perkembangan Anak** adalah aplikasi yang dirancang untuk membantu orang tua, tenaga medis, dan guru dalam memantau dan mengevaluasi perkembangan anak-anak. Aplikasi ini memungkinkan pengguna untuk melakukan perhitungan berat badan ideal, memeriksa status perkembangan fisik, serta memberikan saran dan rekomendasi terkait gizi yang diperlukan oleh anak-anak.

        ### Fitur-fitur Utama:
        1. **Kalkulator Berat dan Tinggi Ideal**: 
            - Menggunakan rumus **Indeks Broca** untuk menghitung berat badan ideal berdasarkan tinggi badan anak. Aplikasi ini juga memberikan rekomendasi berdasarkan status berat badan anak, apakah sudah sesuai dengan usia dan tinggi badan mereka.
        
        2. **Perhitungan IMT (Indeks Massa Tubuh)**: 
            - Menghitung IMT anak untuk mengetahui kategori berat badan anak (normal, obesitas, kurus, dll.) yang dapat membantu menentukan langkah-langkah yang tepat untuk menjaga kesehatan anak.

        3. **Laporan dalam Format Sertifikat PDF**: 
            - Setelah melakukan perhitungan, aplikasi ini akan menghasilkan sertifikat PDF yang memuat hasil analisis perkembangan anak. Sertifikat ini dapat digunakan sebagai dokumentasi untuk orang tua, tenaga medis, atau untuk arsip sekolah.
        
        4. **Rekomendasi Gizi**: 
            - Aplikasi memberikan saran mengenai pola makan yang sehat berdasarkan berat badan dan kategori IMT anak. Hal ini dapat membantu orang tua atau tenaga medis dalam menentukan kebutuhan gizi yang tepat.

        5. **Visualisasi Grafik**: 
            - Perbandingan berat badan anak dengan berat ideal dapat dilihat dalam bentuk grafik yang mudah dipahami. Hal ini memberikan gambaran yang lebih jelas mengenai status perkembangan anak.

        ### Cara Penggunaan Aplikasi:
        1. **Masukkan Data Anak**: 
            - Masukkan nama, usia, jenis kelamin, berat badan, dan tinggi badan anak pada halaman kalkulator untuk memulai.
        
        2. **Cek Berat Ideal**: 
            - Setelah memasukkan data, klik tombol "🔍 Cek Ideal" untuk mengetahui apakah berat badan anak sudah sesuai dengan berat ideal berdasarkan rumus Broca. Anda juga akan mendapatkan status berat badan (kurang, normal, atau berlebih) dan tinggi badan anak.
        
        3. **Unduh Sertifikat PDF**: 
            - Setelah hasil perhitungan muncul, Anda dapat mengunduh sertifikat dalam format PDF yang berisi hasil analisis perkembangan anak.
        
        4. **Gunakan Fitur Grafis dan Saran Gizi**: 
            - Lihat grafik perbandingan berat badan dan dapatkan rekomendasi mengenai pola makan dan aktivitas anak untuk mendukung perkembangan yang sehat.

        --- 
        **Dibuat oleh:**  
        🧑‍💻 **Mr. Zuzawa**  
        💬 *"Membantu tumbuh kembang anak, dimulai dari data yang baik."*
        """)

    # Tambahkan bagian saran dan masukan
    st.markdown("""
    ## 📣 Saran dan Masukan
    
    Kami sangat menghargai setiap saran dan masukan dari Anda untuk meningkatkan aplikasi ini. Jika Anda memiliki pertanyaan atau feedback, jangan ragu untuk menghubungi kami melalui WhatsApp:
    
    [Klik di sini untuk menghubungi kami](https://wa.me/628123456789?text=Halo%20saya%20ingin%20memberikan%20masukan%20untuk%20aplikasi%20ini.)
    """)


