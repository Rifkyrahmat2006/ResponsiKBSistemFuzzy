import os
from flask import Flask, render_template, request

# Tentukan folder template dan static secara absolut
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

def calculate_fuzzy_price(berat_val, bersih_val):
    import numpy as np
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    
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
    rule1 = ctrl.Rule(kebersihan['poor'] | berat['poor'], harga['murah'])
    rule2 = ctrl.Rule(kebersihan['average'] | berat['average'], harga['standar'])
    rule3 = ctrl.Rule(kebersihan['good'] & berat['good'], harga['mahal'])
    
    # Simulation
    pricing_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    pricing = ctrl.ControlSystemSimulation(pricing_ctrl)

    pricing.input['berat'] = berat_val
    pricing.input['kebersihan'] = bersih_val
    try:
        pricing.compute()
        return int(pricing.output['harga'])
    except:
        return 5000 # default fallback jika fuzzy tidak menghasilkan output

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path):
    res = None
    input_data = None
    if request.method == 'POST':
        try:
            b = float(request.form.get('berat', 0.5))
            k = float(request.form.get('kebersihan', 50))
            m = int(request.form.get('material', 1))
            input_data = {'berat': b, 'kebersihan': k, 'material': m}
            res = calculate_fuzzy_price(b, k)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print("Error Details:", error_details)
            res = f"Error: {str(e)}"
    return render_template('index.html', result=res, input_data=input_data)
