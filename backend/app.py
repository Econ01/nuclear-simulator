# backend/app.py
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from physics.models import NuclearBlastModel

import os
BASE_DIR = os.path.dirname(__file__)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, '../frontend/templates'),
    static_folder=os.path.join(BASE_DIR, '../frontend')
)

CORS(app)

# Serve the main page
@app.route('/')
def home():
    return render_template('index.html')

# API endpoints
@app.route('/calculate-blast', methods=['POST'])
def calculate_blast():
    data = request.json
    yield_kt = float(data['yield'])
    distance = float(data['distance'])
    
    results = {
        'overpressure_kpa': NuclearBlastModel.overpressure(yield_kt, distance),
        'thermal_cal_per_cm2': NuclearBlastModel.thermal_radiation(yield_kt, distance),
        'radiation_sv': NuclearBlastModel.radiation_dose(yield_kt, distance)
    }
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5000, debug=True)