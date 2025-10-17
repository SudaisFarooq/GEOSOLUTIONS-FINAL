import os
from flask import Flask, request, jsonify, send_from_directory
from model.predict import predict_flood

app = Flask(__name__, static_folder='public', static_url_path='')

# Serve index page
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

# Serve floodPrediction page
@app.route('/floodPrediction')
def flood_prediction_page():
    return send_from_directory('public', 'floodPrediction.html')

# Test route
@app.route('/test')
def test():
    return 'Server is running correctly.'

# Prediction API
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not start_date or not end_date or latitude is None or longitude is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        result = predict_flood(start_date, end_date, latitude, longitude)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
