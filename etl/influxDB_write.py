from influxdb_client import InfluxDBClient, Point, WritePrecision, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

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