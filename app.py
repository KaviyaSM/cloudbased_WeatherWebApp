from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS
from groq import Groq
from geonamescache import GeonamesCache
from fuzzywuzzy import process
import re
from unidecode import unidecode
import string
import firebase_admin
from firebase_admin import credentials, auth, firestore
from flask_cors import cross_origin
from dotenv import load_dotenv
import os


app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app, origins="http://127.0.0.1:5500") 

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API")
GROQ_API_KEY = os.getenv("GORQ_API")

OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

groq_client = Groq(api_key=GROQ_API_KEY)

# Path to your Firebase service account key JSON file
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

gc = GeonamesCache()
all_cities = [city["name"] for city in gc.get_cities().values()]

aliases = {
    "bangalore": "Bengaluru",
    # add other common aliases if needed
}

def verify_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid']
    except Exception as e:
        print("Token verification failed:", e)
        return None


def extract_city_from_text(user_input):
    user_input_norm = unidecode(user_input.lower())
    # Remove punctuation so regex word boundaries work correctly
    user_input_norm = re.sub(f"[{re.escape(string.punctuation)}]", " ", user_input_norm)

    # Normalize cities too
    norm_city_map = {unidecode(city.lower()): city for city in all_cities}

    matched_cities = []
    for norm_city, original_city in norm_city_map.items():
        if re.search(rf"\b{re.escape(norm_city)}\b", user_input_norm):
            matched_cities.append(original_city)

    if matched_cities:
        return matched_cities[0]
    
    # Check aliases
    for alias, real_city in aliases.items():
        if re.search(rf"\b{re.escape(alias)}\b", user_input_norm):
            return real_city

    # Fuzzy fallback
    best_match, score = process.extractOne(
        user_input_norm, list(norm_city_map.keys())
    )
    if score >= 90 and abs(len(best_match) - len(user_input_norm)) <= 3:
        return norm_city_map[best_match]

    return None

def save_last_city(uid, city):
    user_ref = db.collection('users').document(uid)
    user_ref.set({'last_city': city}, merge=True)

def get_last_city(uid):
    user_ref = db.collection('users').document(uid)
    doc = user_ref.get()
    if doc.exists:
        return doc.to_dict().get('last_city')
    return None



def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

def generate_natural_reply(user_question, weather_data):
    # Extract details from weather data
    city = weather_data.get("name", "the city")
    description = weather_data["weather"][0]["description"]
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]

    context = (
        f"Weather in {city}:\n"
        f"- Description: {description}\n"
        f"- Temperature: {temp}°C (Feels like {feels_like}°C)\n"
        f"- Humidity: {humidity}%\n"
        f"- Wind speed: {wind_speed} m/s\n\n"
        f"User's question: {user_question}\n\n"
        f"Based on the above weather, answer the question naturally and helpfully."
        f"If the user is asking whether they need an umbrella or if it will rain, answer based on the weather description. "
        f"Be direct, and make the answer useful to a regular person going outside. "
        f"If the user asks something else, use the weather data to answer that instead."
       )

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant."},
            {"role": "user", "content": context}
        ],
        temperature=0.5,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()

@app.route('/')
def index():
    return app.send_static_file('register.html')

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        id_token = data.get('id_token', '')  # Get the token from frontend

        uid = verify_token(id_token)
        if not uid:
            return jsonify({'reply': "Authentication failed. Please login again."}), 401

        city = extract_city_from_text(user_message)

        if city:
            save_last_city(uid, city)
        else:
            city = get_last_city(uid)
            if not city:
                return jsonify({'reply': "Sorry, I couldn't find a city in your message. Please try again."})

        weather = get_weather(city)
        if not weather:
            return jsonify({'reply': "Sorry, I couldn't fetch the weather info. Please try again."})

        reply = generate_natural_reply(user_message, weather)
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"Error in /api/chatbot: {e}")
        return jsonify({'reply': "Internal server error occurred."}), 500


if __name__ == '__main__':
    app.run(debug=True)
