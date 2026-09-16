# List event IDs with:
#   curl "https://api.elections.org.za/api/v1/ElectoralEvent" -H "Authorization: Bearer ${IEC_API_TOKEN}"

# EVENT_IDS = [1335, 1334]  # 2024 PROVINCIAL and NATIONAL ELECTION
EVENT_IDS = [1887]  # 2026 LOCAL GOVERNMENT ELECTIONS

# Set which election type to process
IS_LGE = True

BALLOT_RESULTS_ENDPOINT = "api/v1/LGEBallotResults" if IS_LGE else "api/v1/NPEBallotResults"
