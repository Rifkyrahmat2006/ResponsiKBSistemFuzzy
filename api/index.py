import os
import sys
import types

# Fix for Python 3.12 where distutils and imp are removed
try:
    import distutils
except ImportError:
    try:
        import setuptools
    except ImportError:
        pass

try:
    import imp
except ImportError:
    # Create a dummy imp module for backward compatibility
    imp_module = types.ModuleType('imp')
    sys.modules['imp'] = imp_module
    # Add common functions used by older packages
    def find_module(name, path=None): return None
    def load_module(name, file, pathname, description): return None
    imp_module.find_module = find_module
    imp_module.load_module = load_module

try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass

from flask import Flask, render_template, request

# Tentukan folder template dan static secara absolut
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

def calculate_fuzzy_price(berat_val, bersih_val, material_val):
    import numpy as np
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    
    # Definisi Variabel Fuzzy
    berat = ctrl.Antecedent(np.arange(0, 11, 1), 'berat')
    kebersihan = ctrl.Antecedent(np.arange(0, 101, 1), 'kebersihan')
    material = ctrl.Antecedent(np.arange(1, 4, 1), 'material')
    harga = ctrl.Consequent(np.arange(1000, 15001, 100), 'harga')

    # Membership Functions
    berat.automf(3) # poor, average, good
    kebersihan.automf(3)
    
    # Material membership
    material['rendah'] = fuzz.trimf(material.universe, [1, 1, 2])
    material['tinggi'] = fuzz.trimf(material.universe, [1, 2, 3])
    material['logam'] = fuzz.trimf(material.universe, [2, 3, 3])

    harga['murah'] = fuzz.trimf(harga.universe, [1000, 3000, 5000])
    harga['standar'] = fuzz.trimf(harga.universe, [4000, 7000, 10000])
    harga['mahal'] = fuzz.trimf(harga.universe, [9000, 12000, 15000])

    # Rules yang lebih kompleks mencakup material
    rule1 = ctrl.Rule(kebersihan['poor'] | berat['poor'], harga['murah'])
    rule2 = ctrl.Rule(kebersihan['average'] & material['rendah'], harga['murah'])
    rule3 = ctrl.Rule(kebersihan['average'] & (material['tinggi'] | material['logam']), harga['standar'])
    rule4 = ctrl.Rule(kebersihan['good'] & berat['good'] & material['logam'], harga['mahal'])
    rule5 = ctrl.Rule(kebersihan['good'] & material['tinggi'], harga['mahal'])
    
    # Simulation
    pricing_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
    pricing = ctrl.ControlSystemSimulation(pricing_ctrl)

    pricing.input['berat'] = berat_val
    pricing.input['kebersihan'] = bersih_val
    pricing.input['material'] = material_val
    
    try:
        pricing.compute()
        return int(pricing.output['harga'])
    except:
        # Fallback dinamis berdasarkan material jika compute gagal
        base_prices = {1: 2000, 2: 5000, 3: 8000}
        return base_prices.get(material_val, 5000)

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
            res = calculate_fuzzy_price(b, k, m)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print("Error Details:", error_details)
            res = f"Error: {str(e)}"
    return render_template('index.html', result=res, input_data=input_data)
