import json
import config as config
import datetime
import os
import logging
import sys

import google.auth.transport.requests
import google.cloud.logging


## Helper functions
def GetConfig():
    # Function to Open config.json file and load values
    dirname = os.path.dirname(__file__)
    config_file = os.path.join(dirname, '../../config.json')
    try:
        # Read file
        f = open(config_file)
        data = json.load(f)
        # Set Variables
        config.gcp_project = os.environ.get('GCP_PROJECT', data['project'])
        config.dashboard_url = os.environ.get('DASHBOARD_URL', data['dashboard-url'])
        config.site_urls = os.environ.get('SITE_URLS', data['site-urls'])
        config.load_test_url = os.environ.get('LOAD_TEST_URL', data['load-test-url'])
        config.load_test_user_bump = os.environ.get('LOAD_TEST_USER_BUMP', data['load-test-user-bump'])
        config.cachetime = os.environ.get('CACHE_TIMEOUT', data['cache-timeout'])
    except Exception as e:
        # Unable to load file, quit
        logging.error(e)
        quit()

def Configure_Logging():
    """ Function to build logging"""

    # Use Cloud Logging while on GCP
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("Using local logging")