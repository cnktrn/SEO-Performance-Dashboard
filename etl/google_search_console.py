from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from typing import Dict
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from influxDB_write import write_to_influxdb, create_point_with_tag, create_point
from urllib3.exceptions import ConnectTimeoutError
import urllib3

# define general constants
#Non-string values require approximately three bytes. String values require variable space, determined by string compression
API_SERVICE_NAME = "webmasters"
API_VERSION = "v3"
SCOPE = ["https://www.googleapis.com/auth/webmasters.readonly"]



def auth_using_key_file(key_filepath: str) -> Resource:
    """Authenticate using a service account key file saved locally"""

    credentials = service_account.Credentials.from_service_account_file(
        key_filepath, scopes=SCOPE
    )
    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    return service


# filepath location of your service account key json file
KEY_FILE = './key/seo_api_key.json'

# authenticate session
service = auth_using_key_file(key_filepath=KEY_FILE)

# verify your service account has permissions to your domain
service.sites().list().execute()

#DOMAIN = "sc-domain:analytica.de"


def query(client: Resource, payload: Dict[str, str], domain) -> Dict[str, any]:
    response = client.searchanalytics().query(siteUrl=domain, body=payload).execute()
    return response


#START_DATE = "2022-01-01"  # define your start date


def create_gsc(start_date, domain, bucket):
    MAX_ROWS = 25_000
    dimensions = ["query","page", "date"]
    end_date = datetime.now().strftime("%Y-%m-%d")
    response_rows = []
    i = 0
    while True:

        # https://developers.google.com/webmaster-tools/v1/searchanalytics/query
        payload = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": MAX_ROWS,
            "startRow": i * MAX_ROWS,
        }

        # make request to API
        response = query(service, payload, domain)

        # if there are rows in the response append to the main list
        if response.get("rows"):
            
            for row in response["rows"]:
                if row["impressions"] > 1 & row["clicks"] > 0:
                    row["page"] = row["keys"][1]
                    row["date"] = row["keys"][2]
                    date_string = row["keys"][2]
                    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
                    influx_date_str = date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                    print(influx_date_str)
                    print(row)
                    print("\n\n")

                    try:
                        points = []
                        point = create_point_with_tag(row["keys"][1], "impressions", row["impressions"], "keyword", row["keys"][0], influx_date_str)
                        points.append(point)
                        #write_to_influxdb("Mock3", point)
                        point = create_point_with_tag(row["keys"][1], "clicks", row["clicks"], "keyword", row["keys"][0], influx_date_str)
                        points.append(point)
                        #write_to_influxdb("Mock3", point)
                        ctr = round(float(row["ctr"]), 3)
                        point = create_point_with_tag(row["keys"][1], "ctr", ctr, "keyword", row["keys"][0], influx_date_str)
                        points.append(point)
                        #write_to_influxdb("Mock3", point)
                        position = round(float(row["position"]), 1)
                        point = create_point_with_tag(row["keys"][1], "position", position, "keyword", row["keys"][0], influx_date_str)
                        points.append(point)
                        write_to_influxdb(bucket, points)
                        

                    except urllib3.exceptions.ConnectTimeoutError as e:
                        print("Connection timeout error occurred:", str(e))
                    
                    

                else:
                    response["rows"].remove(row)
                
            
            response_rows.extend(response["rows"])
            
            
            i += 1
        else:
            break

        print(f"Collected {len(response_rows):,} rows")
        #print(response_rows[1])

create_gsc("2022-01-01", "sc-domain:analytica.de", "Analytica")