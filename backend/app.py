import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from physics.blast import peak_overpressure, dynamic_pressure, arrival_time, positive_phase_duration
from physics.thermal import thermal_energy, ignition_probability
from physics.radiation import prompt_radiation_dose, residual_radiation_dose
from physics.fallout import fallout_pattern
import numpy as np

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '../frontend')

app = Flask(__name__, 
            template_folder=os.path.join(FRONTEND_DIR, 'templates'),
            static_folder=FRONTEND_DIR)  # Serve entire frontend as static

CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate-blast', methods=['POST'])
def calculate_blast():
    data = request.json
    yield_kt = float(data['yield'])
    distance_m = float(data['distance'])
    burst_height = float(data.get('burst_height', 0))
    
    results = {
        'overpressure_kpa': peak_overpressure(yield_kt, distance_m, burst_height),
        'dynamic_pressure_kpa': dynamic_pressure(yield_kt, distance_m, burst_height),
        'arrival_time_sec': arrival_time(yield_kt, distance_m, burst_height),
        'positive_phase_duration_sec': positive_phase_duration(yield_kt, distance_m, burst_height),
        'thermal_cal_per_cm2': thermal_energy(yield_kt, distance_m, burst_height_m=burst_height),
        'ignition_probability': ignition_probability(thermal_energy(yield_kt, distance_m, burst_height_m=burst_height)),
        'prompt_radiation_sv': prompt_radiation_dose(yield_kt, distance_m, burst_height_m=burst_height),
        'residual_radiation_sv_per_h': residual_radiation_dose(yield_kt, distance_m, time_after_explosion=1.0)
    }
    return jsonify(results)

@app.route('/calculate-fallout', methods=['POST'])
def calculate_fallout():
    data = request.json
    # FIXED THE FUNCTION PARAMETER NAME
    lon, lat, contamination = fallout_pattern(
        yield_kt=float(data['yield']),
        burst_height_m=float(data['burst_height']),
        latitude=float(data['latitude']),
        longitude=float(data['longitude']),
        wind_speed=float(data.get('wind_speed', 5)),
        wind_direction=float(data.get('wind_direction', 90))
    )
    
    # Convert to list for JSON serialization
    return jsonify({
        'longitude': lon.tolist(),
        'latitude': lat.tolist(),
        'contamination': contamination.tolist()
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)