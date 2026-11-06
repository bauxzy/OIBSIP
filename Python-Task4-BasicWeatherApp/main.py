"""
Atmos — a light, location-first weather dashboard.
Weather data: Open-Meteo (geocoding + forecast) and Zippopotam.us (postal lookup).
"""

import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image, ImageTk

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
POSTAL_URL = "https://api.zippopotam.us"

BASE_DIR = Path(__file__).resolve().parent
ICON_DIR = BASE_DIR / "assets" / "weather"

WEATHER = {
    0: ("Clear sky", "clear"), 1: ("Mainly clear", "partly"),
    2: ("Partly cloudy", "partly"), 3: ("Overcast", "cloud"),
    45: ("Fog", "fog"), 48: ("Rime fog", "fog"),
    51: ("Light drizzle", "rain"), 53: ("Drizzle", "rain"),
    55: ("Dense drizzle", "rain"), 56: ("Freezing drizzle", "rain"),
    57: ("Heavy freezing drizzle", "rain"), 61: ("Slight rain", "rain"),
    63: ("Moderate rain", "rain"), 65: ("Heavy rain", "rain"),
    66: ("Freezing rain", "rain"), 67: ("Heavy freezing rain", "rain"),
    71: ("Slight snow", "snow"), 73: ("Snow", "snow"),
    75: ("Heavy snow", "snow"), 77: ("Snow grains", "snow"),
    80: ("Rain showers", "rain"), 81: ("Moderate showers", "rain"),
    82: ("Heavy showers", "storm"), 85: ("Snow showers", "snow"),
    86: ("Heavy snow showers", "snow"), 95: ("Thunderstorm", "storm"),
    96: ("Thunderstorm with hail", "storm"), 99: ("Heavy thunderstorm", "storm"),
}


class AtmosApp:
    BG = "#f3f7fa"
    WHITE = "#ffffff"
    TEXT = "#213547"
    MUTED = "#718493"
    BLUE = "#367da8"
    BLUE_LIGHT = "#e7f2f8"
    LINE = "#dce7ed"
    PALE = "#f7fafc"

    def __init__(self, root):
        self.root = root
        self.root.title("Atmos | Weather")
        self.root.geometry("960x790")
        self.root.minsize(820, 700)
        self.root.configure(bg=self.BG)

        self.query = tk.StringVar()
        self.country = tk.StringVar(value="IN")
        self.unit = tk.StringVar(value="°C")
        self.status = tk.StringVar(value="Search for a city or enter a postal code.")
        self.last_data = None
        self.icon_images = {}
        self._load_icons()
        self._build()

    def _load_icons(self):
        for key, filename in {
            "clear": "clear.png", "partly": "partly.png", "cloud": "cloud.png",
            "rain": "rain.png", "snow": "snow.png", "storm": "storm.png", "fog": "fog.png"
        }.items():
            try:
                image = Image.open(ICON_DIR / filename).convert("RGBA")
                self.icon_images[key] = ImageTk.PhotoImage(image)
            except (OSError, ValueError):
                self.icon_images[key] = None

    def _card(self, parent, padding=16):
        return tk.Frame(parent, bg=self.WHITE, padx=padding, pady=padding,
                        highlightthickness=1, highlightbackground=self.LINE)

    def _button(self, parent, text, command, primary=False):
        return tk.Button(
            parent, text=text, command=command,
            bg=self.BLUE if primary else self.BLUE_LIGHT,
            fg="#ffffff" if primary else self.BLUE,
            activebackground="#28688f", activeforeground="#ffffff",
            relief="flat", bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"), padx=17, pady=9
        )

    def _build(self):
        page = tk.Frame(self.root, bg=self.BG, padx=28, pady=22)
        page.pack(fill="both", expand=True)

        header = tk.Frame(page, bg=self.BG)
        header.pack(fill="x", pady=(0, 17))
        brand = tk.Frame(header, bg=self.BG)
        brand.pack(side="left")
        tk.Label(brand, text="ATMOS  /  LOCAL WEATHER", bg=self.BG, fg=self.BLUE,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(brand, text="Weather, at a glance.", bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(4, 0))
        unit_area = tk.Frame(header, bg=self.BG)
        unit_area.pack(side="right", anchor="ne")
        tk.Label(unit_area, text="DISPLAY UNIT", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="e", pady=(2, 5))
        self.unit_button = self._button(unit_area, "°C   /   °F", self.toggle_unit)
        self.unit_button.pack(anchor="e")

        search = self._card(page, 15)
        search.pack(fill="x", pady=(0, 10))
        tk.Label(search, text="LOCATION", bg=self.WHITE, fg=self.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        search_row = tk.Frame(search, bg=self.WHITE)
        search_row.pack(fill="x", pady=(8, 0))
        self.entry = tk.Entry(search_row, textvariable=self.query, bg=self.PALE,
                              fg=self.TEXT, insertbackground=self.TEXT,
                              relief="flat", bd=0, font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 9))
        self.entry.bind("<Return>", lambda _event: self.search())
        tk.Label(search_row, text="POSTAL COUNTRY", bg=self.WHITE, fg=self.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 6))
        self.country_box = ttk.Combobox(
            search_row, textvariable=self.country, values=["IN", "US", "GB", "CA", "AU", "DE", "FR"],
            width=5, state="readonly", font=("Segoe UI", 10)
        )
        self.country_box.pack(side="left", padx=(0, 9), ipady=4)
        self.search_btn = self._button(search_row, "Find weather", self.search, True)
        self.search_btn.pack(side="right")

        self.status_label = tk.Label(page, textvariable=self.status, bg=self.BG,
                                     fg=self.MUTED, font=("Segoe UI", 9), anchor="w")
        self.status_label.pack(fill="x", pady=(0, 11))

        # Hero layout: weather art and temperature take visual priority.
        hero = self._card(page, 22)
        hero.pack(fill="x", pady=(0, 13))
        hero_top = tk.Frame(hero, bg=self.WHITE)
        hero_top.pack(fill="x")
        self.place_label = tk.Label(hero_top, text="Your location", bg=self.WHITE,
                                    fg=self.TEXT, font=("Segoe UI", 16, "bold"))
        self.place_label.pack(side="left")
        self.updated_label = tk.Label(hero_top, text="", bg=self.WHITE, fg=self.MUTED,
                                      font=("Segoe UI", 8))
        self.updated_label.pack(side="right")

        hero_body = tk.Frame(hero, bg=self.WHITE)
        hero_body.pack(fill="x", pady=(12, 3))
        art_area = tk.Frame(hero_body, bg=self.WHITE, width=205, height=160)
        art_area.pack(side="left", padx=(0, 22))
        art_area.pack_propagate(False)
        self.hero_icon = tk.Label(art_area, image=self.icon_images.get("partly"),
                                  bg=self.WHITE)
        self.hero_icon.pack(expand=True)
        temperature_area = tk.Frame(hero_body, bg=self.WHITE)
        temperature_area.pack(side="left", fill="y", expand=True, anchor="w")
        self.temp_label = tk.Label(temperature_area, text="—", bg=self.WHITE, fg=self.TEXT,
                                   font=("Segoe UI", 54, "bold"))
        self.temp_label.pack(anchor="w", pady=(9, 0))
        self.condition_label = tk.Label(temperature_area, text="Search a location to begin",
                                        bg=self.WHITE, fg=self.BLUE, font=("Segoe UI", 13))
        self.condition_label.pack(anchor="w", pady=(0, 7))
        self.feels_label = tk.Label(temperature_area, text="Feels like —",
                                    bg=self.WHITE, fg=self.MUTED, font=("Segoe UI", 10))
        self.feels_label.pack(anchor="w")

        metric_row = tk.Frame(hero, bg=self.WHITE)
        metric_row.pack(fill="x", pady=(15, 0))
        self.metric_labels = {}
        for title, key in (("HUMIDITY", "humidity"), ("WIND", "wind"),
                           ("RAINFALL", "rain"), ("HIGH / LOW", "range")):
            tile = tk.Frame(metric_row, bg=self.BLUE_LIGHT, padx=13, pady=10)
            tile.pack(side="left", fill="x", expand=True, padx=(0, 8))
            tk.Label(tile, text=title, bg=self.BLUE_LIGHT, fg=self.BLUE,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value = tk.Label(tile, text="—", bg=self.BLUE_LIGHT, fg=self.TEXT,
                             font=("Segoe UI", 12, "bold"))
            value.pack(anchor="w", pady=(4, 0))
            self.metric_labels[key] = value

        hourly = self._forecast_section(page, "THE NEXT 6 HOURS", 6)
        hourly.pack(fill="x", pady=(0, 12))
        daily = self._forecast_section(page, "THE NEXT 5 DAYS", 5)
        daily.pack(fill="x", pady=(0, 8))

        tk.Label(page, text="Forecast data by Open-Meteo  ·  Conditions are estimates",
                 bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8)).pack(anchor="w")

    def _forecast_section(self, parent, title, count):
        card = self._card(parent, 15)
        tk.Label(card, text=title, bg=self.WHITE, fg=self.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        strip = tk.Frame(card, bg=self.WHITE)
        strip.pack(fill="x", pady=(10, 0))
        slots = []
        for _ in range(count):
            tile = tk.Frame(strip, bg=self.PALE, padx=8, pady=8,
                            highlightthickness=1, highlightbackground="#edf2f5")
            tile.pack(side="left", fill="both", expand=True, padx=(0, 7))
            when = tk.Label(tile, text="—", bg=self.PALE, fg=self.MUTED,
                            font=("Segoe UI", 8, "bold"))
            when.pack()
            icon = tk.Label(tile, text="·", bg=self.PALE, fg=self.BLUE,
                            font=("Segoe UI Symbol", 15))
            icon.pack(pady=2)
            temp = tk.Label(tile, text="—", bg=self.PALE, fg=self.TEXT,
                            font=("Segoe UI", 10, "bold"))
            temp.pack()
            detail = tk.Label(tile, text="", bg=self.PALE, fg=self.MUTED,
                              font=("Segoe UI", 7), wraplength=105)
            detail.pack(pady=(3, 0))
            slots.append((when, icon, temp, detail))
        if count == 6:
            self.hourly_slots = slots
        else:
            self.daily_slots = slots
        return card

    def search(self):
        value = self.query.get().strip()
        if not value:
            self._set_status("Enter a city name or postal code.", True)
            self.entry.focus_set()
            return
        self.search_btn.config(state="disabled", text="Searching…")
        self._set_status(f"Looking up {value}…")
        threading.Thread(target=self._fetch, args=(value,), daemon=True).start()

    def _fetch(self, value):
        try:
            if value.isdigit():
                place = self._postal_lookup(value)
            else:
                response = requests.get(
                    GEOCODING_URL,
                    params={"name": value, "count": 1, "language": "en", "format": "json"},
                    timeout=12
                )
                response.raise_for_status()
                results = response.json().get("results") or []
                if not results:
                    raise ValueError("Location not found. Check the spelling and try again.")
                result = results[0]
                place = {
                    "name": result.get("name", value),
                    "admin1": result.get("admin1", ""),
                    "country": result.get("country", ""),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "timezone": result.get("timezone", "auto")
                }

            params = {
                "latitude": place["latitude"], "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "hourly": "temperature_2m,precipitation_probability,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": 5, "timezone": place.get("timezone", "auto"),
                "wind_speed_unit": "kmh"
            }
            response = requests.get(FORECAST_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            self.root.after(0, self._show_weather, place, data)
        except requests.Timeout:
            self.root.after(0, self._show_error, "The weather service timed out. Please try again.")
        except requests.ConnectionError:
            self.root.after(0, self._show_error, "No network connection. Check your internet and retry.")
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            self.root.after(0, self._show_error, f"Weather service error ({status}).")
        except ValueError as exc:
            self.root.after(0, self._show_error, str(exc))
        except (KeyError, TypeError, IndexError):
            self.root.after(0, self._show_error, "The weather service returned an unexpected response.")
        except Exception:
            self.root.after(0, self._show_error, "Unable to retrieve weather. Please try again.")

    def _postal_lookup(self, postal):
        country = self.country.get().strip().lower()
        response = requests.get(f"{POSTAL_URL}/{country}/{postal}", timeout=12)
        if response.status_code == 404:
            raise ValueError("Postal code not found for the selected country.")
        response.raise_for_status()
        data = response.json()
        places = data.get("places") or []
        if not places:
            raise ValueError("No location was returned for that postal code.")
        location = places[0]
        return {
            "name": location.get("place name", postal),
            "admin1": location.get("state", ""),
            "country": data.get("country", ""),
            "latitude": float(location["latitude"]),
            "longitude": float(location["longitude"]),
            "timezone": "auto"
        }

    def _show_weather(self, place, data):
        self.search_btn.config(state="normal", text="Find weather")
        current = data["current"]
        daily = data["daily"]
        self.last_data = data
        parts = [place.get("name", "")]
        if place.get("admin1") and place["admin1"] != place.get("name"):
            parts.append(place["admin1"])
        if place.get("country"):
            parts.append(place["country"])
        self.place_label.config(text=", ".join(p for p in parts if p))
        self.updated_label.config(text=f"Updated {datetime.now().strftime('%I:%M %p')}")
        description, icon_key = WEATHER.get(current["weather_code"], ("Unknown conditions", "cloud"))
        self.hero_icon.config(image=self.icon_images.get(icon_key))
        self.temp_label.config(text=self._temperature(current["temperature_2m"]))
        self.condition_label.config(text=description)
        self.feels_label.config(text=f"Feels like {self._temperature(current['apparent_temperature'])}")
        self.metric_labels["humidity"].config(text=f"{current['relative_humidity_2m']}%")
        self.metric_labels["wind"].config(text=f"{current['wind_speed_10m']} km/h")
        self.metric_labels["rain"].config(text=f"{current['precipitation']} mm")
        high = self._temperature(daily["temperature_2m_max"][0])
        low = self._temperature(daily["temperature_2m_min"][0])
        self.metric_labels["range"].config(text=f"{high} / {low}")
        self._render_hourly(data)
        self._render_daily(data)
        self._set_status("Weather updated successfully.")

    def _temperature(self, celsius):
        if self.unit.get() == "°F":
            return f"{celsius * 9 / 5 + 32:.0f}°F"
        return f"{celsius:.0f}°C"

    def toggle_unit(self):
        self.unit.set("°F" if self.unit.get() == "°C" else "°C")
        if self.last_data:
            self._show_weather_from_cache()

    def _show_weather_from_cache(self):
        data = self.last_data
        current = data["current"]
        daily = data["daily"]
        self.temp_label.config(text=self._temperature(current["temperature_2m"]))
        self.feels_label.config(text=f"Feels like {self._temperature(current['apparent_temperature'])}")
        self.metric_labels["range"].config(
            text=f"{self._temperature(daily['temperature_2m_max'][0])} / {self._temperature(daily['temperature_2m_min'][0])}"
        )
        self._render_hourly(data)
        self._render_daily(data)

    def _render_hourly(self, data):
        hourly = data["hourly"]
        current_time = data["current"]["time"]
        start = next((i for i, stamp in enumerate(hourly["time"]) if stamp >= current_time), 0)
        for slot_index, widgets in enumerate(self.hourly_slots):
            index = start + slot_index
            if index >= len(hourly["time"]):
                break
            stamp = datetime.fromisoformat(hourly["time"][index])
            desc, icon_key = WEATHER.get(hourly["weather_code"][index], ("Unknown", "cloud"))
            widgets[0].config(text=stamp.strftime("%I %p").lstrip("0"))
            widgets[1].config(text={"clear": "☀", "partly": "◒", "cloud": "☁", "rain": "☂", "snow": "❄", "storm": "ϟ", "fog": "≋"}.get(icon_key, "☁"))
            widgets[2].config(text=self._temperature(hourly["temperature_2m"][index]))
            rain = hourly["precipitation_probability"][index]
            widgets[3].config(text=f"{desc}\nRain {rain}%")

    def _render_daily(self, data):
        daily = data["daily"]
        for index, widgets in enumerate(self.daily_slots):
            stamp = datetime.fromisoformat(daily["time"][index])
            desc, icon_key = WEATHER.get(daily["weather_code"][index], ("Unknown", "cloud"))
            high = self._temperature(daily["temperature_2m_max"][index])
            low = self._temperature(daily["temperature_2m_min"][index])
            rain = daily["precipitation_sum"][index]
            widgets[0].config(text="Today" if index == 0 else stamp.strftime("%a"))
            widgets[1].config(text={"clear": "☀", "partly": "◒", "cloud": "☁", "rain": "☂", "snow": "❄", "storm": "ϟ", "fog": "≋"}.get(icon_key, "☁"))
            widgets[2].config(text=f"{high} / {low}")
            widgets[3].config(text=f"{desc}\n{rain} mm")

    def _set_status(self, message, error=False):
        self.status.set(message)
        self.status_label.config(fg="#bd554d" if error else self.MUTED)

    def _show_error(self, message):
        self.search_btn.config(state="normal", text="Find weather")
        self._set_status(message, True)


def main():
    root = tk.Tk()
    AtmosApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
