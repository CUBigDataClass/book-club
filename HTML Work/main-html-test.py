#GCP Imports
from flask import Flask, render_template, request

# import packages
import os
import pandas as pd
import folium
import json
import webbrowser
import branca

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def root():

    if request.method == 'POST':
      result = request.form
    else:
        result = "0000-00-00"

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

    today = '2020-04-20'

    df = df[df.date == today]
    df['date'] = df['date'].astype(str)

    #########################

    counties = 'us-counties.json'

    # bins to control the color-coding
    # bins = list(df['cases'].quantile([0, .5, .75, .8, .85, .997, .998, .999, 1]))
    bins = list([0, 10, 100, 1000, 10000, 100000, 200000])

    m = folium.Map(location = [39.8282, -98.5795], zoom_start = 4)

    folium.Choropleth(counties, data = df, columns = ['FIPS_Code', 'cases'],
                    key_on = 'feature.id', fill_color = 'YlOrRd', fill_opacity = 0.7, line_opacity = 0.5,
                    legend_name = 'COVID-19 cases', bins = bins, reset = True).add_to(m)

    # map_path = os.path.abspath(__file__) + "\\templates"

    m.save( "./static/new.html")

    iframe = "/templates/new.html"

    return render_template('index.html', iframe = iframe, result = result)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)