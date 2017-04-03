import logging
import os
import requests
import json
import redis
import time

log = logging.getLogger(__name__)

def workflow_submit(workflow_spec):
    log.info('submitting to workflow server: %s',workflow_spec)
    resp = requests.post(os.environ['RECAST_WORKFLOW_SERVER']+'/workflow_submit',
    					 headers = {'content-type': 'application/json'},
    					 data = json.dumps(workflow_spec),
            )
    processing_id = resp.json()['id']
    return processing_id

def workflow_status(workflow_ids):
    resp = requests.get(os.environ['RECAST_WORKFLOW_SERVER']+'/workflow_status',
    					 headers = {'content-type': 'application/json'},
    					 data = json.dumps({'workflow_ids': workflow_ids}),
            )
    return resp.json()

def get_stored_messages(workflow_id):
    resp = requests.get(os.environ['RECAST_WORKFLOW_SERVER']+'/workflow_msgs',
                         headers = {'content-type': 'application/json'},
                         data = json.dumps({'workflow_id': workflow_id}),
            )
    return resp.json()

def all_jobs():
    return requests.get(os.environ['RECAST_WORKFLOW_SERVER']+'/jobs').json()

def logpubsub():
    server_data = requests.get(os.environ['RECAST_WORKFLOW_SERVER']+'/pubsub_server').json()
    red = redis.StrictRedis(host = server_data['host'],
                              db = server_data['db'],
                            port = server_data['port'],)
    pubsub = red.pubsub()
    pubsub.subscribe(server_data['channel'])
    return pubsub

def log_msg_until(breaker = None):
    pubsub = logpubsub()
    while True:
        if breaker and breaker():
            return
        message = pubsub.get_message()
        if message:
            yield message      
        time.sleep(0.001)  # be nice to the system :)    
