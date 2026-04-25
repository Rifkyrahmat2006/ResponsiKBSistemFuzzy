
# PRD: Smart-Trash-Classifier (Fuzzy Logic System)

## 1. Ringkasan Produk
Sebuah sistem berbasis web yang menggunakan **Logika Fuzzy** untuk menentukan nilai ekonomi (harga beli) sampah anorganik secara otomatis berdasarkan kondisi fisik sampah, bukan hanya sekadar berat.

## 2. Masalah & Urgensi
* **Subjektivitas:** Penentuan harga di bank sampah seringkali dilakukan secara manual dan subjektif.
* **Kualitas Sampah:** Sampah yang kotor atau basah menurunkan harga jual ke pabrik, namun seringkali dihargai sama dengan sampah bersih oleh pengelola bank sampah.
* **Urgensi:** Meningkatkan transparansi harga dan mendorong nasabah untuk menyetorkan sampah dalam keadaan bersih dan terpilah dengan baik.

## 3. Spesifikasi Logika Fuzzy (Mamdani)
Sistem ini akan memproses 3 variabel input untuk menghasilkan 1 output harga.

* **Input 1: Berat Sampah (kg)**
    * Linguistik: Ringan, Sedang, Berat.
* **Input 2: Tingkat Kebersihan (%)**
    * Linguistik: Kotor, Cukup Bersih, Sangat Bersih.
* **Input 3: Jenis Material (Skala Prioritas)**
    * Linguistik: Plastik Rendah (kresek), Plastik Tinggi (PET/HDPE), Logam.
* **Output: Harga Beli (Rupiah/kg)**
    * Linguistik: Murah, Standar, Mahal.

---

## 4. Arsitektur Teknis
* **Backend:** Python + Flask.
* **Fuzzy Library:** `scikit-fuzzy` (untuk perhitungan logika fuzzy).
* **Frontend:** HTML5 + Tailwind CSS (Responsif untuk petugas bank sampah di lapangan).
* **Deployment:** Vercel (Serverless Functions).

---

## 5. Implementasi Kode (Flask)

Untuk deploy ke Vercel, struktur folder harus mengikuti standar *Serverless Functions*.

### 1. Struktur Folder
```text
smart-trash-classifier/
├── api/
│   └── index.py        # Logika Flask & Fuzzy
├── templates/
│   └── index.html      # UI Input & Hasil
├── static/
│   └── css/            # Tailwind (via CDN)
├── requirements.txt    # Library yang dibutuhkan
├── vercel.json         # Konfigurasi Deployment
└── README.md
```

### 2. File: `requirements.txt`
```text
Flask==2.3.2
numpy==1.24.3
scikit-fuzzy==0.4.2
```

### 3. File: `api/index.py` (Core Logic)
```python
from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)

def calculate_fuzzy_price(berat_val, bersih_val):
    # Definisi Variabel Fuzzy
    berat = ctrl.Antecedent(np.arange(0, 11, 1), 'berat')
    kebersihan = ctrl.Antecedent(np.arange(0, 101, 1), 'kebersihan')
    harga = ctrl.Consequent(np.arange(1000, 10001, 100), 'harga')

    # Membership Functions
    berat.automf(3) # poor, average, good
    kebersihan.automf(3)
    harga['murah'] = fuzz.trimf(harga.universe, [1000, 2000, 5000])
    harga['standar'] = fuzz.trimf(harga.universe, [4000, 6000, 8000])
    harga['mahal'] = fuzz.trimf(harga.universe, [7000, 10000, 10000])

    # Rules Sederhana
    rule1 = ctrl.Rule(berat['good'] & kebersihan['good'], harga['mahal'])
    rule2 = ctrl.Rule(kebersihan['poor'], harga['murah'])
    
    # Simulation
    pricing_ctrl = ctrl.ControlSystem([rule1, rule2])
    pricing = ctrl.ControlSystemSimulation(pricing_ctrl)

    pricing.input['berat'] = berat_val
    pricing.input['kebersihan'] = bersih_val
    pricing.compute()
    
    return int(pricing.output['harga'])

@app.route('/', methods=['GET', 'POST'])
def index():
    res = None
    if request.method == 'POST':
        b = float(request.form.get('berat'))
        k = float(request.form.get('kebersihan'))
        res = calculate_fuzzy_price(b, k)
    return render_template('index.html', result=res)
```

```