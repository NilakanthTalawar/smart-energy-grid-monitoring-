import os
import json
import time
import requests
from azure.eventhub import EventHubProducerClient, EventData


# --------------------------------------------------
# Configuration
# --------------------------------------------------

EIA_API_KEY = os.getenv("EIA_API_KEY")
FABRIC_CONNECTION_STRING = os.getenv(
    "FABRIC_EVENTHUB_CONNECTION_STRING"
)

if not EIA_API_KEY:
    raise RuntimeError("EIA_API_KEY environment variable is missing.")

if not FABRIC_CONNECTION_STRING:
    raise RuntimeError(
        "FABRIC_EVENTHUB_CONNECTION_STRING environment variable is missing."
    )


# --------------------------------------------------
# Regions
# --------------------------------------------------

REGIONS = [
    "CAL",
    "ERCO",
    "FLA",
    "CAR",
    "CENT"
]


# --------------------------------------------------
# EIA API
# --------------------------------------------------

URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"


# --------------------------------------------------
# Track already sent records
# --------------------------------------------------

sent_records = set()


# --------------------------------------------------
# Fetch data
# --------------------------------------------------

def get_latest_events():

    events = []

    for region_code in REGIONS:

        print(f"Checking {region_code}...")

        params = {
            "api_key": EIA_API_KEY,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[type][0]": "D",
            "facets[respondent][0]": region_code,
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": "1"
        }

        try:

            response = requests.get(
                URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            result = response.json()

            records = result["response"]["data"]

            if not records:
                print(f"  No data for {region_code}")
                continue

            record = records[0]

            timestamp = record["period"]

            # Unique ID = region + hour
            record_id = f"{region_code}_{timestamp}"

            # Skip duplicate
            if record_id in sent_records:

                print(
                    f"  Already sent: {timestamp}"
                )

                continue

            event = {
                "Timestamp": timestamp + ":00:00",
                "RegionCode": record["respondent"],
                "RegionName": record["respondent-name"],
                "MetricType": record["type-name"],
                "DemandMWh": float(record["value"]),
                "Unit": "MWh",
                "Source": "EIA-930"
            }

            events.append(event)

            print(
                f"  NEW → {record['respondent-name']} | "
                f"{record['value']} MWh"
            )

        except Exception as e:

            print(
                f"  ERROR for {region_code}: {e}"
            )

    return events


# --------------------------------------------------
# Send events to Fabric
# --------------------------------------------------

def send_to_fabric(events):

    if not events:

        print("\nNo new events to send.")

        return


    print(
        f"\nSending {len(events)} new events to Fabric..."
    )

    producer = EventHubProducerClient.from_connection_string(
        conn_str=FABRIC_CONNECTION_STRING
    )

    try:

        batch = producer.create_batch()

        for event in events:

            event_data = EventData(
                json.dumps(event)
            )

            try:

                batch.add(event_data)

            except ValueError:

                producer.send_batch(batch)

                batch = producer.create_batch()

                batch.add(event_data)

        producer.send_batch(batch)

    finally:

        producer.close()


    # Mark records as sent
    for event in events:

        record_id = (
            f"{event['RegionCode']}_"
            f"{event['Timestamp'][:13]}"
        )

        sent_records.add(record_id)


    print(
        f"SUCCESS → {len(events)} events sent."
    )


# --------------------------------------------------
# Continuous collector
# --------------------------------------------------

print("=" * 60)
print("SMART ENERGY GRID - CONTINUOUS EIA COLLECTOR")
print("=" * 60)

print("\nMonitoring 5 regions:")
print("CAL  - California")
print("ERCO - Texas")
print("FLA  - Florida")
print("CAR  - Carolinas")
print("CENT - Central")

print("\nCollector started.")
print("Press CTRL+C to stop.\n")


try:

    while True:

        print("\n" + "-" * 60)

        current_events = get_latest_events()

        send_to_fabric(current_events)

        print("\nWaiting 60 seconds...")

        time.sleep(60)


except KeyboardInterrupt:

    print("\n\nCollector stopped by user.")