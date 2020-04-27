#GCP Imports
from flask import Flask, render_template, request, Response
from google.cloud import storage

import logging
import os

# import packages
import pandas as pd
import folium
import json
import webbrowser
import branca

from datetime import datetime, timedelta
from pandas.io.json import json_normalize
import branca.colormap as cm


# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     """Uploads a file to the bucket."""
#     # bucket_name = "your-bucket-name"
#     # source_file_name = "local/path/to/file"
#     # destination_blob_name = "storage-object-name"

#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)

#     blob.upload_from_filename(source_file_name)

#     print(
#         "File {} uploaded to {}.".format(
#             source_file_name, destination_blob_name
#         )
#     )

# def get(self):
#     bucket_name = os.environ.get(
#         'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

#     self.response.headers['Content-Type'] = 'text/plain'
#     self.response.write(
#         'Demo GCS Application running from Version: {}\n'.format(
#             os.environ['CURRENT_VERSION_ID']))
#     self.response.write('Using bucket name: {}\n\n'.format(bucket_name))

# def create_file(self, filename):
#   """Create a file.

#   The retry_params specified in the open call will override the default
#   retry params for this particular file handle.

#   Args:
#     filename: filename.
#   """
#   self.response.write('Creating file %s\n' % filename)

#   write_retry_params = gcs.RetryParams(backoff_factor=1.1)
#   gcs_file = gcs.open(filename,
#                       'w',
#                       content_type='text/plain',
#                       options={'x-goog-meta-foo': 'foo',
#                                'x-goog-meta-bar': 'bar'},
#                       retry_params=write_retry_params)
#   gcs_file.write('abcde\n')
#   gcs_file.write('f'*1024*4 + '\n')
#   gcs_file.close()
#   self.tmp_filenames_to_clean_up.append(filename)

# def download_blob(bucket_name, source_blob_name, destination_file_name):
#     """Downloads a blob from the bucket."""
#     # bucket_name = "your-bucket-name"
#     # source_blob_name = "storage-object-name"
#     # destination_file_name = "local/path/to/file"

#     storage_client = storage.Client()

#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(source_blob_name)
#     blob.download_to_filename(destination_file_name)

#     print(
#         "Blob {} downloaded to {}.".format(
#             source_blob_name, destination_file_name
#         )
#     )


app = Flask(__name__)

#CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

@app.route('/', methods = ['POST', 'GET'])
def root():

    if request.method == 'POST':
      result = request.form.get('selected-date')
    else:
        result = "2020-02-10"

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

    today = result

    df = df[df.date == today]
    df['date'] = df['date'].astype(str)

    #########################

    counties = 'us-counties.json'

    # bins to control the color-coding
    # bins = list(df['cases'].quantile([0, .5, .75, .8, .85, .997, .998, .999, 1]))
    max_cases = df['cases'].max()
    bins = list([0, max_cases*.0001, max_cases*.001, max_cases*.01, max_cases*.1, max_cases])

    m = folium.Map(location = [39.8282, -98.5795], zoom_start = 4)

    choropleth = folium.Choropleth(counties, data = df, columns = ['FIPS_Code', 'cases'],
                  key_on = 'feature.id', fill_color = "YlOrRd", fill_opacity = 0.7, line_opacity = 0.5,
                  legend_name = 'COVID-19 cases', highlight = True, bins = bins, reset = True)

    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['name'], aliases = ['County:']))

    choropleth.add_to(m)

    #m.save( "./tmp/new6.html")

    #upload_blob("please-work-ill-pay-you.appspot.com", "./tmp/new6.html", "new6.html")

    return render_template('index.html', result = result, map=m._repr_html_())


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)