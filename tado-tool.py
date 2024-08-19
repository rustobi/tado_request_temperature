from PyTado.interface import Tado
import pandas as pd
from datetime import datetime
from pathlib import Path
import os, requests, configparser

TADO_USERNAME = ""
TADO_PASSWORD = ""
WEATHER_API_KEY = ""
CITY="Krefeld"

def get_weather(api_key):
    # OpenWeatherMap API URL
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    # Vollständige URL mit API-Schlüssel und Stadtname
    complete_url = f"{base_url}appid={api_key}&q={CITY}&units=metric"

    # HTTP-Anfrage an die API
    response = requests.get(complete_url)
    
    # Antwort in JSON konvertieren
    data = response.json()

    # Überprüfen, ob die Stadt gefunden wurde
    if data["cod"] != "404":
        main = data["main"]
        temperature = main["temp"]
        humidity = main["humidity"]

        return (temperature, humidity)
    else:
        return None

def write_to_csv():
    # Tado-Objekt erstellen
    t = Tado(TADO_USERNAME, TADO_PASSWORD)

    # Zonen abrufen
    zones = t.get_zones()

    # Liste zur Speicherung der Klimadaten erstellen
    climate_data = []
    datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current_temp, current_humidity = get_weather(api_key=WEATHER_API_KEY)
    current_temp = f"{current_temp:.2f}".replace('.', ',')
    current_humidity = f"{current_humidity:.2f}".replace('.', ',')

    # Klimadaten für jede Zone abrufen
    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']
        
        # Klimadaten für die aktuelle Zone abrufen
        climate = t.get_climate(zone=zone_id)
        temperature = f"{climate['temperature']:.2f}".replace('.', ',')
        humidity = f"{climate['humidity']:.2f}".replace('.', ',')
        
        # Daten sammeln
        climate_data.append({
            "Zone": zone_name,
            "Timestamp": datetime_now,
            "Temperature (°C)": temperature,
            "Humidity (%)": humidity
        })

    if current_temp and current_humidity:
        climate_data.append({
            "Zone": CITY,
            "Timestamp": datetime_now,
            "Temperature (°C)": current_temp,
            "Humidity (%)": current_humidity
        })

    # Daten in einem DataFrame speichern
    df = pd.DataFrame(climate_data)

    # Daten in einer CSV-Datei speichern mit UTF-8 Encoding
    csv_filename = os.path.join(Path(__file__).parent, "tado_climate_data.csv")

    if os.path.isfile(csv_filename):
        df.to_csv(csv_filename, index=False, sep=";", encoding="windows-1252", mode="a", header=False)
    else:
        df.to_csv(csv_filename, index=False, sep=";", encoding="windows-1252")

    print(f"Klima-Daten erfolgreich erfasst und in '{csv_filename}' gespeichert.")

def set_globals():
    global TADO_USERNAME, TADO_PASSWORD, WEATHER_API_KEY
    
    config = configparser.ConfigParser()
    config.read(os.path.join(Path(__file__).parent, "tado.ini"))

    TADO_USERNAME = config.get('SECRETS', 'username')
    TADO_PASSWORD = config.get('SECRETS', 'password')
    WEATHER_API_KEY = config.get('SECRETS', 'weather_api_key')

if __name__ == "__main__":
    set_globals()
    write_to_csv()