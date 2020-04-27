# import packages
import pandas as pd
import folium
import json
import webbrowser
import branca
from datetime import datetime, timedelta
from pandas.io.json import json_normalize
import branca.colormap as cm
import geopandas as gpd
import requests
from folium.features import GeoJson, GeoJsonTooltip

#############################################################
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
df['FIPS_Code'] = df['FIPS_Code'].astype(float).astype(int)

#############################################################
# add this part with front end linkage
# set "today" as chosen date

df['date'] = pd.to_datetime(df['date'])
recent_date = df['date'].max()
chosen_date = str(recent_date)

df = df[df.date == chosen_date]
df['date'] = df['date'].astype(str)
# print(df)

#############################################################
# geopandas dataframe holding the geometries

response = requests.get(r"https://gist.githubusercontent.com/wrobstory/5586482/raw/6031540596a4ff6cbfee13a5fc894588422fd3e6/us-counties.json")
data = response.json()
county_geo_name = gpd.GeoDataFrame.from_features(data, crs='EPSG:4326')
county_geo_FIPS = gpd.GeoDataFrame.from_file("https://gist.githubusercontent.com/wrobstory/5586482/raw/6031540596a4ff6cbfee13a5fc894588422fd3e6/us-counties.json")
del county_geo_FIPS['geometry']

county_geo = county_geo_name.join(county_geo_FIPS, rsuffix='_fromFIPS')
del county_geo['name_fromFIPS']
county_geo['id'] = county_geo['id'].astype(int)
# print(county_geo)

#############################################################
#merge the two dataframes
county_geo_cases_merged = county_geo.merge(df, how='left', left_on='id', right_on='FIPS_Code')

del county_geo_cases_merged['county']
del county_geo_cases_merged['FIPS_Code']

county_geo_cases_merged['cases'] = county_geo_cases_merged['cases'].fillna(0.0).astype(int)
county_geo_cases_merged['deaths'] = county_geo_cases_merged['deaths'].fillna(0.0).astype(int)

# print(county_geo_cases_merged)

#############################################################
# mapping the dataframe created above

max_cases = county_geo_cases_merged['cases'].quantile(1)

colormap = branca.colormap.LinearColormap(
    vmin=0,
    vmax=max_cases,
    colors=['green', 'yellowgreen', 'yellow', 'orange', 'orangered', 'red'],
    index=[0, 10, 100, 1000, 10000, max_cases],
    caption="COVID-19 Cases",
)

m = folium.Map(location=[38, -97.6], zoom_start=5)

tooltip = GeoJsonTooltip(
    fields=['name', 'cases', 'deaths'],
    aliases=['County', 'Cases', 'Deaths'],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """
)


g = folium.GeoJson(
    county_geo_cases_merged,
    style_function=lambda x: {
        "fillColor": colormap(x["properties"]["cases"])
        if x["properties"]["cases"] is not None
        else "transparent",
        "color": "black",
        "fillOpacity": 0.7
    },
    smooth_factor=.1,
    tooltip=tooltip
).add_to(m)

colormap.add_to(m)

m.save('new.html')
webbrowser.open('new.html')
