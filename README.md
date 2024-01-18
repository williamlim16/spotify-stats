# Spotify Insight Analyzer

## Introduction
The Spotify Insight Analyzer is a personal data analysis project designed to provide users with a deeper understanding of how Spotify uses their data to curate personalized music experiences. By gathering and analyzing individual Spotify user data, the project aims to shed light on the extent to which Spotify "knows" its users and the patterns underlying music recommendations.

## Instruction
Run these commands to initialize the necessary environment.
```sh
git clone https://github.com/williamlim16/spotify-stats.git
cd spotify-stats
docker compose up airflow-init
docker compose up -d 
```
After that, open http://localhost:8081 and and Adminer page should be accessible. These credentials should work right out of the box. But, you can modify these credentials with POSTGRES_USER POSTGRES_PASSWORD variable in docker-compose file. Through the UI, create a new database "spotify".

- user: postgres
- password: postgres
- url: db

Open a new tab http://localhost:8080 and sign in with credentials. Head to Admin > Variables and create theese three variables. You can create an id and secret through this [link](https://developer.spotify.com/dashboard). If you do not have streaming history file, you can request it to Spotify through this [link](https://support.spotify.com/au/article/data-rights-and-privacy-settings/). After a few seconds, try to refresh the page. The error should go away after inputting these three variables. Streaming history should be pointing to your history file.

- spotify_id: spotify id string.
- spotify_secret: spotify secret string.
- streaming_history: path to streaming history file.

Finally, we can execute the code by pressing play button on the Apache Airflow dashboard. The process should start and progressively building your database. After all of the process are finished, you can see the populated data in the Adminer.

