from config import EVENT_IDS, IS_LGE
from utils import (
    get_json_from_endpoint,
    json_file_exists,
    save_json_to_file_in_directory,
)


# Special vote dates and venues
upcoming_special_votes = get_json_from_endpoint("api/SpecialVotes/UpComingSpecialVotes")

electoral_event_types = get_json_from_endpoint("api/v1/ElectoralEvent")

electoral_events = []
for electoral_event_type in electoral_event_types:
    electoral_events += get_json_from_endpoint(
        f"api/v1/ElectoralEvent?ElectoralEventTypeID={electoral_event_type['ID']}"
    )

for event_id in EVENT_IDS:
    data_directory = f"data/{event_id}"

    save_json_to_file_in_directory(electoral_event_types, data_directory, "electoral-event-types")
    save_json_to_file_in_directory(electoral_events, data_directory, "electoral-events")
    save_json_to_file_in_directory(upcoming_special_votes, data_directory, "special-votes")

    event = next(
        (e for e in electoral_events if event_id in (e.get("ElectoralEventID"), e.get("ID"))),
        None,
    )
    if event:
        print(f"Electoral event {event_id}: {event.get('Description', event)}")
    else:
        print(f"Warning: event {event_id} not in the ElectoralEvent list. Continuing anyway.")

    # Voting stations
    voting_stations = get_json_from_endpoint(
        f"api/v1/VotingStations?ElectoralEventID={event_id}"
    )
    save_json_to_file_in_directory(voting_stations, data_directory, "voting-stations")
    print(f"Fetched {len(voting_stations)} voting stations")

    # Parties contesting the event
    save_json_to_file_in_directory(
        get_json_from_endpoint(f"api/v1/ContestingParties?ElectoralEventID={event_id}"),
        data_directory,
        "contesting-parties",
    )

    # Provinces and municipalities derived from the voting stations
    municipalities = {}
    provinces = {}
    for voting_station in voting_stations:
        key = (voting_station["ProvinceID"], voting_station["MunicipalityID"])
        municipalities[key] = voting_station["Municipality"]
        provinces[voting_station["ProvinceID"]] = voting_station["Province"]
    print(f"Found {len(municipalities)} municipalities in {len(provinces)} provinces")

    for (province_id, municipality_id), name in sorted(municipalities.items()):
        print(f"{municipality_id} {name}")

        # Parties contesting this municipality
        if not json_file_exists(f"{data_directory}/contesting-parties", str(municipality_id)):
            save_json_to_file_in_directory(
                get_json_from_endpoint(
                    f"api/v1/ContestingParties?ElectoralEventID={event_id}"
                    f"&ProvinceID={province_id}&MunicipalityID={municipality_id}"
                ),
                f"{data_directory}/contesting-parties",
                str(municipality_id),
            )

        # Candidates published per municipality for local elections
        if IS_LGE and not json_file_exists(f"{data_directory}/candidates", str(municipality_id)):
            save_json_to_file_in_directory(
                get_json_from_endpoint(
                    f"api/v1/LGECandidates?ElectoralEventID={event_id}"
                    f"&MunicipalityID={municipality_id}"
                ),
                f"{data_directory}/candidates",
                str(municipality_id),
            )

    if not IS_LGE:
        save_json_to_file_in_directory(
            get_json_from_endpoint(
                f"api/v1/NPENationalCandidates?ElectoralEventID={event_id}"
            ),
            data_directory,
            "national-candidates",
        )

        for province_id, province_name in sorted(provinces.items()):
            print(f"{province_id} {province_name}")

            if json_file_exists(f"{data_directory}/provincial-candidates", str(province_id)):
                continue

            save_json_to_file_in_directory(
                get_json_from_endpoint(
                    f"api/v1/NPEProvincialCandidates?ElectoralEventID={event_id}"
                    f"&ProvinceID={province_id}"
                ),
                f"{data_directory}/provincial-candidates",
                str(province_id),
            )
