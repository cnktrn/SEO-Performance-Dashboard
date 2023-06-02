"""Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, timezone, date, time
from influxdb_client import InfluxDBClient, Point, WritePrecision, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz



# You can generate a Token from the "Tokens Tab" in the UI
token = "C_YCM_dHzdvVl0GTWXTcVwvth6HT8I5-K4gkALGhwGdzMRhoawGEnkGD41yU2gQz64CYVGkdAhGSIfWqJU_2lQ=="
org = "MM"
bucket = "Mock"

client = InfluxDBClient(url="http://20.160.222.178:8086/", token=token, org=org)

write_api = client.write_api(write_options=SYNCHRONOUS)
# Initialize the query API
query_api = QueryApi(client)

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './key/seo_api_key.json'
VIEW_ID = '329272465' #329272465   <-> 275154011
metricDescription = ""
metricValue = 0


def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics, startDate, endDate, metric):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate':f'{startDate}daysAgo', 'endDate': f'{endDate}daysAgo'}],
          'metrics': [{'expression': metric}]#,
          #'dimensions': [{'name': 'ga:city'}]
        }]
      }
  ).execute()

def get_report_last_24(analytics, metric):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate':'1daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': metric}]#,
          #'dimensions': [{'name': 'ga:city'}]
        }]
      }
  ).execute()

def create_point(metricDescription, metricValue, metricForm, displayedDays, date):
  point = Point(metricDescription)\
        .field(metricDescription, metricValue)\
        .time(date, WritePrecision.NS)\
        .tag("metricForm", metricForm)\
        .tag("displayDays", displayedDays)\

  return point


def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])
      

      for header, dimension in zip(dimensionHeaders, dimensions):
        #print(header + ': ', dimension)
        pass

      for i, values in enumerate(dateRangeValues):
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          global metricDescription 
          metricDescription = metricHeader.get('name')
          global metricValue
          metricValue = float(value)


def add_metric_to_bucket(days, metric, buc, metricForm, displayedDays):
  analytics = initialize_analyticsreporting()
  for i in range(days):
    response = get_report(analytics, i+2, i+1, metric)
    print_response(response)

  # Get the current datetime with nanosecond precision
    current_time = datetime.combine(date.today(), time(12, 0))
    one_day_ago = current_time - timedelta(days=i+1)
    one_day_ago_influxdb = one_day_ago.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    point = create_point(metricDescription, metricValue, metricForm, displayedDays, one_day_ago_influxdb)

  # Write the Point object to InfluxDB
    #write_api.write(bucket=buc, org=org, record=point)
    print(one_day_ago_influxdb)
  
  response = get_report_last_24(analytics, metric)
  print_response(response)


  point = create_point(metricDescription, metricValue, metricForm, displayedDays, datetime.utcnow())      
  write_api.write(bucket=buc, org=org, record=point)


def update(buc):
  
  flux_query = f'import "influxdata/influxdb/schema"\n\nschema.measurements(bucket: "{buc}")'
  
  # Execute the Flux query
  result = query_api.query(query=flux_query)
  
  # Print the result
  for table in result:
    for record in table:
    
      flux_query = f'import "influxdata/influxdb/schema"\n\nschema.measurementTagValues(bucket: "{buc}", measurement: "{record.get_value()}", tag: "displayDays")'
      resultTags = query_api.query(query=flux_query)
      daysValue = resultTags[0].records[0]['_value']
     
      flux_query = f'import "influxdata/influxdb/schema"\n\nschema.measurementTagValues(bucket: "{buc}", measurement: "{record.get_value()}", tag: "metricForm")'
      resultTags = query_api.query(query=flux_query)
      metricFormValue = resultTags[0].records[0]['_value']
     
      query = f'from(bucket: "{buc}")' \
      '|> range(start: 0, stop: now())' \
      f'|> filter(fn: (r) => r["_measurement"] == "{record.get_value()}")' \
      '|> keep(columns: ["_time"])' \
      '|> last(column: "_time")'
      
      tables = client.query_api().query(query=query)
      last_timestamp = tables[0].records[0]["_time"]
      last_timestamp=str(last_timestamp)

      # Convert the last timestamp to a datetime object with timezone information
      last_datetime = datetime.fromisoformat(last_timestamp).replace(tzinfo=pytz.UTC)
      current_datetime = datetime.now(timezone.utc)
      timedelta = current_datetime - last_datetime
      days_between = timedelta.days

      add_metric_to_bucket(days_between, record.get_value(), buc, metricFormValue, daysValue)

def main():
  add_metric_to_bucket(20, "ga:bounces", "Mock","piechart", 20)
  #update("Mock")

if __name__ == '__main__':
  main()