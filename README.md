# Tado Request Temperature
This Python script generates a CSV file containing all relevant zone temperatures along with the current temperature of your city.

## Setup
### Required Libraries
Ensure you have the following Python libraries installed:

- pytado: A library for interacting with the Tado API. You can find it here: [PyTado](https://github.com/chrism0dwk/PyTado) | ```pip install python-tado```
- pandas: For data processing and CSV file creation. | ```pip install pandas```
- datetime: For handling dates and times.
- pathlib and os: For file management.
- requests: To make HTTP requests, particularly to the weather API.
- configparser: For reading configuration files.

### OpenWeatherMap
If you want to include the current weather data for your city, set up an account with OpenWeatherMap and create an API key: [OpenWeatherMap API Key](https://openweathermap.org/appid)

### Secrets
Create a file named 'tado.ini' with the following structure to store your credentials and API key:
```dosini
[SECRETS]
username = my@username.com
password = mypassword
weather_api_key = myweatherapikey
```

## Run
Execute the Python script to gather your Tado zone data along with the current weather data, which will be saved into a CSV file.
