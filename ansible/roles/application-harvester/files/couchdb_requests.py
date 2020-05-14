import requests
import logging
import http
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
from requests_toolbelt.utils import dump

logger = logging.getLogger('CouchDB')
couch_vars = {"COUCHDB_BASE_URL": "http://172.26.133.111:8080/", "USERNAME": "admin", "PASSWORD": "admin"}
def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 504),
    method_whitelist=["HEAD", "GET", "PUT", "DELETE", "POST"],
    session=None,
    couch_vars={}
):
    """
    
    Function to ensure that there's fault tolerance when making API Calls to Couch 
    retries -> Total number of retries
    backoff_factor -> How long the processes will sleep between failed requests
        Calculation for it is = {backoff factor} * (2 ** ({number of total retries} - 1))
    status_forcelist -> The HTTP response codes to retry on
    session -> Deafult to create a new session otherwise use an existing
    method_whitelist -> The HTTP methods to retry on
    vars -> Variables dictionary
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=method_whitelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    # Uncomment line below to get logging on the request
    # session.hooks["response"] = [logging_hook]
    session.auth = (couch_vars['USERNAME'], couch_vars['PASSWORD'])
    return session

def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))

def couchdb_test():
    try:
        s = requests.Session()
        response = requests_retry_session(session=s, couch_vars=couch_vars).get(couch_vars['COUCHDB_BASE_URL']+'_uuids')
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
           logger.exception("Bad Request was Sent")
        else:
           logger.exception(e.__class__.__name__)
    except Exception as e: 
        print('Failure Caused by ', e.__class__.__name__)
    else:
        print('It eventually worked', response.status_code)
   
def couch_post(tweet):
    print(tweet)
    try:
        s = requests.Session()
        response = requests_retry_session(session=s, couch_vars=couch_vars).post(couch_vars['COUCHDB_BASE_URL'] + "twitter", json = tweet)
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
           logger.exception("Bad Request was Sent")
        else:
           logger.exception(e.__class__.__name__)
    except Exception as e: 
        print('Failure Caused by ', e.__class__.__name__)
        return False
    else:
        print(response.json())
        print('It eventually worked', response.status_code)
        return
    

    