from PyTado.interface import Tado
from PyTado.exceptions import TadoCredentialsException
import pandas as pd
from datetime import datetime
from pathlib import Path
import os, requests, configparser, logging, time, sys

TADO_USERNAME = ""
TADO_PASSWORD = ""
WEATHER_API_KEY = ""
CURRENT_DATE = ""
CITY="Krefeld"
LOGGER: logging.Logger = None

def set_globals():
    global TADO_USERNAME, TADO_PASSWORD, WEATHER_API_KEY, CURRENT_DATE
    
    config = configparser.ConfigParser()
    config.read(os.path.join(Path(__file__).parent, "tado.ini"))

    TADO_USERNAME = config.get('SECRETS', 'username')
    TADO_PASSWORD = config.get('SECRETS', 'password')
    WEATHER_API_KEY = config.get('SECRETS', 'weather_api_key')
    CURRENT_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def set_logger():
    global LOGGER

    LOGGER = logging.getLogger("tado-tool")
    LOGGER.setLevel(logging.INFO)
    
    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('[%(levelname)s] - (%(name)s): %(message)s'))
    
    LOGGER.addHandler(ch)


def get_weather(api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={CITY}&units=metric"

    try:
        response = requests.get(complete_url)
    except requests.RequestException as e:
        LOGGER.warning(f"Couldn't get weather data: {e}")
    
    data = response.json()

    if data["cod"] != 200:
        LOGGER.warning(f"Wrong openweathermap-API-Key: {data}")
        return None

    main = data["main"]
    return (f"{main['temp']:.2f}".replace('.', ','),
            f"{main['humidity']:.2f}".replace('.', ','))

    
def get_zone_data() -> list:
    climate_data = []

    try:
        t = Tado(TADO_USERNAME, TADO_PASSWORD)
    except TadoCredentialsException as ce:
        LOGGER.error(f"Wrong Tado credentials: {ce}")
        sys.exit(9)

    zones = t.get_zones()

    LOGGER.debug(f"Found following zones: {', '.join([zone['name'] for zone in zones])}")

    for zone in zones:
        zone_id = zone['id']
        zone_name = zone['name']
        
        climate = t.get_climate(zone=zone_id)
        temperature = f"{climate['temperature']:.2f}".replace('.', ',')
        humidity = f"{climate['humidity']:.2f}".replace('.', ',')

        LOGGER.debug(
            f'Zone: {zone_name}, Temperature (°C): {temperature}, Humidity (%): {humidity}'
        )
        
        climate_data.append({
            "Zone": zone_name,
            "Timestamp": CURRENT_DATE,
            "Temperature (°C)": temperature,
            "Humidity (%)": humidity
        })

    if not climate_data: # I don't need the weather data if i have no zone data
        return None

    weather_data = get_weather(api_key=WEATHER_API_KEY)

    if not weather_data:
        return climate_data
    
    current_temp = "{weather_data[0]:.2f}".replace('.', ',')
    current_humidity = "{weather_data[1]:.2f}".replace('.', ',')

    current_temp, current_humidity = get_weather(api_key=WEATHER_API_KEY)
    if current_temp and current_humidity:
        climate_data.append({
            "Zone": CITY,
            "Timestamp": CURRENT_DATE,
            "Temperature (°C)": current_temp,
            "Humidity (%)": current_humidity
        })

    return climate_data

def write_dataframe_to_csv(data: pd.DataFrame):
    csv_filename = os.path.join(Path(__file__).parent, "tado_climate_data.csv")

    try:
        if os.path.isfile(csv_filename):
            data.to_csv(csv_filename, index=False, sep=";", encoding="windows-1252", mode="a", header=False)
        else:
            data.to_csv(csv_filename, index=False, sep=";", encoding="windows-1252")

        LOGGER.info(f"Climate data successfully recorded and saved in '{csv_filename}'.")
    except PermissionError as pe:
        LOGGER.error(f"Permission denied for writing to {csv_filename}: {pe}")
        sys.exit(9)


def execute():
    climate_data: list = get_zone_data()
    
    if not climate_data:
        LOGGER.error("No zone data available")

    df = pd.DataFrame(climate_data)

    write_dataframe_to_csv(df)


if __name__ == "__main__":
    start_time = time.time()

    set_logger()
    
    LOGGER.info("Start measurement")
    
    set_globals()
    execute()

    LOGGER.info(f"Executed normaly in {round(time.time() - start_time, 2)}s")
