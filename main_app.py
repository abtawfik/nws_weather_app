'''
Simple weather app that uses National Weather Service official forecast
images and forecast API

@author - Ahmed Tawfik
'''
import streamlit as st
import requests
import pandas as pd
import numpy as np
import geopy
from geopy.geocoders import Nominatim
from collections import namedtuple


#------------------------------------------------------------
# Create input address bar that takes an address
#------------------------------------------------------------
default_address = 'Durham, NC'
address  =  st.sidebar.text_input('Enter Address:', default_address)

#------------------------------------------------------------
# Pass address through geopy to get lat and lon
#------------------------------------------------------------
geoloc = Nominatim(user_agent='MyNWS_Emulator')
location = geoloc.geocode(address)
if location is None or not isinstance(location, geopy.location.Location):
    #st.sidebar.exception(ValueError('Bad address entered. Try a zipcode or a more specific address.'))
    #st.sidebar.exception('Bad address entered. Try a zipcode or a more specific address.')
    st.sidebar.info('Bad address entered. Try a zipcode or a more specific address.')
    st.sidebar.warning('...Picking random address...')
    lat, lon = np.random.uniform(30,55), np.random.uniform(-120,-70)
else:
    lat, lon = location.latitude, location.longitude

#------------------------------------------------------------
# NWS API URL
#------------------------------------------------------------
api_base_url = 'https://api.weather.gov'

#------------------------------------------------------------
# Get type of forecast URLs and nearest station metadata
#------------------------------------------------------------
metadata_response = requests.get(f'{api_base_url}/points/{lat},{lon}')

#------------------------------------------------------------
# Check that good data was returned
#------------------------------------------------------------
if metadata_response.status_code != 200:
    st.warning('Service is currently unavailable to try a different address or refresh the page')

#------------------------------------------------------------
# Get daily forecast
#------------------------------------------------------------
metadata           = metadata_response.json()
daily_forecast_url = metadata['properties']['forecast']

#------------------------------------------------------------
# Location info of MET office
#------------------------------------------------------------
location_info    = metadata['properties']['relativeLocation']['properties']
Location_Info    = namedtuple( 'Location', sorted(location_info) )
current_location = Location_Info(**location_info)
city_state       = f'{current_location.city}, {current_location.state}'

#------------------------------------------------------------
# Get the daily forecast info
# and check that there is a valid response (200)
#------------------------------------------------------------
daily_forecast_response = requests.get(daily_forecast_url)
if daily_forecast_response.status_code != 200:
    st.warning('Service is currently unavailable to try a different address or refresh the page')

#------------------------------------------------------------
# Parse the JSON response to a pandas dataframe 
#------------------------------------------------------------
daily_forecast_data = daily_forecast_response.json()
daily_forecast      = pd.DataFrame( daily_forecast_data['properties']['periods']).sort_values(by='number')

#------------------------------------------------------------
# Extract the relevant forecast information we want to display
#------------------------------------------------------------
names     = daily_forecast.name.values
pictures  = daily_forecast.icon.values
shortinfos= daily_forecast.shortForecast.values
details   = daily_forecast.detailedForecast.values
temps     = daily_forecast.temperature
units     = daily_forecast.temperatureUnit.iloc[0]
timeofday = daily_forecast.isDaytime.values

#------------------------------------------------------------
# Create the City and State header
#------------------------------------------------------------
st.markdown(f'<h1>{city_state}</h1>', unsafe_allow_html=True)
st.markdown('<div class="dropdown-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="dropdown-divider"></div>', unsafe_allow_html=True)

#------------------------------------------------------------
# Loop over each forecast time of day and print
#------------------------------------------------------------
for name, picture, shortinfo, detail, temp, tod in zip(names, pictures, shortinfos, details, temps, timeofday):
    Current_Day = f'''#### {name} 
    ![weather image]({picture} "{shortinfo}") #### {shortinfo} -- {temp} {units}
    {detail}'''
    #st.markdown(Current_Day)
    highlow = 'High: ' if tod else 'Low: '
    st.subheader(name)
    st.image(picture)
    st.markdown(f'**{highlow}**{temp} {units}') # -- ***{shortinfo}***')
    st.markdown(detail)
    st.markdown('<div class="dropdown-divider"></div>', unsafe_allow_html=True)


