# import packages
import pandas as pd
import folium
import json
import webbrowser


# create pandas dataframe with covid case/death data and FIPS info
df = pd.read_csv('current_covid.csv', na_values=[' '])

# convert FIPS codes to strings in order to match geojson data
df['FIPS_Code'] = df['FIPS_Code'].astype(str)
df = df[df.FIPS_Code != 'nan']
df['FIPS_Code'] = df['FIPS_Code'].astype(float).astype(int).astype(str)

counties = 'us-counties.json'

# bins to control the color-coding
bins = list(df['cases'].quantile([0, .2, .5, .8, 1]))

m = folium.Map(location = [39.8282, -98.5795], zoom_start = 4)

folium.Choropleth(counties, data = df, columns = ['FIPS_Code', 'cases'],
                  key_on = 'feature.id', fill_color = 'YlOrRd', fill_opacity = 0.7, line_opacity = 0.5,
                  legend_name = 'COVID-19 cases', bins = bins, reset = True).add_to(m)

m.save('new.html')
webbrowser.open('new.html')
