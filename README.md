# OpenUp IEC API to CSV

Python code and data from the [IEC's API](https://api.elections.org.za/help) for the 2024 National and Regional Elections.

# Run Code

You need Python `3.8`

```
pip install -r requirements.txt
python get-all-voting-station-results.py
python update-voting-station-reults-from-latest-in.py
python convert-voting-station-results-to-province-csv.py
```

# Useful CURLs

## Get a token
```
curl https://api.elections.org.za/token -X POST -d "grant_type=password&username=USERNAME&password=PASSWORD"
export IEC_API_TOKEN=TOKENFROMABOVE
```


## Get types of electoral events
```
curl "https://api.elections.org.za/api/v1/ElectoralEvent" -H "Authorization: Bearer ${IEC_API_TOKEN}"
```

## Get elecotral event ID e.g. 2024 NATIONAL ELECTION is 1334
```
curl "https://api.elections.org.za/api/v1/ElectoralEvent?ElectoralEventTypeID=1" -H "Authorization: Bearer ${IEC_API_TOKEN}"
export EID=1334
```

## Get all voting stations for an electoral event
```
curl "https://api.elections.org.za/api/v1/VotingStations?ElectoralEventID=${EID}" -H "Authorization: Bearer ${IEC_API_TOKEN}"
```

## Get voting station details
```
curl "https://api.elections.org.za/api/v1/VotingStationDetails?VDNumber=54760125" -H "Authorization: Bearer ${IEC_API_TOKEN}"
```

## Get 1000 most recently updated voting stations
```
curl "https://api.elections.org.za/api/v1/LatestResultsIn?ElectoralEventID=${EID}&NumberOfVDs=1000" -H "Authorization: Bearer ${IEC_API_TOKEN}"
```

## Get a voting station's results
```
curl "https://api.elections.org.za/api/v1/NPEBallotResults?ElectoralEventID=1335&ProvinceID=3&MunicipalityID=3003&VDNumber=32841266" -H "Authorization: Bearer ${IEC_API_TOKEN}"
```

## Delimitation details for an electoral event
```
curl "https://api.elections.org.za/api/v1/Delimitation?ElectoralEventID=${EID}" -H "Authorization: Bearer ${IEC_API_TOKEN}"
```