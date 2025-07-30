import streamlit as st
import datetime
import requests
import wikipedia
from streamlit_extras.let_it_rain import rain

# ============= Keys & Constants =============
api_key = "40ba2c4079b0ff1737c2229b6bc323ea"
default_city = "London"

# ---------- Web Tab  ----------
st.set_page_config(page_title="Tanya's Weather App", page_icon="🌦️", layout="wide")

# ---------- HEADER ----------
st.title(" 🌦️ My Weather App")
st.subheader( "Welcome to Weather App Get real-time weather + city info")
st.divider()

# ---------- API Key  ----------

# Define the weather display function outside the if-block
def show_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        temperature = data['main']['temp']
        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        icon_code = data['weather'][0]['icon']
        country = data['sys']['country']
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.success(f"Weather for {city.title()}, {country}")
            st.write(f"📅 **Date:** {datetime.date.today().strftime('%A, %d %B %Y')}")

            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(icon_url)
            with col2:
                st.metric("🌡️ Temperature", f"{temperature} °C")
                st.metric("💧 Humidity", f"{humidity}%")
                st.metric("💨 Wind Speed", f"{wind_speed} m/s")
                st.write(f"🌥️ **Condition:** {weather_desc.capitalize()}")

        # Emoji Rain Effects
        # Example: weather_main = "Rain" (from your weather API)

        if st.button("🌈 Show Weather Animation"):
            if "rain" in weather_main.lower():
                rain(emoji="🌧️", font_size=36, falling_speed=5)
            elif "snow" in weather_main.lower():
                rain(emoji="❄️", font_size=36, falling_speed=4)
            elif "clear" in weather_main.lower():
                rain(emoji="☀️", font_size=36, falling_speed=3)
            elif "cloud" in weather_main.lower():
                rain(emoji="☁️", font_size=36, falling_speed=2)

        with right_col:
            st.subheader(f"🗺️ {city.title()} on the Map")
            st.map(data={"lat": [lat], "lon": [lon]})

            st.subheader("📘 Did you know ?")
            try:
                search_term = f"{city}, {country}"
                summary = wikipedia.summary(search_term, sentences=3)
                st.write(summary)

            except wikipedia.exceptions.PageError:
                st.warning(f"No Wikipedia page found for '{city}, {country}'.")
    else:
        st.error("⚠️ Could not retrieve data. Please check the city name.")


#==================================== Main =============================================================

# ---------- INPUTS ----------

#----- City by user:---
city = st.text_input("Enter a city name and press 'Enter' : ", placeholder="For Example: Haifa").strip().lower()

#---- Preferred Units  ---
unit_temp = ["°C", "°F"]
selection = st.segmented_control(
    "Select Temperature Units : ", unit_temp, selection_mode="single"
)
st.markdown(f"Your selected options: {selection}.")

unit_speed = ["m/s", "km/h"]
selection = st.segmented_control(
    "Select Wind Speed Units :", unit_speed, selection_mode="single"
)
st.markdown(f"Your selected options: {selection}.")


# ---------- API Execution ----------
if len(city) == 0:
    st.info("Enter a city name above to view the weather and city info.")
    show_weather(default_city, api_key)
else:
    with st.spinner("Loading..."):
        show_weather(city, api_key)


# ---------- FOOTER ----------
st.divider()
st.caption("Made with Streamlit • Weather from OpenWeatherMap • Info from Wikipedia")
