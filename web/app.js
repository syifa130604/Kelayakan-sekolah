(function () {
  "use strict";
  const LABEL = {
    Sekolah_per_1000_siswa: ["Jumlah sekolah", "Banyaknya sekolah untuk setiap 1.000 siswa."],
    Mengulang_per_1000_siswa: ["Siswa mengulang kelas", "Banyaknya siswa mengulang kelas per 1.000 siswa."],
    Rombel_per_1000_siswa: ["Rombongan belajar", "Banyaknya rombongan belajar (kelas) per 1.000 siswa."],
    Guru_kurang_S1_per_1000_siswa: ["Guru berpendidikan di bawah S1", "Kepala sekolah dan guru berpendidikan di bawah S1, per 1.000 siswa."],
    Guru_S1_ke_atas_per_1000_siswa: ["Guru berpendidikan S1 ke atas", "Kepala sekolah dan guru berpendidikan S1 ke atas, per 1.000 siswa."],
    Tendik_SM_per_1000_siswa: ["Tenaga kependidikan lulusan SM", "Tenaga kependidikan berpendidikan SM, per 1.000 siswa."],
    Tendik_di_atas_SM_per_1000_siswa: ["Tenaga kependidikan di atas SM", "Tenaga kependidikan berpendidikan di atas SM, per 1.000 siswa."],
    Prop_kelas_baik: ["Ruang kelas baik", "Persentase ruang kelas dalam kondisi baik."],
    Prop_kelas_rusak_ringan: ["Ruang kelas rusak ringan", "Persentase ruang kelas rusak ringan."],
    Prop_kelas_rusak_sedang: ["Ruang kelas rusak sedang", "Persentase ruang kelas rusak sedang."],
    Prop_kelas_rusak_berat: ["Ruang kelas rusak berat", "Persentase ruang kelas rusak berat."],
  };
  const KELAS_KEYS = ["Prop_kelas_baik", "Prop_kelas_rusak_ringan", "Prop_kelas_rusak_sedang", "Prop_kelas_rusak_berat"];
  const KELOMPOK = [
    ["Sekolah dan siswa", ["Sekolah_per_1000_siswa", "Mengulang_per_1000_siswa", "Rombel_per_1000_siswa"]],
    ["Guru dan tenaga kependidikan", ["Guru_kurang_S1_per_1000_siswa", "Guru_S1_ke_atas_per_1000_siswa", "Tendik_SM_per_1000_siswa", "Tendik_di_atas_SM_per_1000_siswa"]],
    ["Kondisi ruang kelas", KELAS_KEYS],
  ];
  const WARNA = { Rendah: "#1F7A5C", Tinggi: "#B5382E" };
  const KET_ADEGAN = {
    Rendah: "Ilustrasi suasana: lebih banyak siswa bertahan di sekolah. Bukan data nyata.",
    Tinggi: "Ilustrasi suasana: lebih banyak siswa berisiko meninggalkan sekolah. Bukan data nyata.",
  };
  const skala = (f) => (KELAS_KEYS.includes(f) ? 100 : 1);
  const $ = (id) => document.getElementById(id);
  const fmtId = (n, d) => n.toFixed(d).replace(".", ",");
  const nilai = {};          // nilai tampilan (kelas dalam persen)
  const slider = {};         // elemen input per fitur
  const C = 2 * Math.PI * 40;

  // ----- Bangun slider -----
  const wadah = $("kelompok");
  KELOMPOK.forEach(([judul, daftar], i) => {
    const det = document.createElement("details");
    det.className = "kelompok";
    if (i === 0) det.open = true;
    det.innerHTML = `<summary>${judul}</summary><div class="isi-kelompok"></div>`;
    const isi = det.querySelector(".isi-kelompok");
    daftar.forEach((f) => {
      const [nama, bantuan] = LABEL[f];
      const lo = MODEL.min[f] * skala(f), hi = MODEL.max[f] * skala(f);
      const div = document.createElement("div");
      div.className = "field";
      div.innerHTML = `<label for="in_${f}"><span>${nama}</span><span class="val" id="v_${f}"></span></label>
        <input type="range" id="in_${f}" min="${lo}" max="${hi}" step="${(hi - lo) / 400}">
        <div class="bantuan">${bantuan}</div>`;
      isi.appendChild(div);
      const inp = div.querySelector("input");
      slider[f] = inp;
      inp.addEventListener("input", () => { setNilai(f, parseFloat(inp.value)); hitung(); clearPreset(); });
    });
    wadah.appendChild(det);
  });

  function setNilai(f, v) {
    nilai[f] = v;
    const inp = slider[f];
    inp.value = v;
    const lo = parseFloat(inp.min), hi = parseFloat(inp.max);
    inp.style.setProperty("--p", ((v - lo) / (hi - lo)) * 100 + "%");
    $("v_" + f).textContent = KELAS_KEYS.includes(f) ? Math.round(v) + "%" : fmtId(v, 2);
  }
  function isiDari(sumber) {
    MODEL.fitur.forEach((f) => setNilai(f, sumber[f] * skala(f)));
  }

  // ----- Kotak suara pohon -----
  const kotak = $("suara");
  MODEL.trees.forEach((_, j) => { const s = document.createElement("span"); s.style.setProperty("--i", j); kotak.appendChild(s); });

  // ----- Hitung & tampilkan -----
  let lastHasil = null;
  function hitung() {
    const data = {};
    MODEL.fitur.forEach((f) => (data[f] = nilai[f] / skala(f)));
    const tot = KELAS_KEYS.reduce((a, k) => a + data[k], 0);
    if (tot > 0) KELAS_KEYS.forEach((k) => (data[k] /= tot));
    const x = MODEL.fitur.map((f) => data[f]);
    const r = prediksiRF(MODEL, x);
    tampil(r);
  }

  function tampil(r) {
    const hasil = MODEL.kelas[r.idx];
    const p = r.proba[r.idx];
    const menang = r.suara.filter((s) => s === r.idx).length;
    document.body.dataset.state = hasil.toLowerCase();
    const lbl = $("label");
    lbl.textContent = hasil;
    lbl.style.color = WARNA[hasil];
    if (hasil !== lastHasil) { lbl.classList.remove("pulse"); void lbl.offsetWidth; lbl.classList.add("pulse"); }
    lastHasil = hasil;
    $("adeganKet").textContent = KET_ADEGAN[hasil];

    const ring = $("cincinIsi");
    ring.setAttribute("stroke-dasharray", C.toFixed(1));
    ring.style.strokeDashoffset = (C * (1 - p)).toFixed(1);
    ring.setAttribute("stroke", WARNA[hasil]);
    $("cincinTeks").textContent = Math.round(p * 100) + "%";

    $("ringkas").innerHTML = `${menang} dari ${r.suara.length} pohon keputusan memilih <b>${hasil}</b>. Hasil akhir ditentukan dari suara terbanyak seluruh pohon.`;
    $("bar-peluang").innerHTML = MODEL.kelas.map((nm, j) => {
      const v = r.proba[j] * 100;
      return `<div class="baris"><div class="atas"><span>${nm}</span><span>${Math.round(v)}%</span></div>
        <div class="latar"><div class="isi" style="width:${v.toFixed(0)}%;background:${WARNA[nm]}"></div></div></div>`;
    }).join("");

    [...kotak.children].forEach((el, j) => {
      el.style.background = WARNA[MODEL.kelas[r.suara[j]]];
      el.title = `Pohon ${j + 1}: ${MODEL.kelas[r.suara[j]]}`;
      el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop");
    });
  }

  // ----- Contoh pengisian -----
  const tombol = document.querySelectorAll(".preset button");
  function clearPreset() { tombol.forEach((b) => b.setAttribute("aria-pressed", "false")); }
  tombol.forEach((b) => b.addEventListener("click", () => {
    const k = b.dataset.preset;
    isiDari(k === "median" ? MODEL.median : MODEL.presets[k]);
    hitung();
    clearPreset();
    b.setAttribute("aria-pressed", "true");
  }));

  // ----- Tentang model -----
  const info = MODEL.info;
  const mf = info.max_features;
  $("infoModel").innerHTML = `
    <p><b>Algoritma.</b> Random Forest dengan ${info.n_estimators} pohon keputusan, kedalaman maksimum ${info.max_depth}, minimum ${info.min_samples_leaf} data per daun, dan ${mf} dipertimbangkan di setiap pemisahan. Setiap pohon dilatih dari sampel data yang berbeda (bagging), lalu hasil akhirnya diambil dari suara terbanyak.</p>
    <p><b>Data.</b> Kelayakan pendidikan Indonesia, ${info.n_data} provinsi. Seluruh nilai diubah menjadi rasio per 1.000 siswa agar provinsi besar dan kecil bisa dibandingkan.</p>
    <p><b>Target.</b> Tingkat putus sekolah per 1.000 siswa. Provinsi di atas nilai median (sekitar ${fmtId(info.median_putus, 2)}) digolongkan Tinggi, selebihnya Rendah.</p>
    <p><b>Kinerja.</b> Pada pembagian 80/20 (${info.n_test} data uji), akurasi ${Math.round(info.acc_test * 100)}%. Angka ini berasal dari satu pembagian kecil, jadi lebih tepat dibaca bersama hasil 40 pembagian acak: rata-rata akurasi <b>${Math.round(info.acc_robust_mean * 100)}%</b> dengan simpangan baku ${Math.round(info.acc_robust_std * 100)}%.</p>
    <p><b>Overfitting.</b> Pengaturan daun minimum dan pemilihan seluruh fitur dipilih lewat cross-validation untuk menekan overfitting. Selisih akurasi latih dan uji menurun, tetapi belum hilang karena datanya sangat sedikit.</p>
    <p><b>Keterbatasan.</b> Gunakan situs ini untuk memahami cara kerja Random Forest, bukan untuk menilai kondisi provinsi yang sebenarnya. Perhitungan di browser memakai struktur pohon yang sama dengan model scikit-learn.</p>`;
  const top = Object.entries(MODEL.importance).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const maks = top[0][1];
  $("fiturPenting").innerHTML = top.map(([f, v]) =>
    `<div class="baris"><div class="atas"><span>${LABEL[f][0]}</span><span>${fmtId(v, 2)}</span></div>
     <div class="latar"><div class="isi" style="width:${(v / maks * 100).toFixed(0)}%;background:#1D4E89"></div></div></div>`).join("");

  // ----- Bingkai adegan: di HP fokus ke sekolah dan bendera -----
  const adegan = $("adegan");
  function aturBingkai() { adegan.setAttribute("viewBox", window.innerWidth < 900 ? "520 0 680 460" : "0 0 1200 460"); }
  aturBingkai();
  window.addEventListener("resize", aturBingkai);

  // ----- Mulai -----
  isiDari(MODEL.median);
  document.querySelector('.preset button[data-preset="median"]').setAttribute("aria-pressed", "true");
  hitung();
})();
