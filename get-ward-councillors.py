import csv
import os

from config import EVENT_IDS
from utils import (
    get_json_from_endpoint,
    json_file_exists,
    load_json_from_file_in_directory,
    save_json_to_file_in_directory,
)


def flatten(record, prefix=""):
    """Flatten nested dicts, e.g. PartyDetail.Name -> PartyDetail_Name."""
    row = {}
    for key, value in record.items():
        if isinstance(value, dict):
            row.update(flatten(value, f"{prefix}{key}_"))
        else:
            row[f"{prefix}{key}"] = value
    return row


for event_id in EVENT_IDS:
    data_directory = f"data/{event_id}"
    councillors_directory = f"{data_directory}/ward-councillors"
    output_directory = f"output/pre-election/{event_id}"

    # Wards derived from the voting stations saved by get-pre-election-data.py
    voting_stations = load_json_from_file_in_directory(data_directory, "voting-stations")
    wards = {}
    for voting_station in voting_stations:
        wards[voting_station["WardID"]] = voting_station
    print(f"Event {event_id}: found {len(wards)} wards")

    rows = []
    for ward_id, voting_station in sorted(wards.items()):
        # Skip wards already downloaded
        if not json_file_exists(councillors_directory, str(ward_id)):
            save_json_to_file_in_directory(
                get_json_from_endpoint(f"api/v1/LGEWardCouncilor?WardID={ward_id}"),
                councillors_directory,
                str(ward_id),
            )

        context = {
            "ProvinceID": voting_station["ProvinceID"],
            "Province": voting_station["Province"],
            "MunicipalityID": voting_station["MunicipalityID"],
            "Municipality": voting_station["Municipality"],
            "WardID": ward_id,
        }

        if not json_file_exists(councillors_directory, str(ward_id)):
            # No councillor returned, e.g. a new ward
            rows.append(context)
            continue

        councillors = load_json_from_file_in_directory(councillors_directory, str(ward_id))
        if isinstance(councillors, dict):
            councillors = [councillors]
        for councillor in councillors:
            rows.append({**context, **flatten(councillor)})

    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(f"{output_directory}/ward-councillors.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, restval="")
        writer.writeheader()
        writer.writerows(rows)

    missing = sum(1 for row in rows if "Name" not in row)
    print(f"Wrote {len(rows)} rows to {output_directory}/ward-councillors.csv ({missing} wards without a councillor)")
