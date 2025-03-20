from flask import Flask, render_template, request
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

API_KEY = ""  # Replace with your API key

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    error_message = None

    if request.method == "POST":
        city = request.form["city"].strip()
        
        if not city:
            error_message = "City name cannot be empty!"
            logging.warning("User submitted an empty city name.")
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()
                logging.info(f"Fetched weather for {city}: {weather_data}")
            else:
                error_message = "City not found! Please enter a valid city."
                logging.error(f"Failed to fetch weather for {city}. API response: {response.text}")

    return render_template("index.html", weather=weather_data, error=error_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
