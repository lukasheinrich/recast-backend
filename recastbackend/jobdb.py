import logging
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

######### Generic Job DB stuff
#########

def all_jobs():
    return wflowapi.all_jobs()

def job_details(jobguid):
    return jobs_details([jobguid])

def jobs_details(jobguids):
    status     = wflowapi.workflow_status(jobguids)
    details = {jobid: {
        'job_type': 'workflow',
        'status': status
        } for jobid,status in zip(jobguids,status)
    }
    return details

######### RECAST specific Job DB stuff
#########

def joblist_key(basicreqid,wflowconfig):
    return 'recast:{}:{}:jobs'.format(basicreqid,wflowconfig)

def register_job(basicreqid,wflowconfig,jobguid):
    # append his job to list of jobs of the request:parameter:wflowconfig
    joblist = joblist_key(basicreqid,wflowconfig)
    log.info('taking note of a processing for basic request %s with wflowconfig %s. jobguid: %s store under: %s',basicreqid,wflowconfig,jobguid,joblist)
    wflowprocdb.rpush(joblist,jobguid)

def get_processings(basicreqid,wflowconfig):
    jobs = wflowprocdb.lrange(joblist_key(basicreqid,wflowconfig),0,-1)
    return [{'job':job,'wflowconfig':wflowconfig, 'status': wflowapi.workflow_status([job])} for job in jobs]

def get_flattened_jobs(basicreq,wflowconfigs):
    return [x for this_config_proc in [get_processings(basicreq,wc) for wc in wflowconfigs] for x in this_config_proc]
