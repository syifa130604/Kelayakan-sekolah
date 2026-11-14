/* Inferensi Random Forest di browser: meniru scikit-learn (predict_proba = rata-rata proporsi kelas di daun). */
(function (g) {
  function lacak(pohon, x) {
    let n = 0;
    while (pohon.l[n] !== -1) {
      // scikit-learn membandingkan nilai float32 dengan ambang float64
      n = Math.fround(x[pohon.f[n]]) <= pohon.t[n] ? pohon.l[n] : pohon.r[n];
    }
    return pohon.v[n];
  }
  g.prediksiRF = function (model, x) {
    const k = model.kelas.length;
    const proba = new Array(k).fill(0);
    const suara = [];
    for (const p of model.trees) {
      const v = lacak(p, x);
      let terbaik = 0;
      for (let c = 0; c < k; c++) { proba[c] += v[c]; if (v[c] > v[terbaik]) terbaik = c; }
      suara.push(terbaik);
    }
    for (let c = 0; c < k; c++) proba[c] /= model.trees.length;
    let idx = 0;
    for (let c = 1; c < k; c++) if (proba[c] > proba[idx]) idx = c;
    return { proba, suara, idx };
  };
})(typeof window !== "undefined" ? window : globalThis);
