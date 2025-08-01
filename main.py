import streamlit as st
import datetime
import requests
from streamlit_extras.let_it_rain import rain
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# ============================================
# ------------- Keys & Constants -------------
# ============================================

# ---------- API Key  ----------
api_key = "40ba2c4079b0ff1737c2229b6bc323ea"



# ================================================
# ------------- Streamlit Web Design -------------
# ================================================


# ---------- Web Tab  ----------
st.set_page_config(page_title="Tanya's Weather App", page_icon="🌦️", layout="wide")


# ---------- Header & Description  ----------
st.title("🌦️  My Weather App 🌦️ ")
st.subheader( "Welcome to Weather App Get real-time weather + city info")
st.divider()


# ================================================
#     ------------- Functions -------------
# ================================================


def get_weather(city,api_key, temp_selection, speed_selection):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        temperature = data['main']['temp']
        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        country = data['sys']['country']
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        icon = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"


        # ----- Results Units Conversion ------

        if temp_selection == "°F":
            temperature = round((temperature * 9/5) + 32,2)

        if speed_selection == "km/h":
            wind_speed = round((wind_speed * 3.6), 2)

        #----------------------------------------


        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.success(f"Weather for {city.title()}, {country}")
            st.write(f"📅 **Date:** {datetime.date.today().strftime('%A, %d %B %Y')}")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                st.image(icon_url)

            with col2:
                st.metric("🌡️ Temperature", f"{temperature} {temp_selection}")
                st.metric("💧 Humidity", f"{humidity}%")
                st.metric("💨 Wind Speed", f"{wind_speed} {speed_selection}")
                st.write(f"🌥️ **Condition:** {weather_desc.capitalize()}")

        # ----------- Emoji Rain Effects--------------------
        # Example: weather_main = "Rain" (from your weather API)
            with col3:
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


    else:
        st.error("⚠️ Could not retrieve data. Please check the city name.")




# ---------------- Get Forcast ------------------------

def get_weekly_forcast (city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        print("Could not retrieve forecast data. Please try again later.")
        exit()

    forcast_data = response.json()

    st.subheader("🌤️ 5-Day Forecast")

    daily_data ={} # define empty list, get days from json

    for item in forcast_data["list"]:
        date = datetime.datetime.fromtimestamp(item["dt"]).date() #unix notation convertion
        if date not in daily_data:
            daily_data[date] = [] #group by day, and create empty list for each day
        daily_data[date].append(item)  # populate with the relevant item

    # Limit to next 5 days
    days = list(daily_data.keys())[:5]
    cols = st.columns(len(days))

    dates = []
    daily_temps = []

    for i, day in enumerate(days):
        with cols[i]:
            entries = daily_data[day]
            temps = [entry["main"]["temp"] for entry in entries]
            descriptions = [entry["weather"][0]["description"] for entry in entries]
            icons = [entry["weather"][0]["icon"] for entry in entries]

            avg_temp = round(sum(temps) / len(temps), 1)
            description = max(set(descriptions), key=descriptions.count)
            icon_url = f"http://openweathermap.org/img/wn/{icons[0]}@2x.png"

            st.markdown(f"### {day.strftime('%a %d %b')}")
            st.image(icon_url)
            st.write(f"**{description.capitalize()}**")
            st.write(f"🌡️ Average Temperature : {avg_temp} °C")

            dates.append(day.strftime('%a %d %b'))
            daily_temps.append(avg_temp)


# ----- Plot using the forcast results :

    df = pd.DataFrame({"Date": dates,"Avg Temperature (°C)": daily_temps}) # set df
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x="Date", y="Avg Temperature (°C)", marker="o")
    plt.title("Weekly Average Temperature")
    plt.xlabel("Date")
    plt.ylabel("Avg Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)

    st.pyplot(plt)
#========================================== Main ========================================================



# ================================================
#     ------------- User Inputs: -------------
# ================================================

st.info("Enter a city name and complete your unit preferences :")

#----- City by user:---

col_input, col_utemp, col_uspeed  = st.columns([0.4, 0.2, 0.6 ])
with col_input:
    city = st.text_input("Enter a city name and press 'Enter' : ", placeholder="For Example: Haifa").strip().lower()

#---- Preferred Units  ---

with col_utemp :

    unit_temp = ["°C", "°F"]
    temp_selection = st.segmented_control("Select Temperature Units : ", unit_temp, selection_mode="single")
    st.markdown(f"Your selected options: {temp_selection}.")
    if not temp_selection:
        temp_selection = "°C"

with col_uspeed :
    unit_speed = ["m/s", "km/h"]
    speed_selection = st.segmented_control("Select Wind Speed Units :", unit_speed, selection_mode="single")
    st.markdown(f"Your selected options: {speed_selection}.")
    if not speed_selection:
        speed_selection = "km/h"


# ---------- API Execution ----------
if len(city) == 0:
    get_weather("Haifa" ,api_key, "°C", "m/s")
else:
    with st.spinner("Loading..."):
        get_weather(city,api_key, temp_selection, speed_selection)
        get_weekly_forcast(city, api_key)

st.divider()

# ---------- FOOTER ----------
st.divider()
st.caption("Made with Streamlit • Weather from OpenWeatherMap • Info from Wikipedia")
