# TFT_Crawler

This Python script is designed to interact with the Riot Games API, particularly for the Teamfight Tactics (TFT) game mode. It efficiently handles rate limits imposed by the API and fetches various types of game data including summoner IDs, PUUIDs, match IDs, and detailed match data.

## Features

* Rate Limit Handling: Uses a custom rate limiter to manage API requests within the limits set by Riot Games.
* Data Retrieval: Gathers data such as summoner rankings, player statistics, and match details.
* Data Persistence: Saves and loads data to and from local files to avoid unnecessary API calls and to provide offline data analysis capabilities.

## Setup

* API Key: You need a Riot Games API key to fetch data. Place your API key in a file named api_key.txt in the same directory as the script.
* Libraries
  * requests
  * json
  * time
 
## Contributing

Go ahead and get forkin wild. This is really small right now, and I wnat to update it over time. If you want to help, I'm here for fun and to learn. 
