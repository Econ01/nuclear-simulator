from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/')
def home():
    return "Nuclear Simulator Backend"

@app.route('/calculate-blast', methods=['POST'])
def calculate_blast():
    data = request.json
    yield_kt = float(data['yield'])
    distance_m = float(data['distance'])
    
    # We'll implement the actual physics in the next step
    result = {
        'yield_kt': yield_kt,
        'distance_m': distance_m,
        'overpressure_psi': 0,  # Placeholder
        'radiation_sv': 0       # Placeholder
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)