from dotenv import load_dotenv
import os
import requests

load_dotenv()
tmdb_api_key=os.getenv("TMDB_API_KEY")

base="https://api.themoviedb.org/3"

tv_response=requests.get(url=f"{base}/discover/tv",
                       params={"api_key":tmdb_api_key,
                               "include_adult":False,
                               "language":"en-US",
                               "sort_by": "vote_average.desc",
                               "vote_count.gte":500,
                               "vote_average.gte":7.8,
                               "without_genres":"99,10763,10764,10767", # excluding documentary(99),news(10763),reality(10764),talk(10767)
                               "page":15})
tv=tv_response.json()

print("Total results:",tv["total_results"])
print("Total pages:",tv["total_pages"])

for show in tv["results"]:
    print(show["name"],"|", show["id"],"|",show["vote_average"])

#To see all genres (their ids and corresponding names) you can run the below code

#genre_response=requests.get(url=f"{base}/genre/tv/list",params={"api_key":tmdb_api_key})
#genre=genre_response.json()
#print(genre["genres"])



