from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

app = Flask(__name__, 
    template_folder='../templates',
    static_folder='../static'
)
CORS(app)

def train_weather_model(historical_data, feature, day_index):
    # Prepare data for training with more features
    X = np.array([[
        i,  # day number
        np.sin(2 * np.pi * i / 365),  # yearly seasonality
        np.cos(2 * np.pi * i / 365),
        np.sin(2 * np.pi * i / 7),    # weekly pattern
        np.cos(2 * np.pi * i / 7),
    ] for i in range(len(historical_data))]) 
    
    y = np.array([day[feature] for day in historical_data])
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict with seasonal variations
    future_days = range(len(historical_data), len(historical_data) + 7)
    future_X = np.array([[
        i,
        np.sin(2 * np.pi * (i + day_index) / 365),
        np.cos(2 * np.pi * (i + day_index) / 365),
        np.sin(2 * np.pi * (i + day_index) / 7),
        np.cos(2 * np.pi * (i + day_index) / 7),
    ] for i in future_days])
    
    predictions = model.predict(future_X)
    
    # Add daily variations
    if feature == 'temp':
        daily_variation = 2 * np.sin(np.pi * (day_index % 24) / 24)
        predictions = predictions + daily_variation
    
    return predictions.tolist()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/backend/get_weather', methods=['POST'])
def get_weather():
    try:
        city = request.json['city']
        API_KEY = '75007ae6dac17e1935cd25508b0ae9ef'

        # Get coordinates
        geo_response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city},IN&limit=1&appid={API_KEY}")
        geo_data = geo_response.json()

        if not geo_data:
            return jsonify({'error': 'City not found'}), 404

        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

        # Get current weather
        current_response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}")
        current_data = current_response.json()

        # Get historical data using 5-day forecast API (more efficient)
        forecast_response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}")
        forecast_data = forecast_response.json()

        # Process forecast data (40 data points, every 3 hours for 5 days)
        historical_data = []
        if 'list' in forecast_data:
            for data_point in forecast_data['list']:
                historical_data.append({
                    'temp': data_point['main']['temp'],
                    'humidity': data_point['main']['humidity'],
                    'wind_speed': data_point['wind']['speed']
                })

        # Add current weather to historical data
        historical_data.append({
            'temp': current_data['main']['temp'],
            'humidity': current_data['main']['humidity'],
            'wind_speed': current_data['wind']['speed']
        })

        # Train models and get predictions
        daily_forecasts = []
        for i in range(7):
            temp_pred = train_weather_model(historical_data, 'temp', i)
            humidity_pred = train_weather_model(historical_data, 'humidity', i)
            wind_pred = train_weather_model(historical_data, 'wind_speed', i)
            
            daily_forecasts.append({
                'temperature': round(temp_pred[0]),
                'humidity': round(humidity_pred[0]),
                'windSpeed': round(wind_pred[0] * 3.6, 1)  # Convert m/s to km/h
            })

        return jsonify({
            'current': {
                'temperature': round(current_data['main']['temp']),
                'humidity': current_data['main']['humidity'],
                'windSpeed': round(current_data['wind']['speed'] * 3.6, 1)
            },
            'forecast': daily_forecasts
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)