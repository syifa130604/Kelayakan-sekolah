import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Prediksi Putus Sekolah", page_icon="🎓", layout="wide")

# ---------- Data model ----------
@st.cache_resource
def muat_model():
    return joblib.load("model_rf.joblib")

paket = muat_model()
model, fitur, kelas = paket["model"], paket["fitur"], paket["kelas"]

LABEL = {
    "Sekolah_per_1000_siswa": ("Jumlah sekolah", "Banyaknya sekolah untuk setiap 1.000 siswa."),
    "Mengulang_per_1000_siswa": ("Siswa mengulang kelas", "Banyaknya siswa mengulang kelas per 1.000 siswa."),
    "Rombel_per_1000_siswa": ("Rombongan belajar", "Banyaknya rombongan belajar (kelas) per 1.000 siswa."),
    "Guru_kurang_S1_per_1000_siswa": ("Guru berpendidikan di bawah S1", "Kepala sekolah dan guru berpendidikan di bawah S1, per 1.000 siswa."),
    "Guru_S1_ke_atas_per_1000_siswa": ("Guru berpendidikan S1 ke atas", "Kepala sekolah dan guru berpendidikan S1 ke atas, per 1.000 siswa."),
    "Tendik_SM_per_1000_siswa": ("Tenaga kependidikan lulusan SM", "Tenaga kependidikan berpendidikan SM, per 1.000 siswa."),
    "Tendik_di_atas_SM_per_1000_siswa": ("Tenaga kependidikan di atas SM", "Tenaga kependidikan berpendidikan di atas SM, per 1.000 siswa."),
    "Prop_kelas_baik": ("Ruang kelas baik", "Persentase ruang kelas dalam kondisi baik."),
    "Prop_kelas_rusak_ringan": ("Ruang kelas rusak ringan", "Persentase ruang kelas rusak ringan."),
    "Prop_kelas_rusak_sedang": ("Ruang kelas rusak sedang", "Persentase ruang kelas rusak sedang."),
    "Prop_kelas_rusak_berat": ("Ruang kelas rusak berat", "Persentase ruang kelas rusak berat."),
}
KELAS_KEYS = ["Prop_kelas_baik", "Prop_kelas_rusak_ringan", "Prop_kelas_rusak_sedang", "Prop_kelas_rusak_berat"]
KELOMPOK = [
    ("Sekolah dan siswa", ["Sekolah_per_1000_siswa", "Mengulang_per_1000_siswa", "Rombel_per_1000_siswa"]),
    ("Guru dan tenaga kependidikan", ["Guru_kurang_S1_per_1000_siswa", "Guru_S1_ke_atas_per_1000_siswa",
                                       "Tendik_SM_per_1000_siswa", "Tendik_di_atas_SM_per_1000_siswa"]),
    ("Kondisi ruang kelas", KELAS_KEYS),
]
WARNA = {"Rendah": "#1F7A5C", "Tinggi": "#B5382E"}

def skala(f):
    """Ruang kelas ditampilkan dalam persen, fitur lain apa adanya."""
    return 100.0 if f in KELAS_KEYS else 1.0

def reset_nilai():
    for f in fitur:
        st.session_state[f"in_{f}"] = float(paket["median"][f]) * skala(f)

for f in fitur:
    st.session_state.setdefault(f"in_{f}", float(paket["median"][f]) * skala(f))

# ---------- Gaya ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp, button, input { font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important; }
.stApp { background: #F3F5F8; }
header[data-testid="stHeader"] { background: transparent; }
.stAppDeployButton, #MainMenu, footer { display: none !important; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }
h1.judul { font-size: 2.1rem; font-weight: 800; color: #14213D; letter-spacing: -0.02em; margin: 0 0 .35rem 0; line-height: 1.2; }
p.sub { color: #5B6776; font-size: 1.02rem; margin: 0 0 1.4rem 0; max-width: 62ch; line-height: 1.6; }
.stTabs [data-baseweb="tab-list"] { gap: 1.6rem; border-bottom: 1px solid #DDE3EA; }
.stTabs [data-baseweb="tab"] { font-weight: 600; color: #5B6776; padding: .6rem 0; }
.stTabs [aria-selected="true"] { color: #1D4E89; }
div[data-testid="stExpander"] { background: #FFFFFF; border: 1px solid #DDE3EA; border-radius: 12px; box-shadow: none; }
div[data-testid="stExpander"] summary { font-weight: 700; color: #14213D; }
.st-key-hasil { position: sticky; top: 1.2rem; }
.kartu { background: #FFFFFF; border: 1px solid #DDE3EA; border-radius: 16px; padding: 1.5rem 1.6rem; }
.kartu .kecil { color: #5B6776; font-size: .92rem; margin: 0; }
.kartu .besar { animation: muncul .5s cubic-bezier(.2,.8,.2,1) both; font-size: 3rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; margin: .2rem 0 .6rem 0; }
.kartu .teks { color: #14213D; font-size: .98rem; line-height: 1.55; margin: 0 0 1.1rem 0; }
.bar-baris { margin: .55rem 0; }
.bar-atas { display: flex; justify-content: space-between; font-size: .9rem; color: #14213D; margin-bottom: .25rem; font-weight: 600; }
.bar-latar { background: #E8ECF1; border-radius: 99px; height: 10px; overflow: hidden; }
.bar-isi { height: 10px; border-radius: 99px; width: var(--w); animation: tumbuh .8s cubic-bezier(.2,.8,.2,1) both; }
.pohon { display: flex; gap: 5px; margin: .3rem 0 1.1rem 0; }
.pohon span { flex: 1; height: 22px; border-radius: 5px; animation: pop .4s cubic-bezier(.2,.9,.3,1.3) both; animation-delay: calc(var(--i) * 55ms + 120ms); }
.faktor-judul { font-weight: 700; color: #14213D; margin: 1.4rem 0 .3rem 0; font-size: .98rem; }
.faktor-ket { color: #5B6776; font-size: .85rem; margin: 0 0 .5rem 0; line-height: 1.5; }
.catatan { color: #5B6776; font-size: .85rem; line-height: 1.55; margin-top: 1.1rem; }
div.stButton > button { border-radius: 10px; font-weight: 600; border: 1px solid #C9D2DD; background: #FFFFFF; color: #14213D; }
div.stButton > button:hover { border-color: #1D4E89; color: #1D4E89; }
.kepala { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.cincin-isi { stroke-dashoffset: var(--o); animation: cincin 1s cubic-bezier(.2,.8,.2,1) both; }
.kartu { transition: box-shadow .25s ease, border-color .25s ease; }
.kartu:hover { box-shadow: 0 10px 30px rgba(20,33,61,.08); border-color: #C9D2DD; }
div[data-testid="stExpander"] { transition: border-color .2s ease, box-shadow .2s ease; }
div[data-testid="stExpander"]:hover { border-color: #1D4E89; box-shadow: 0 4px 14px rgba(29,78,137,.08); }
h1.judul { animation: muncul .7s cubic-bezier(.2,.8,.2,1) both; }
p.sub { animation: muncul .7s .12s cubic-bezier(.2,.8,.2,1) both; }
@keyframes tumbuh { from { width: 0; } to { width: var(--w); } }
@keyframes pop { from { opacity: 0; transform: scale(.3); } to { opacity: 1; transform: scale(1); } }
@keyframes muncul { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes cincin { from { stroke-dashoffset: var(--c); } to { stroke-dashoffset: var(--o); } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="judul">Prediksi tingkat putus sekolah per provinsi</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub">Masukkan kondisi pendidikan suatu provinsi. Model Random Forest akan menilai apakah '
            'tingkat putus sekolahnya tergolong Rendah atau Tinggi, dan hasilnya langsung diperbarui saat nilai diubah.</p>',
            unsafe_allow_html=True)

tab_prediksi, tab_model = st.tabs(["Prediksi", "Tentang model"])

with tab_prediksi:
    kiri, kanan = st.columns([3, 2], gap="large")

    with kiri:
        nilai = {}
        for i, (judul, daftar) in enumerate(KELOMPOK):
            with st.expander(judul, expanded=(i == 0)):
                for f in daftar:
                    nama, bantuan = LABEL[f]
                    lo, hi = float(paket["min"][f]) * skala(f), float(paket["max"][f]) * skala(f)
                    satuan = "%" if f in KELAS_KEYS else ""
                    fmt = "%.0f%%" if f in KELAS_KEYS else "%.2f"
                    nilai[f] = st.slider(nama, min_value=lo, max_value=hi, key=f"in_{f}",
                                         help=bantuan, format=fmt)
        st.button("Kembalikan ke nilai tipikal", on_click=reset_nilai)

    # Komposisi ruang kelas dinormalisasi agar totalnya 100%
    data = {f: nilai[f] / skala(f) for f in fitur}
    total_kelas = sum(data[k] for k in KELAS_KEYS)
    if total_kelas > 0:
        for k in KELAS_KEYS:
            data[k] = data[k] / total_kelas
    X_in = pd.DataFrame([data], columns=fitur)

    proba = model.predict_proba(X_in)[0]
    idx = int(proba.argmax())
    hasil = kelas[idx]
    suara = [int(t.predict(X_in.values)[0]) for t in model.estimators_]
    n_pohon = len(suara)
    n_menang = sum(1 for s in suara if s == idx)

    kotak_pohon = "".join(
        f'<span style="--i:{j};background:{WARNA[kelas[s]]}" title="Pohon {j+1}: {kelas[s]}"></span>'
        for j, s in enumerate(suara))

    bars = ""
    for j, nm in enumerate(kelas):
        p = proba[j] * 100
        bars += (f'<div class="bar-baris"><div class="bar-atas"><span>{nm}</span><span>{p:.0f}%</span></div>'
                 f'<div class="bar-latar"><div class="bar-isi" style="--w:{p:.0f}%;background:{WARNA[nm]}"></div></div></div>')

    C = 2 * 3.14159265 * 40
    p_menang = float(proba[idx])
    off = C * (1 - p_menang)
    cincin = (f'<svg viewBox="0 0 100 100" width="96" height="96" role="img" aria-label="Peluang {hasil} {p_menang:.0%}">'
              f'<circle cx="50" cy="50" r="40" fill="none" stroke="#E8ECF1" stroke-width="10"/>'
              f'<circle class="cincin-isi" cx="50" cy="50" r="40" fill="none" stroke="{WARNA[hasil]}" stroke-width="10" '
              f'stroke-linecap="round" stroke-dasharray="{C:.1f}" style="--c:{C:.1f};--o:{off:.1f}" transform="rotate(-90 50 50)"/>'
              f'<text x="50" y="57" text-anchor="middle" font-size="21" font-weight="800" fill="#14213D">{p_menang:.0%}</text></svg>')

    penting = pd.Series(model.feature_importances_, index=fitur).sort_values(ascending=False).head(5)
    maks = penting.max()
    faktor = ""
    for f, v in penting.items():
        faktor += (f'<div class="bar-baris"><div class="bar-atas"><span>{LABEL[f][0]}</span><span>{v:.2f}</span></div>'
                   f'<div class="bar-latar"><div class="bar-isi" style="--w:{v/maks*100:.0f}%;background:#1D4E89"></div></div></div>')

    with kanan:
        with st.container(key="hasil"):
            st.markdown(f"""
<div class="kartu">
  <div class="kepala">
    <div>
      <p class="kecil">Prediksi tingkat putus sekolah</p>
      <p class="besar" style="color:{WARNA[hasil]}">{hasil}</p>
    </div>
    {cincin}
  </div>
  <p class="teks">{n_menang} dari {n_pohon} pohon keputusan memilih <b>{hasil}</b>. Hasil akhir ditentukan dari suara terbanyak seluruh pohon.</p>
  {bars}
  <div class="faktor-judul">Suara tiap pohon</div>
  <div class="pohon">{kotak_pohon}</div>
  <p class="catatan">Model dilatih dari data 38 provinsi dan dibuat untuk keperluan pembelajaran. Lihat tab Tentang model untuk akurasi dan keterbatasannya.</p>
</div>""", unsafe_allow_html=True)

with tab_model:
    info = paket["info"]
    mf = info["max_features"]
    st.markdown(f"""
<div class="kartu">
<p class="teks"><b>Algoritma.</b> Random Forest dengan {info['n_estimators']} pohon keputusan, kedalaman maksimum {info['max_depth']}, minimum {info['min_samples_leaf']} data per daun, dan {mf} dipertimbangkan di setiap pemisahan. Setiap pohon dilatih dari sampel data yang berbeda (bagging), lalu hasil akhirnya diambil dari suara terbanyak.</p>
<p class="teks"><b>Data.</b> Kelayakan pendidikan Indonesia, {info['n_data']} provinsi. Seluruh nilai diubah menjadi rasio per 1.000 siswa agar provinsi besar dan kecil bisa dibandingkan.</p>
<p class="teks"><b>Target.</b> Tingkat putus sekolah per 1.000 siswa. Provinsi di atas nilai median (sekitar {str(round(info['median_putus'], 2)).replace('.', ',')}) digolongkan Tinggi, selebihnya Rendah.</p>
<p class="teks"><b>Kinerja.</b> Pada pembagian 80/20 ({info['n_test']} data uji), akurasi {info['acc_test']:.0%}. Angka ini berasal dari satu pembagian kecil, jadi lebih tepat dibaca bersama hasil 40 pembagian acak: rata-rata akurasi <b>{info['acc_robust_mean']:.0%}</b> dengan simpangan baku {info['acc_robust_std']:.0%}.</p>
<p class="teks"><b>Overfitting.</b> Pengaturan daun minimum dan pemilihan seluruh fitur dipilih lewat cross-validation untuk menekan overfitting. Selisih akurasi latih dan uji menurun, tetapi belum hilang karena datanya sangat sedikit.</p>
<p class="teks"><b>Keterbatasan.</b> Gunakan aplikasi ini untuk memahami cara kerja Random Forest, bukan untuk menilai kondisi provinsi yang sebenarnya.</p>
<div class="faktor-judul" style="margin-top:1.2rem">Fitur yang paling berpengaruh pada model</div>
<p class="faktor-ket">Lima fitur dengan skor kepentingan tertinggi. Berlaku untuk model secara keseluruhan, bukan untuk satu input.</p>
{faktor}
</div>""", unsafe_allow_html=True)