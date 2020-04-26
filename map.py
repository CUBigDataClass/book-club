# import packages
import pandas as pd
import folium
import json
import webbrowser
import branca
from datetime import datetime, timedelta
from pandas.io.json import json_normalize
import branca.colormap as cm

# create pandas dataframe with covid case/death data and FIPS info
county_data = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
df = pd.read_csv(county_data, na_values=[' '])

# fix FIPS code column (fips -> FIPS_Code)
df.columns = ['date', 'county', 'state', 'FIPS_Code', 'cases', 'deaths']

# fix NYC FIPS code
df['FIPS_Code'] = df['FIPS_Code'].astype(str)
df.loc[(df.county == 'New York City'), 'FIPS_Code']='36061.0'

# convert FIPS codes to strings in order to match geojson data
df['FIPS_Code'] = df['FIPS_Code'].astype(str)
df = df[df.FIPS_Code != 'nan']
df['FIPS_Code'] = df['FIPS_Code'].astype(float).astype(int).astype(str)
df = df[df.county != 'Unknown']

df['FIPS_Code'] = df['FIPS_Code'].astype(str)
df.loc[(df.county == 'New York City'), 'FIPS_Code']='36061.0'
df['FIPS_Code'] = df['FIPS_Code'].astype(float).astype(int).astype(str)

#########################
# add this part with front end linkage
# set "today" as chosen date

df['date'] = pd.to_datetime(df['date'])
recent_date = df['date'].max()
chosen_date = str(recent_date)

df = df[df.date == chosen_date]
df['date'] = df['date'].astype(str)

#########################

counties = 'us-counties.json'

# bins to control the color-coding
max_cases = df['cases'].max()
bins = list([0, max_cases*.0001, max_cases*.001, max_cases*.01, max_cases*.1, max_cases])

m = folium.Map(location = [39.8282, -98.5795], zoom_start = 4)

choropleth = folium.Choropleth(counties, data = df, columns = ['FIPS_Code', 'cases'],
                  key_on = 'feature.id', fill_color = "YlOrRd", fill_opacity = 0.7, line_opacity = 0.5,
                  legend_name = 'COVID-19 cases', highlight = True, bins = bins, reset = True)

choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['name'], aliases = ['County:']))

choropleth.add_to(m)

#########################
# create markers for each county
# json_df = pd.read_json(counties)
# json_df['features'] = json_df['features'].astype(str)
# json_df.features.str.split(expand=True)
# print(json_df)

#########################

m.save('new.html')
webbrowser.open('new.html')
