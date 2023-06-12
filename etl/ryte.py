import requests
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta, timezone, date, time
import pytz





apiEndpoint = 'https://api.ryte.com'

token = "C_YCM_dHzdvVl0GTWXTcVwvth6HT8I5-K4gkALGhwGdzMRhoawGEnkGD41yU2gQz64CYVGkdAhGSIfWqJU_2lQ=="
org = "MM"


client = InfluxDBClient(url="http://20.160.222.178:8086/", token=token, org=org)

write_api = client.write_api(write_options=SYNCHRONOUS)
# Initialize the query API
query_api = QueryApi(client)

def create_point(url,metric, metricValue, date):
  point = Point(url)\
        .field(metric, metricValue)\
        .time(date, WritePrecision.NS)\

  return point


requestUrl = "https://api.ryte.com/zoom/json"

headers = {
        'Content-Type': 'application/json'
    }

def update_ryte(bucket, attributeList, api_key, project):
    query = f'from(bucket: "{bucket}")' \
      '|> range(start: 0, stop: now())' \
      '|> keep(columns: ["_time"])' \
      '|> last(column: "_time")'
    
    tables = client.query_api().query(query=query)
    #print(tables[0].records[0])
    last_timestamp = tables[0].records[0]["_time"]
    last_timestamp=str(last_timestamp)
    #print(last_timestamp)

    # Convert the last timestamp to a datetime object with timezone information
    last_datetime = datetime.fromisoformat(last_timestamp).replace(tzinfo=pytz.UTC)
    current_datetime = datetime.now(timezone.utc)
    timedelta = current_datetime - last_datetime
    days_between = timedelta.days
    #print(days_between)
    extract_data_for_x_days(bucket, attributeList, days_between, api_key, project)



def extract_data_for_x_days(bucket, attributeList, days, api_key, project):
    
    for i in range(days):
        date = datetime.now() - timedelta(days=1+i)
        date = date.strftime('%y%m%d')
        print(date)
        extract_data(bucket, attributeList, date+"-2202", api_key, project)
#create a function that gets data for x days
def extract_data(bucket, attributeList, date, api_key, project):
    
   
    
    requestBody = {"action": "list", "crawl" : date,
            "authentication": {
                "api_key": api_key,
                "project": project,
            
            },
            "functions": [
                {
                    "name": "count",
                    "method": "count",
                    "parameters": [
                        {
                            "attribute": "url"
                        }
                    ]
                }
            ],
            "filter": {
                "AND": [
                {
                    "field": "is_local",
                    "operator": "==",
                    "value": True
                },
                {
                    "field": "url_type_id",
                    "operator": "==",
                    "value": 1
                },
                {
                    "field": "header_status_group",
                    "operator": "==",
                    "value": "2xx"
                }
                ]
                    },"pagination": {
                "offset": 0,
                "limit": 1000
            },
            "sorting": [
                {
                "attribute": "count_links_outgoing",
                "direction": "DESC"
                }
            ],
            "attributes": attributeList +["url"]
        }
    
    #print(requestBody)
    requestBody = json.dumps(requestBody)
    response = requests.post(requestUrl, headers=headers, data=requestBody)

    if response.ok:
        jsonResult = response.json()
        #print("Result:")
        
        #(jsonResult["last_crawled"])
        print(len(jsonResult["result"]))  
        if len(jsonResult["result"]) > 0:
            print(len(jsonResult["result"]))  
            print((jsonResult["last_crawled"]))
            for result in jsonResult["result"]:
                
                for attribute in attributeList:
                    (result["url"],attribute, result[attribute], jsonResult["last_crawled"])
                    point = create_point(result["url"], attribute, result[attribute], jsonResult["last_crawled"])
                    write_api.write(bucket=bucket, org=org, record=point)
                    try:
                        write_api.write(bucket=bucket, org=org, record=point)
                    except Exception as e:
                        print("Connection timeout error occurred:", str(e))
                     
    else:
        print(response.text)
        print('API request failed with status code:', response.status_code)

     

def main():
    attributeList = [  "count_links_outgoing",
            "count_links_outgoing_external",
            "count_links_outgoing_internal",
            "count_incoming_translations",
            "count_translations",
            "page_speed",
            "passes_juice_to_url",
            "server_connect_time",
            "server_load_time",
            "speed_index"]
    #extract_data(attributeList, '230430-2203', "7df8cf7ef1981515ad93199d2cda8fed", "p9a6b2adea2a2853eadcbbd3fe6f20cd")
    #extract_data_for_x_days("Analytica", attributeList, 100, "7df8cf7ef1981515ad93199d2cda8fed", "p9a6b2adea2a2853eadcbbd3fe6f20cd")
    update_ryte("Analytica", attributeList, "7df8cf7ef1981515ad93199d2cda8fed", "p9a6b2adea2a2853eadcbbd3fe6f20cd")

if __name__ == '__main__':
  main()