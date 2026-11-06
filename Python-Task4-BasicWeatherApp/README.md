# Atmos — Weather Dashboard

Atmos is a light-themed desktop weather application built with Python and Tkinter. It uses Open-Meteo for city geocoding and weather forecasts, and Zippopotam.us for postal-code lookup.

## Features

- Search by city name.
- Search by postal code, with a selectable country code (default: IN).
- Current temperature, feels-like temperature, humidity, wind speed and precipitation.
- Locally bundled weather illustrations for current conditions.
- Six-hour forecast with temperature and precipitation probability.
- Five-day forecast with high/low temperatures and precipitation totals.
- Celsius/Fahrenheit conversion.
- In-app error handling for empty input, unknown city/postal code, network failures, timeouts and HTTP errors.
- Requests run in a background thread so the interface remains responsive.

## Requirements

- Python 3.10+
- Tkinter (included with most standard Windows Python installations)
- `requests`
- `Pillow`

## Run on Windows

Open a terminal in this folder:

```bash
py -m pip install -r requirements.txt
py main.py
```

If `py` is unavailable, use `python` instead.

## Searching

- Enter a city such as `Kolkata` or `London`.
- For a postal code, enter digits only and select the matching country code from the dropdown. For example, `700001` with `IN`, or `10001` with `US`.

## Data sources

- Open-Meteo Geocoding API: city-name lookup.
- Open-Meteo Forecast API: current, hourly and daily weather.
- Zippopotam.us: postal-code lookup by country.

Open-Meteo: https://open-meteo.com/  
Zippopotam.us: https://www.zippopotam.us/

The app displays provider data as returned; weather values are forecasts/estimates and may differ from local instruments. Check each provider's current terms and attribution requirements before redistributing or using commercially.

## Project structure

```text
Python-Task4-BasicWeatherApp/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   └── weather/
│       ├── clear.png
│       ├── partly.png
│       ├── cloud.png
│       ├── rain.png
│       ├── snow.png
│       ├── storm.png
│       └── fog.png
└── screenshots/
```

## Internship task

Oasis Infobyte — Python Programming Track  
Task 4: Basic Weather App — Advanced Tier
