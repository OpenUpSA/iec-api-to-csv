import os
import json
import csv

from utils import get_json_from_endpoint, save_json_to_file_in_directory


event_ids = [1335, 1334]

voting_stations = []
with open(f"data/voting-stations.json", "r") as file:
    voting_stations = json.load(file)
print(f"Loaded {len(voting_stations)} voting stations")

for event_id in event_ids:
    latest_results = get_json_from_endpoint(
        f"api/v1/LatestResultsIn?ElectoralEventID={event_id}&NumberOfVDs=1000"
    )

    for result in latest_results:
        try:
            vd_number = result["VDNumber"]
            released_date = result["ReleasedDate"]

            filename = f"{event_id}" + released_date.replace(":", "-") + f"-{vd_number}"

            if os.path.exists(f"data/voting-stations-results/{filename}.json"):
                print(f"Skipping {filename}.json")
                continue

            # Find voting_station in voting_stations by vd_number
            voting_station = next(
                (vs for vs in voting_stations if vs["VDNumber"] == vd_number), None
            )

            if voting_station:
                province_id = voting_station["ProvinceID"]
                municipality_id = voting_station["MunicipalityID"]

                vd_result = get_json_from_endpoint(
                    f"api/v1/NPEBallotResults?ElectoralEventID={event_id}&ProvinceID={province_id}&MunicipalityID={municipality_id}&VDNumber={vd_number}"
                )

                save_json_to_file_in_directory(
                    vd_result, "data/voting-stations-results", filename
                )

                vd_result["released_date"] = released_date
                voting_station["results"][event_id] = vd_result
            else:
                print(f"Voting station {vd_number} not found in voting_stations")
        except KeyError as e:
            print(f"Error processing result: {result}")

save_json_to_file_in_directory(voting_stations, "data", "voting-stations")
