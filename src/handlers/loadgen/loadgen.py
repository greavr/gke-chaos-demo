import threading
import requests
import time
import config
import random
import logging

## Add Load Function
def AddLoad():
    # Generate X number of extra requests
    try:
        for i in range(config.load_test_user_bump):
            x = threading.Thread( target=make_request, args=(i,))
            x.start()
    except:
        logging.error(f"Error: unable to start thread")
        return False

    #All Good
    return True

## Get Current Load
def GetLoad():
    return config.current_load


# Function to make request
def make_request(name):
    config.current_load += 1
    for i in range(3):
        requests.get(url = config.load_test_url)
        time.sleep(random.randint(0, 20))
    config.current_load -= 1