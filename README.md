# Smart Energy Grid Monitoring System

Real-time U.S. electricity grid monitoring system built on Microsoft Fabric —
ingesting live EIA-930 demand data, detecting high-load conditions, and
triggering automated alerts, visualized in Power BI.

## Architecture

EIA API → Python Collector → Fabric Eventstream → Eventhouse (KQL) →
KQL Analytics → Power Automate (Event Hub trigger) → SendGrid Alert → Power BI Dashboard



![Architecture](architecture_eventstream.png)



## Features
- Real (not simulated) live electricity demand data from 5 U.S. grid regions
  (California, Texas, Florida, Carolinas, Central)
- Real-time ingestion via Microsoft Fabric Eventstream, deduped hourly per region
- KQL-based analytics: grid load % deviation, peak analysis, HIGH LOAD /
  ELEVATED / NORMAL classification
- Automated email alerts on high-load conditions — built independently via
  Power Automate + SendGrid after Fabric Data Activator's native email path
  was blocked by a tenant mailbox licensing limitation
- Live Power BI dashboard: KPI cards, regional map, trend lines, load
  distribution, live table

## Screenshots

**Real-time data landing in Eventhouse**


![Data Preview](griddemand_table_preview.png)



**KQL grid load classification query**


![KQL Query](kql_grid_load_query.png)



**Power Automate alert flow**


![Flow](power_automate_flow.png)



**All alert runs succeeding**


![Run History](power_automate_run_history.png)



**Final dashboard**


![Dashboard](dashboard_final.png)



**Live collector running**


![Collector](python_collector_running.png)



## Tech Stack
Microsoft Fabric (Eventstream, Eventhouse, KQL), Python, Azure Event Hubs,
Power Automate, SendGrid, Power BI, DAX

## Data Source
U.S. Energy Information Administration (EIA) API — EIA-930 hourly electricity demand
https://api.eia.gov/v2/electricity/rto/region-data/data/

## Setup
1. Clone repo
2. `pip install requests azure-eventhub`
3. Set environment variables: `EIA_API_KEY`, `FABRIC_EVENTHUB_CONNECTION_STRING`
4. `python EIA_Grid_Test.py`

## Author
Neelakantha Talawar
