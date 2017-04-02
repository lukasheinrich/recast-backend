import logging
import os
import requests
import json
from recastcelery.messaging import get_stored_messages as redis_messages
from recastcelery.messaging import get_redis

log = logging.getLogger(__name__)

def workflow_submit(workflow_spec):
    log.info('submitting to workflow server: %s',workflow_spec)
    resp = requests.post(os.environ['RECAST_WORKFLOW_SERVER']+'/workflow_submit',
    					 headers = {'content-type': 'application/json'},
    					 data = json.dumps(workflow_spec),
            )
    celery_id = resp.json()['id']
    return celery_id

def workflow_status(processing_ids):
    resp = requests.get(os.environ['RECAST_WORKFLOW_SERVER']+'/workflow_submit',
    					 headers = {'content-type': 'application/json'},
    					 data = json.dumps({'workflow_ids': processing_ids}),
            )
    return resp.json()

def get_stored_messages(jobguid):
    return redis_messages(jobguid)

def logpublisher():
    return get_redis() 