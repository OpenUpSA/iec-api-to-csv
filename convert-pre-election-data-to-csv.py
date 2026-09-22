import csv
import json
import os

from config import EVENT_IDS
from utils import json_file_exists, load_json_from_file_in_directory


def write_csv(rows, output_directory, filename):
    if not rows:
        print(f"No rows for {filename}, skipping")
        return

    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(f"{output_directory}/{filename}", "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, restval=""
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value) if isinstance(value, (list, dict)) else value
                    for key, value in row.items()
                }
            )

    print(f"Wrote {len(rows)} rows to {output_directory}/{filename}")


def records_from(directory, filename, context):
    """Records from one JSON file, each merged with its province/municipality."""
    if not json_file_exists(directory, filename):
        # Nothing published yet
        return []

    records = load_json_from_file_in_directory(directory, filename)
    if isinstance(records, dict):
        records = [records]

    return [{**context, **record} for record in records]


for event_id in EVENT_IDS:
    data_directory = f"data/{event_id}"
    output_directory = f"output/pre-election/{event_id}"

    voting_stations = load_json_from_file_in_directory(data_directory, "voting-stations")
    print(f"Event {event_id}: loaded {len(voting_stations)} voting stations")

    write_csv(voting_stations, output_directory, "voting-stations.csv")

    municipality_context = {}
    province_context = {}
    for voting_station in voting_stations:
        province = {
            "Province": voting_station["Province"],
            "ProvinceID": voting_station["ProvinceID"],
        }
        province_context[voting_station["ProvinceID"]] = province
        municipality_context[voting_station["MunicipalityID"]] = {
            **province,
            "Municipality": voting_station["Municipality"],
            "MunicipalityID": voting_station["MunicipalityID"],
        }

    parties = records_from(data_directory, "contesting-parties", {})
    for municipality_id, context in sorted(municipality_context.items()):
        parties += records_from(
            f"{data_directory}/contesting-parties", str(municipality_id), context
        )
    write_csv(parties, output_directory, "contesting-parties.csv")

    # Candidates published per municipality
    # National and provincial are per event and per province
    candidates = records_from(data_directory, "national-candidates", {})
    for municipality_id, context in sorted(municipality_context.items()):
        candidates += records_from(
            f"{data_directory}/candidates", str(municipality_id), context
        )
    for province_id, context in sorted(province_context.items()):
        candidates += records_from(
            f"{data_directory}/provincial-candidates", str(province_id), context
        )
    write_csv(candidates, output_directory, "candidates.csv")

    write_csv(
        records_from(data_directory, "special-votes", {}),
        output_directory,
        "special-votes.csv",
    )
