import celery
import celery.result
import redis

import recastapi.request
import recastbackend.catalogue
import logging
import os
log = logging.getLogger(__name__)

def get_redis():
    log.info('getting celery from %s',os.environ['RECAST_CELERY_REDIS_HOST'])
    return redis.StrictRedis(host = os.environ['RECAST_CELERY_REDIS_HOST'],
                               db = os.environ['RECAST_CELERY_REDIS_DB'],
                             port = os.environ['RECAST_CELERY_REDIS_PORT'])

def joblist_key(basicreqid,backend):
    return 'recast:{}:{}:jobs'.format(basicreqid,backend)

def jobguid_to_celery_key(jobguid):
    return 'recast:{}:celery'.format(jobguid)

def celery_to_jobguid(celeryid):
    return 'recast:{}:jobguid'.format(celeryid)

def jobguid_message_key(jobguid):
    return 'recast:{}:msgs'.format(jobguid)

def register_job(basicreqid,backend,jobguid):
    #append his job to list of jobs of the request:parameter:backend
    red = get_redis()
    joblist = joblist_key(basicreqid,backend)
    log.info('taking note of a processing for basic request %s with backend %s. jobguid: %s store under: %s',basicreqid,backend,jobguid,joblist)
    red.rpush(joblist,jobguid)

def map_job_to_celery(jobguid,asyncresult_id):
    #map job id to celery id
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

def get_processings(basicreqid,backend):
    red = get_redis()
    jobs = red.lrange(joblist_key(basicreqid,backend),0,-1)
    return [{'job':job,'backend':backend,'celery':get_celery_status(get_celery_id(job))} for job in jobs]

def get_flattened_jobs(app,basicreq,backends):
    app.set_current()
    return [x for this_backend_proc in [get_processings(basicreq,b) for b in backends] for x in this_backend_proc]
