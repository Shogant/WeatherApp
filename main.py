import streamlit as st
import datetime
import requests
from streamlit_extras.let_it_rain import rain
import pandas as pd


# ================================================
# ------------- Keys & Constants -------------
# ================================================

# ---------- API Key  ----------
api_key = "40ba2c4079b0ff1737c2229b6bc323ea"



# ================================================
# ------------- Streamlit Web Design -------------
# ================================================


# ---------- Web Tab  ----------
st.set_page_config(page_title="Tanya's Weather App", page_icon="🌦️", layout="wide")


# ---------- Header & Description  ----------
st.title("🌦️  My Weather App 🌦️ ")
st.markdown("#### Clouds are grey, skies can be blue,")
st.markdown("#### What’s your city’s weather? Let’s walk you through ! 📲✨.")
st.divider()


# ================================================
#     ------------- Functions -------------
# ================================================
# 1. get_weather - daily weather parameters for location
# 2. get_weekly_forcast - 5 days forcast


# ------------- Function (1) : temp conversion  -----------------------------------------------------

def convert_temperature(temp_celsius, unit):
    if unit == "°F":
        return round((temp_celsius * 9/5) + 32, 1)
    return round(temp_celsius, 1)

# ------------- Function (2) : get_weather -----------------------------------------------------

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


        temperature = convert_temperature(temperature, temp_selection)

        #     temperature = round((temperature * 9/5) + 32,2)

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

        # ----------- Streamlit Extra - Emoji Rain Effects --------------------
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

        get_weekly_forcast(city, api_key, temp_selection)

    else:
        st.error("⚠️ Could not retrieve data. Please check the city name.")




# ------------- Function (2) : get_weekly_forcast -----------------------------------------------------

def get_weekly_forcast (city, api_key, temp_selection):

    # API result is 5 day forcast in 3 hrs intervals:
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        print("Could not retrieve forecast data. Please try again later.")
        exit()

    forcast_data = response.json()

    st.divider()
    st.subheader( " 5-Day Forecast View 📆 :")

# -------- JSON hourly results into days data -----

    daily_data ={} # define empty dictionary, group JSON data per day:

    for item in forcast_data["list"]:
        date = datetime.datetime.fromtimestamp(item["dt"]).date() #unix timestamp convertion to date
        if date not in daily_data:
            daily_data[date] = []  #if new day - create an empty list for it, to be populated with the 3 hr data.
        daily_data[date].append(item)  # populate with item.

    # Limit to 5 days forcast :
    days = list(daily_data.keys())[:5]
    cols = st.columns(len(days))

    # # create for cast view like in the news : ##
    dates = []
    daily_temps = []

    for i, day in enumerate(days):
        with cols[i]:
            entries = daily_data[day]
            temps = [entry["main"]["temp"] for entry in entries] # all temps per day
            descriptions = [entry["weather"][0]["description"] for entry in entries] # all descriptions per day
            icons = [entry["weather"][0]["icon"] for entry in entries] # all icons per day

            avg_temp = round(sum(temps) / len(temps), 1) #avg temp
            avg_temp = convert_temperature(avg_temp, temp_selection)

            description = max(set(descriptions), key=descriptions.count) # most repeatable desc per day
            icon = max(set(icons), key=icons.count) #most repeatable icon
            icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png" # get that icon per url

            st.markdown(f"### {day.strftime('%a %d %b')}")
            st.image(icon_url)
            st.write(f"**{description.capitalize()}**")
            st.write(f" Average Temperature : {avg_temp} {temp_selection}")

            dates.append(day.strftime('%d/%m/%y')) # switch format fot the chart
            daily_temps.append(avg_temp)


# ----- Plot using the forcast results :
    st.divider()
    st.subheader( "Temperature Trend View Per Day 📈 :")


    st.markdown(f"Temperature [{temp_selection}]")
    df = pd.DataFrame({
        "Date": dates,
        "Avg Temperature": daily_temps
    })

    df.set_index("Date", inplace=True)  # x- date, Y- temps
    st.line_chart(df)

    with st.container():
        left, center, right = st.columns([2, 1, 1])
        with center:
            st.write("day")

# =======================================================================================================
#========================================== Main ========================================================
# =======================================================================================================


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

st.divider()

# ---------- FOOTER ----------
st.divider()
st.caption("• Weather from OpenWeatherMap • Made with Streamlit | 2025 ")
