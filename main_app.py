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


def main():
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
    # Create the City and State header
    #------------------------------------------------------------
    st.markdown(f'# {city_state}')
    st.markdown('<div class="dropdown-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="dropdown-divider"></div>', unsafe_allow_html=True)
    
    #------------------------------------------------------------
    # Loop over each forecast time of day and print
    #------------------------------------------------------------
    for i,row in daily_forecast.iterrows():
        highlow = 'High: ' if row.isDaytime else 'Low: '
        st.subheader(row['name'])
        st.image(row.icon)
        st.markdown(f'**{highlow}**{row.temperature} {row.temperatureUnit}') # -- ***{shortinfo}***')
        st.markdown(row.detailedForecast)
        st.markdown('<div class="dropdown-divider"></div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
    
