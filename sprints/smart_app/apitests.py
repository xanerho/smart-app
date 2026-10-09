# All code here is taken from the API website's, but I have no idea if that was allowed :p
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

def get_weather():
	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": 51.5085,
		"longitude": -0.1257,
		"daily": ["temperature_2m_mean", "precipitation_sum", "relative_humidity_2m_mean", "wind_speed_10m_mean"],
		"timezone": "Europe/London",
	}
	responses = openmeteo.weather_api(url, params = params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]

	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
	daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
	daily_wind_speed_10m_mean = daily.Variables(3).ValuesAsNumpy()

	daily_data = {
		"date": pd.date_range(
			start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
			end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
			freq = pd.Timedelta(seconds = daily.Interval()),
			inclusive = "left"
		).tz_convert(response.Timezone().decode()).strftime("%d-%m-%Y")
	}

	daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
	daily_data["precipitation_sum"] = daily_precipitation_sum
	daily_data["wind_speed_10m_mean"] = daily_wind_speed_10m_mean

	daily_dataframe = pd.DataFrame(data = daily_data)
	return daily_dataframe