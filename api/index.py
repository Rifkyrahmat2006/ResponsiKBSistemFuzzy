import os
from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Tentukan folder template dan static secara absolut
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

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
        try:
            b = float(request.form.get('berat', 0))
            k = float(request.form.get('kebersihan', 0))
            res = calculate_fuzzy_price(b, k)
        except (ValueError, TypeError, Exception) as e:
            print("Error:", e)
            res = "Input tidak valid atau error sistem"
    return render_template('index.html', result=res)
