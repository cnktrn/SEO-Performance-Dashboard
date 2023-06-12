import os
from datetime import datetime, timedelta, timezone, date, time
from typing import List
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (Dimension, Metric, DateRange, Metric, OrderBy, 
                                               FilterExpression, MetricAggregation, CohortSpec)
from google.analytics.data_v1beta.types import RunReportRequest, RunRealtimeReportRequest
from influxDB_write import write_to_influxdb, create_point, find_latest_data_point
from urllib3.exceptions import ConnectTimeoutError
import urllib3


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './key/seo_api_key.json'

property_id = '329272465'


        
def run_report(metricList, days, bucket):
    """Runs a simple report on a Google Analytics 4 property."""
    # TODO(developer): Uncomment this variable and replace with your
    #  Google Analytics 4 property ID before running the sample.
    property_id = "329272465"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()
    for metric in metricList:
        for i in range(days):
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name="fullPageUrl")],
                metrics=[Metric(name=metric)],
                date_ranges=[DateRange(start_date=f"{i+1}daysAgo", end_date=f"{i}daysAgo")],
            )
            response = client.run_report(request)
            #print(i)
            for row in response.rows:      
                date = datetime.now() - timedelta(days=1+i)
                date = date.strftime('%y%m%d')
                date_obj = datetime.strptime(date, "%y%m%d")
                influx_date_str = date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                #print(influx_date_str)
                #print( row.metric_values[0].value)
                url = row.dimension_values[0].value
                if url.startswith("www."):
                    url = url[4:]
                dataPoint = create_point("https://"+url, metric, float(row.metric_values[0].value), influx_date_str)
                try:
                    write_to_influxdb(bucket, dataPoint)
                except Exception as e:
                    print("Connection timeout error occurred:", str(e))
                print( url, row.metric_values[0].value)


def updateGA4(metricList, bucket, field):
    last_datetime = find_latest_data_point(bucket, field)
    current_datetime = datetime.now(timezone.utc)
    timedelta = current_datetime - last_datetime
    days_between = timedelta.days
    print(days_between)
    run_report(metricList, days_between, bucket)

#run_report(["screenPageViewsPerUser", "activeUsers", "bounceRate", "screenPageViewsPerSession","totalUsers","sessions"], 31, "Analytica")
#run_report(["sessions"], 7, "Mock2")
updateGA4(["screenPageViewsPerUser", "activeUsers", "bounceRate", "screenPageViewsPerSession","totalUsers","sessions"], "Analytica", "sessions")