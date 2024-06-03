import os
import json
import csv
from datetime import datetime

from utils import get_json_from_endpoint, save_json_to_file_in_directory


voting_stations = []
with open(f"data/voting-stations.json", "r") as file:
    voting_stations = json.load(file)
print(f"Loaded {len(voting_stations)} voting stations")

country = "ZA"

provinces = {}
# Group voting stations by province
for vs in voting_stations:
    province = vs["Province"]
    if province not in provinces:
        provinces[province] = []
    provinces[province].append(vs)

for p in provinces:
    pro = provinces[p]
    with open(f"output/results-{p}.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        csvwriter.writerow(
            [
                "Country",
                "Province",
                "District",
                "Municipality",
                "Ward",
                "VD Number",
                "Registered Population",
                "Spoilt Votes",
                "Total Valid Votes",
                "BallotType",
                "sPartName",
                "Party Votes",
                "Released",
                "Section24AVotes",
                "SpecialVotes",
                "PercVoterTurnout",
                "TotalVotesCast",
                "TotalValidVotes",
                "VDCount",
                "VDWithResultsCaptured",
                "bResultsComplete",
            ]
        )

        for vs in provinces[p]:
            province_name = vs["Province"]
            vd_number = vs["VDNumber"]
            district = vs["VotingDistrict"]
            municipality = vs["Municipality"]
            ward = vs["WardID"]

            for vs_result in vs["results"]:
                vd_result_event = vs["results"][vs_result]

                if "RegisteredVoters" in vd_result_event:
                    registered_population = vd_result_event["RegisteredVoters"]
                else:
                    registered_population = "N/A"
                if "SpoiltVotes" in vd_result_event:
                    spoilt_votes = vd_result_event["SpoiltVotes"]
                else:
                    spoilt_votes = "N/A"
                if "TotalValidVotes" in vd_result_event:
                    total_valid_votes = vd_result_event["TotalValidVotes"]
                else:
                    total_valid_votes = "N/A"
                if "released_date" in vd_result_event:
                    released_date = vd_result_event["released_date"]
                else:
                    released_date = "N/A"

                if "PartyBallotResults" in vd_result_event:
                    for party in vd_result_event["PartyBallotResults"]:
                        csvwriter.writerow(
                            [
                                country,
                                province_name,
                                district,
                                municipality,
                                ward,
                                vd_number,
                                registered_population,
                                spoilt_votes,
                                total_valid_votes,
                                party["BallotType"],
                                party["Name"].replace(
                                    "  ", " "
                                ),  # "CONGRESS  OF THE PEOPLE" has a double space
                                party["ValidVotes"],
                                released_date,
                                vd_result_event["Section24AVotes"],
                                vd_result_event["SpecialVotes"],
                                vd_result_event["PercVoterTurnout"],
                                vd_result_event["TotalVotesCast"],
                                vd_result_event["TotalValidVotes"],
                                vd_result_event["VDCount"],
                                vd_result_event["VDWithResultsCaptured"],
                                vd_result_event["bResultsComplete"],
                            ]
                        )
                else:
                    print(f"No PartyBallotResults in {vd_number}")
