from influxdb_client import InfluxDBClient, Point, WritePrecision, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pytz


def write_to_influxdb(bucket, point):
  token = "C_YCM_dHzdvVl0GTWXTcVwvth6HT8I5-K4gkALGhwGdzMRhoawGEnkGD41yU2gQz64CYVGkdAhGSIfWqJU_2lQ=="
  org = "MM"
  client = InfluxDBClient(url="http://20.160.222.178:8086/", token=token, org=org)
  write_api = client.write_api(write_options=SYNCHRONOUS)
  write_api.write(bucket=bucket, org=org, record=point)


def create_point(url, metric, metricValue, date):
  point = Point(url)\
        .field(metric, metricValue)\
        .time(date, WritePrecision.NS)\

  return point

def create_point_with_tag(url, metric, metricValue, tagName, tagValue, date):
  point = Point(url)\
        .field(metric, metricValue)\
        .tag(tagName, tagValue)\
        .time(date, WritePrecision.NS)\

  return point

def find_latest_data_point(bucket, field):
   
  token = "C_YCM_dHzdvVl0GTWXTcVwvth6HT8I5-K4gkALGhwGdzMRhoawGEnkGD41yU2gQz64CYVGkdAhGSIfWqJU_2lQ=="
  org = "MM"


  client = InfluxDBClient(url="http://20.160.222.178:8086/", token=token, org=org)

  query = f'from(bucket: "{bucket}")' \
    '|> range(start: 0)' \
    f'|> filter(fn: (r) => r["_field"] == "{field}")' \
    '|> last()' \
    '|> sort(columns: ["_time"], desc: false)' \
    '|> group(columns: ["_measurement","_field","_value","keyword"], mode:"except")' \
    '|> keep(columns: ["_time"])' 
    
  tables = client.query_api().query(query=query)
  #print(tables[len(tables)-1].records[0])
  last_timestamp = tables[len(tables)-1].records[0]["_time"]
  last_timestamp=str(last_timestamp)
  
  # Convert the last timestamp to a datetime object with timezone information
  last_datetime = datetime.fromisoformat(last_timestamp).replace(tzinfo=pytz.UTC)
  return last_datetime