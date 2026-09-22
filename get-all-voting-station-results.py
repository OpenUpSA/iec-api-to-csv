from config import BALLOT_RESULTS_ENDPOINT, EVENT_IDS
from utils import get_json_from_endpoint, save_json_to_file_in_directory


event_ids = EVENT_IDS

voting_stations = get_json_from_endpoint(
    f"api/v1/VotingStations?ElectoralEventID={event_ids[0]}"
)

for voting_station in voting_stations:
    province_id = voting_station["ProvinceID"]
    municipality_id = voting_station["MunicipalityID"]
    vd_number = voting_station["VDNumber"]
    voting_station["results"] = {}

    for event_id in event_ids:
        vd_result = get_json_from_endpoint(
            f"{BALLOT_RESULTS_ENDPOINT}?ElectoralEventID={event_id}&ProvinceID={province_id}&MunicipalityID={municipality_id}&VDNumber={vd_number}"
        )
        voting_station["results"][event_id] = vd_result

    save_json_to_file_in_directory(
        voting_station, "data/voting-stations", f"{vd_number}"
    )
    
save_json_to_file_in_directory(voting_stations, "data", "voting-stations")
