import celery
import celery.result
import logging
import re

from recastcelery.messaging import get_redis
from recastcelery.messaging import jobguid_message_key as redis_msg_keys
from recastcelery.messaging import get_stored_messages as redis_messages

log = logging.getLogger(__name__)


### forward messaging methods

def jobguid_message_key(jobguid):
    return redis_msg_keys(jobguid)

def get_stored_messages(jobguid):
    return redis_messages(jobguid)

###

def joblist_key(basicreqid,wflowconfig):
    return 'recast:{}:{}:jobs'.format(basicreqid,wflowconfig)

def jobguid_to_celery_key(jobguid):
    return 'recast:{}:celery'.format(jobguid)

def celery_to_jobguid(celeryid):
    return 'recast:{}:jobguid'.format(celeryid)

def register_job(basicreqid,wflowconfig,jobguid):
    #append his job to list of jobs of the request:parameter:wflowconfig
    red = get_redis()
    joblist = joblist_key(basicreqid,wflowconfig)
    log.info('taking note of a processing for basic request %s with wflowconfig %s. jobguid: %s store under: %s',basicreqid,wflowconfig,jobguid,joblist)
    red.rpush(joblist,jobguid)

def map_job_to_celery(jobguid,asyncresult_id):
    red = get_redis()

    jobtocelery = jobguid_to_celery_key(jobguid)
    red.set(jobtocelery,asyncresult_id)

    celerytojob = celery_to_jobguid(asyncresult_id)
    red.set(celerytojob,jobguid)

def get_celery_id(jobguid):
    red = get_redis()
    return red.get(jobguid_to_celery_key(jobguid))

def get_jobguid_id(celeryid):
    red = get_redis()
    return red.get(celery_to_jobguid(celeryid))

def get_result_obj(jobguid):
    celery_id = get_celery_id(jobguid)
    result = celery.result.AsyncResult(celery_id)
    return result

def get_celery_status(celery_id):
    return celery.result.AsyncResult(celery_id).state

def get_processings(basicreqid,wflowconfig):
    red = get_redis()
    jobs = red.lrange(joblist_key(basicreqid,wflowconfig),0,-1)
    return [{'job':job,'wflowconfig':wflowconfig,'celery':get_celery_status(get_celery_id(job))} for job in jobs]

def get_flattened_jobs(app,basicreq,wflowconfigs):
    app.set_current()
    return [x for this_config_proc in [get_processings(basicreq,wc) for wc in wflowconfigs] for x in this_config_proc]


def all_jobs():
    red = get_redis()
    joblist = [x.group(0).split(':')[1] for x in [re.match('recast:.*:celery',x) for x in red.keys()] if x]
    return joblist

def job_details(jobguid):
    celerytask = get_celery_id(jobguid)
    detail_data = {
        'job_type': 'celery',
        'celery_task': get_celery_id(jobguid),
        'status': get_celery_status(celerytask)
    }
    return detail_data

def job_status(jobguid):
    celerytask = get_celery_id(jobguid)
    status = get_celery_status(celerytask)
    return status
