import json
import config as config
import datetime
import os


## Helper functions
def GetConfig():
    # Function to Open config.json file and load values
    config_file = "code/config.json"
    try:
        # Read file
        f = open(config_file)
        data = json.load(f)
        # Set Variables
        config.gcp_project = os.environ.get('GCP_PROJECT', data['project'])
        config.gke_clusters = os.environ.get('GKE_CLUSTERS', data['gke-clusters'])
        config.dashboard_url = os.environ.get('DASHBOARD_URL', data['dashboard-url'])
        config.site_urls = os.environ.get('SITE_URLS', data['site-urls'])
        config.load_test_url = os.environ.get('LOAD_TEST_URL', data['load-test-url'])
        config.load_test_user_bump = os.environ.get('LOAD_TEST_USER_BUMP', data['load-test-user-bump'])
        config.cachetime = os.environ.get('CACHE_TIMEOUT', data['cache-timeout'])
        config.InstanceCacheLastUpdated = datetime.datetime.now()
        config.PodCacheLastUpdated = datetime.datetime.now()
    except Exception as e:
        # Unable to load file, quit
        print(e)
        quit()