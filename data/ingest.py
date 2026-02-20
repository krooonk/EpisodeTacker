"""
ingest.py
---------
One-time data ingestion script to fetch TV series from TMDB and prepare for database insertion.

Fetches from TMDB:
- Series details (title, description, ratings, etc.)
- All seasons and episodes for finished shows only
- Cast and crew (top 10 actors, creators)
- Poster images (downloaded to posters/ directory)
- Genre mappings

Filters:
- Only includes shows with status "Ended" or "Canceled"
- Minimum 500 vote count, 7.8+ vote average
- Excludes Documentary, News, Reality, Talk genres

Output:
- initial_ingest.json with all enriched show data
- posters/ folder with all poster images
- Checkpoint files every 50 shows for recovery

As of the last run (February 2026):
- 627 shows matched the vote/rating filters
- 515 shows had status "Ended" or "Canceled"
- 112 shows were skipped (returning series)
"""

from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv()
tmdb_api_key=os.getenv("TMDB_API_KEY")

base="https://api.themoviedb.org/3"


shows=[]

for page in range(1,33):
    response=requests.get(url=f"{base}/discover/tv",
                             params={"api_key":tmdb_api_key,
                                    "include_adult":False,
                                    "language":"en-US",
                                    "sort_by": "vote_average.desc",
                                    "vote_count.gte":500,
                                    "vote_average.gte":7.8,
                                    "without_genres":"99,10763,10764,10767", # excluding documentary(99),news(10763),reality(10764),talk(10767)
                                    "page":page})
    status_code=response.status_code
    if status_code!=200:
        print(f"Fetching failed at page {page}. Error: {status_code}")
        break
    data=response.json()
    shows.extend(data["results"]) #results has each show as a dict
    print(f"Done with the fetching of the page {page}. So far {len(shows)} fetched.")


with open("temp_shows.json","w") as f:
    json.dump(shows,f,indent=2)

print(f"Total shows fetched: {len(shows)}")
print("Saved to temp_shows.json")



with open("temp_shows.json","r") as f:
    shows=json.load(f)

enriched_shows=[]
failed_shows=[]
no_posters=[]

for show in shows:
    series_details_response=requests.get(url=f"{base}/tv/{show["id"]}",
                                        params={"api_key":tmdb_api_key})
    time.sleep(0.25)
    status_code=series_details_response.status_code

    #if we can't fetch a show, we continue with others
    if status_code!=200:
        print(f"Fetching failed at show with the id {show["id"]}. Error: {status_code}")
        failed_shows.append({"id":show["id"],"name":show.get("name"),"error":status_code})
        continue

    series_details_data=series_details_response.json()

    if series_details_data["status"] in ["Ended", "Canceled"]:
        creators=[creator["name"] for creator in series_details_data.get("created_by",[])]
        creators_str=", ".join(creators)

        season_num_ep_count=[]
        for season in series_details_data["seasons"]:
            if season["season_number"]!=0:
                season_num_ep_count.append([season["season_number"],season["episode_count"]])

        seasons_with_eps=[]
        season_fail_flag=False
        for season_num,ep_count in season_num_ep_count:

            season_details_response=requests.get(url=f"{base}/tv/{show["id"]}/season/{season_num}",
                                                params={"api_key":tmdb_api_key})
            time.sleep(0.25)

            status_code=season_details_response.status_code
            if status_code!=200:
                print(f"Fetching failed at season {season_num} of show with the id {show["id"]}. Error: {status_code}")
                failed_shows.append({"id":show["id"],"name":show.get("name"),"error": status_code})
                season_fail_flag=True
                break

            season_details_data=season_details_response.json()

            episodes=[]
            for ep in season_details_data["episodes"]:
                episode={
                "episode_number":ep["episode_number"],
                "title":ep.get("name",""),
                "description":ep.get("overview",""),
                }
                episodes.append(episode)

            season_with_eps={
                "season_number":season_num,
                "episode_count":ep_count,
                "episodes":episodes
            }
            seasons_with_eps.append(season_with_eps)

        if season_fail_flag:
            continue

        genres=[genre["id"] for genre in series_details_data.get("genres", [])]

        credits_response=requests.get(url=f"{base}/tv/{show["id"]}/aggregate_credits",
                                      params={"api_key":tmdb_api_key})
        time.sleep(0.25)

        status_code=credits_response.status_code
        if status_code!=200:
            print(f"Fetching failed at getting credits for show with the id {show["id"]}. Error: {status_code}")
            failed_shows.append({"id":show["id"],"name":show.get("name"),"error": status_code})
            continue

        credits_data=credits_response.json()
        main_actors=[actor["name"] for actor in credits_data["cast"][:10]]
        main_actors_str=", ".join(main_actors)

        poster_filename=None
        if series_details_data.get("poster_path"):
            poster_base="https://image.tmdb.org/t/p/w500"
            poster_response=requests.get(url=f"{poster_base}{series_details_data["poster_path"]}")
            time.sleep(0.25)

            if poster_response.status_code==200:
                #create posters directory if it doesn't exist
                os.makedirs("posters", exist_ok=True)

                #save
                poster_filename=f"{series_details_data["id"]}.jpg"
                with open(f"posters/{poster_filename}","wb") as f:
                    f.write(poster_response.content)
            else:
                no_posters.append({"id":show["id"],"name":show.get("name"),"poster_url":series_details_data["poster_path"],"error":status_code})

        enriched_show={
            # all these for series
            "tmdb_id":series_details_data["id"],
            "title":series_details_data["name"],
            "description":series_details_data.get("overview"),
            "origin_country":", ".join(series_details_data["origin_country"]),
            "first_air_date":series_details_data["first_air_date"],
            "last_air_date":series_details_data["last_air_date"],
            "actors":main_actors_str,
            "creators":creators_str,
            "tmdb_vote_average":series_details_data["vote_average"],
            "num_seasons":series_details_data["number_of_seasons"],
            "num_eps":series_details_data["number_of_episodes"],
            "poster_filename":poster_filename,
            "genres":genres,
            "status":series_details_data["status"],
            #this for seasons and episodes
            "seasons":seasons_with_eps
        }

        enriched_shows.append(enriched_show)
        print(f"Processed:{series_details_data['name']}")

        #adding checkpoint at every 50 shows
        if len(enriched_shows)%50==0:
            with open(f"checkpoint_{len(enriched_shows)}.json", "w") as f:
                json.dump(enriched_shows,f)
            print(f"Checkpoint saved at {len(enriched_shows)} shows.")

print(f"Complete: {len(enriched_shows)} shows added.")
print(f"Skipped: {len(shows)-len(enriched_shows)} shows (not ended or failed).")

genres_response=requests.get(url=f"{base}/genre/tv/list",params={"api_key":tmdb_api_key})

status_code=genres_response.status_code
if status_code!=200:
    print(f"Fetching failed at genres. Error: {status_code}")
genres_data=genres_response.json()
genres=genres_data["genres"]

initial_ingest={
    "shows":enriched_shows,
    "genres":genres,
    "failed_shows":failed_shows,
    "no_posters":no_posters
}

with open("initial_ingest.json","w") as f:
    json.dump(initial_ingest,f,indent=2)

print(f"Total of enriched shows fetched: {len(initial_ingest["shows"])}")

print(f"Total of genres fetched: {len(initial_ingest["genres"])}")

print(f"Total of failed posters fetched: {len(initial_ingest["no_posters"])}")

print(f"Total of failed shows to fetch: {len(initial_ingest["failed_shows"])}")
print("Saved to initial_ingest.json")

