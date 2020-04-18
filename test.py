# import packages
import pandas as pd
import folium
import json
import vincent

# data to be read in
county_data = r'current_covid.csv'
county_geo = r'us-counties.json'

with open(county_geo, 'r') as f:
    get_id = json.load(f)

county_codes = [x["id"] for x in get_id["features"]]
county_df = pd.DataFrame({'FIPS_Code': county_codes}, dtype=str)

# create pandas dataframe with covid case/death data and FIPS info
df = pd.read_csv(county_data, na_values=[' '])
df['FIPS_Code'] = df['FIPS_Code'].astype(str)
df = df[df.FIPS_Code != 'nan']
df['FIPS_Code'] = df['FIPS_Code'].astype(str)

df['FIPS_Code'] = df['FIPS_Code'].astype(str).astype(float).astype(int)
county_df['FIPS_Code'] = county_df['FIPS_Code'].astype(str).astype(float).astype(int)

# print('df:\n', df.dtypes)
# print('')
# print('')
# print('')
# print('county_df:\n', county_df.dtypes)
# print('')
# print('')
# print('')


merged = pd.merge(df, county_df, on='FIPS_Code', how='inner')
# print(merged)

m = folium.Map(location = [39.8282, -98.5795], zoom_start = 4)
folium.Choropleth(county_geo, data = merged, columns = ['FIPS_Code', 'cases'],
                  fill_color = 'YlGnBu', line_opacity = 0.5,
                  legend_name = 'COVID-19 cases').add_to(m)

m.save('example.html')
