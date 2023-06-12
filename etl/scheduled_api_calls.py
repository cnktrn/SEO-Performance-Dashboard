from ryte import extract_data_for_x_days, update_ryte
from ga4 import updateGA4
from google_search_console import update_gsc

bucket="Analytica"
attributeList = [ "count_links_outgoing",
            "count_links_outgoing_external",
            "count_links_outgoing_internal",
            "count_incoming_translations",
            "count_translations",
            "page_speed",
            "passes_juice_to_url",
            "server_connect_time",
            "server_load_time",
            "speed_index"]
api_key="7df8cf7ef1981515ad93199d2cda8fed"
project="p9a6b2adea2a2853eadcbbd3fe6f20cd"

update_ryte(bucket, attributeList, api_key, project)

attributeListGA4 = ["screenPageViewsPerUser", "activeUsers", "bounceRate", "screenPageViewsPerSession","totalUsers","sessions"]
updateGA4(attributeListGA4, bucket, "sessions")

update_gsc("sc-domain:analytica.de", "Analytica", "impressions")
