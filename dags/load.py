import json
import pendulum
from airflow.decorators import dag, task
from airflow.models import Variable
import os
import pandas as pd
import psycopg2
import requests
import base64

streaming_history = Variable.get("streaming_history")
spotify_id = Variable.get("spotify_id")
spotify_secret = Variable.get("spotify_secret")

@dag(
    schedule=None,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["spotify"],
)
def taskflow_api():
    @task()
    def extractStreamingHistory():
      obj = os.scandir(streaming_history)
      combined_df = pd.DataFrame()
      for entry in obj:
          print(entry)
          if entry.is_file() and entry.name.startswith("StreamingHistory"):
              df = pd.read_json(entry.path)
              combined_df = pd.concat([combined_df,df], ignore_index=True)
          elif entry.is_file() and entry.name.startswith("Marquee"):
              marquee = pd.read_json(entry.path)
      combined_df.rename(columns = {'endTime':'end_time', 'trackName': 'track_name', 'msPlayed': 'ms_played', 'artistName':'artist_name'}, inplace = True)
      combined_df.to_sql('streaming_history', con='postgresql://postgres:postgres@db:5432/spotify', if_exists='replace', 
                index=False) 
      if marquee is not None:
        marquee.rename(columns = {'artistName':'artist_name'}, inplace = True)
        marquee.to_sql('marquee', con='postgresql://postgres:postgres@db:5432/spotify', if_exists='replace', 
                  index=False) 
    
    @task()
    def extractArtists():
      connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="db",
                                      port="5432",
                                      database="spotify")
      sql_query = pd.read_sql_query ('''
                                    SELECT
                                    *
                                    FROM streaming_history
                                    ''', connection)
      new_df = pd.DataFrame(sql_query, columns = ['artist_name'])
      artists = new_df.loc[:,['artist_name']].drop_duplicates()
      artists['image'] = ''
      artists['id'] = ''
      artists['url'] = ''
      artists.reset_index( inplace=True, drop=True)
      client_id = spotify_id
      client_secret = spotify_secret
      encoded = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")
      headers = {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization": "Basic " + encoded
      }
      payload = {
          "grant_type": "client_credentials"
      }
      response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)
      access_token = response.json()['access_token']
      for index, row in artists.iterrows():
          headers = {
          "Authorization": "Bearer " + access_token
          }
          search_params = {
              'type': 'artist',
              'q': row['artist_name'],
          }
          print(index)
          response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=search_params)
          if len(response.json()['artists']['items']) == 0:
              continue
          artists.at[index,'id'] = response.json()['artists']['items'][0]['id']
          if len(response.json()['artists']['items'][0]['images']) != 0:
              artists.at[index,'image'] = response.json()['artists']['items'][0]['images'][0]['url']
          artists.at[index,'url'] = response.json()['artists']['items'][0]['external_urls']['spotify']
          
      artists.to_sql('artists', con='postgresql://postgres:postgres@db:5432/spotify', if_exists='replace', 
                index=False) 

    extractStreamingHistory() >> extractArtists()

taskflow_api()
