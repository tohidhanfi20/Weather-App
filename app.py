import os
import mysql.connector
from flask import Flask, render_template, request
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

API_KEY = ""  # Replace with your API key

# Load database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

# Connect to Cloud SQL
def get_db_connection():
    connection = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        unix_socket=f"/cloudsql/{INSTANCE_CONNECTION_NAME}"
    )
    return connection

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    error_message = None

    if request.method == "POST":
        city = request.form["city"].strip()

        if not city:
            error_message = "City name cannot be empty!"
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)

            if response.status_code == 200:
                weather_data = response.json()

                # Store city search in Cloud SQL
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO searches (city, country, temp) VALUES (%s, %s, %s)", 
                                   (weather_data["name"], weather_data["sys"]["country"], weather_data["main"]["temp"]))
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print("Database error:", e)

            else:
                error_message = "City not found! Please enter a valid city."

    return render_template("index.html", weather=weather_data, error=error_message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
