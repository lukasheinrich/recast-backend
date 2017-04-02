import logging
import re
import wflowapi
import redis
import os

def wflow_processing_database():
   return redis.StrictRedis(
                host = os.environ.get('RECAST_PROCDB_REDIS_HOST','localhost'),
                db   = os.environ.get('RECAST_PROCDB_REDIS_DB',0),
                port = os.environ.get('RECAST_PROCDB_REDIS_PORT',6379)
          ) 

log = logging.getLogger(__name__)
wflowprocdb = wflow_processing_database()

def joblist_key(basicreqid,wflowconfig):
    return 'recast:{}:{}:jobs'.format(basicreqid,wflowconfig)

def jobguid_to_celery_key(jobguid):
    return 'recast:{}:celery'.format(jobguid)

def celery_to_jobguid(celeryid):
    return 'recast:{}:jobguid'.format(celeryid)

def register_job(basicreqid,wflowconfig,jobguid):
    #append his job to list of jobs of the request:parameter:wflowconfig
    joblist = joblist_key(basicreqid,wflowconfig)
    log.info('taking note of a processing for basic request %s with wflowconfig %s. jobguid: %s store under: %s',basicreqid,wflowconfig,jobguid,joblist)
    wflowprocdb.rpush(joblist,jobguid)

def map_job_to_celery(jobguid,asyncresult_id):
    jobtocelery = jobguid_to_celery_key(jobguid)
    wflowprocdb.set(jobtocelery,asyncresult_id)
    celerytojob = celery_to_jobguid(asyncresult_id)
    wflowprocdb.set(celerytojob,jobguid)

def get_celery_id(jobguid):
    return wflowprocdb.get(jobguid_to_celery_key(jobguid))

def get_jobguid_id(celeryid):
    return wflowprocdb.get(celery_to_jobguid(celeryid))

def get_processings(basicreqid,wflowconfig):
    jobs = wflowprocdb.lrange(joblist_key(basicreqid,wflowconfig),0,-1)
    return [{'job':job,'wflowconfig':wflowconfig,'celery': wflowapi.workflow_status([get_celery_id(job)])} for job in jobs]

def get_flattened_jobs(app,basicreq,wflowconfigs):
    return [x for this_config_proc in [get_processings(basicreq,wc) for wc in wflowconfigs] for x in this_config_proc]

def all_jobs():
    joblist = [x.group(0).split(':')[1] for x in [re.match('recast:.*:celery',x) for x in wflowprocdb.keys()] if x]
    return joblist

def job_details(jobguid):
    return jobs_details([jobguid])

def jobs_details(jobguids):
    celerytasks = [get_celery_id(jobid) for jobid in jobguids]
    status     = wflowapi.workflow_status(celerytasks)

    details = {jobid: {
        'job_type': 'celery',
        'celery_task': cid,
        'status': status
        } for jobid,cid,status in zip(jobguids,celerytasks,status)
    }
    return details
