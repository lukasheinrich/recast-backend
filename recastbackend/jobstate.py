import celery
import celery.result
import redis

import recastapi.request
import recastbackend.catalogue


def get_redis_from_celery(app):
  return redis.StrictRedis(host = app.conf['CELERY_REDIS_HOST'],
                            db = app.conf['CELERY_REDIS_DB'], 
                          port = app.conf['CELERY_REDIS_PORT'])

def joblist_key(request_uuid,parameter_pt,backend):
  return 'recast:{}:{}:{}:jobs'.format(request_uuid,parameter_pt,backend)

def jobguid_to_celery_key(jobguid):
  return 'recast:{}:celery'.format(jobguid)

def jobguid_message_key(jobguid):
  return 'recast:{}:msgs'.format(jobguid)

def register_job(request_uuid,parameter_pt,backend,jobguid):
  #append his job to list of jobs of the request:parameter:backend
  red = get_redis_from_celery(celery.current_app)
  joblist = joblist_key(request_uuid,parameter_pt,backend)
  red.rpush(joblist,jobguid) 
  print "pushed onto {} the value {}".format(joblist,jobguid)
  
def map_job_to_celery(jobguid,asyncresult_id):
  #map job id to celery id
  red = get_redis_from_celery(celery.current_app)
  
  jobtocelery = jobguid_to_celery_key(jobguid)
  red.set(jobtocelery,asyncresult_id)
  print "mapped jobguid to celery"
  

def persist_job(ctx,result_id):
  request_uuid,parameter,backend,jobguid = ctx['requestguid'],ctx['parameter_pt'],ctx['backend'],ctx['jobguid']

  #append his job to list of jobs of the request:parameter:backend
  register_job(request_uuid,parameter,backend,jobguid)

  #map job id to celery id
  map_job_to_celery(jobguid,result_id)


def get_celery_id(jobguid):
  red = get_redis_from_celery(celery.current_app)
  return red.get(jobguid_to_celery_key(jobguid))

def get_celery_status(celery_id):
  print "current celery is: {}".format(celery.current_app)
  print "getting result for {}".format(celery_id)
  return celery.result.AsyncResult(celery_id).state


def get_processings(request_uuid,parameter_pt,backend):
  red = get_redis_from_celery(celery.current_app)
  jobs = red.lrange(joblist_key(request_uuid,parameter_pt,backend),0,-1)
  return [{'job':job,'backend':backend,'celery':get_celery_status(get_celery_id(job))} for job in jobs]
  
def get_flattened_jobs(app,request_uuid,parameter_pt):
  app.set_current()
  request_info = recastapi.request.request(request_uuid)
  analysis_uuid = request_info['analysis-uuid']
  backends = recastbackend.catalogue.getBackends(analysis_uuid)
  nested =  [get_processings(request_uuid,parameter_pt,backend) for backend in backends]

  #flatten
  return [x for sublist in nested for x in sublist]
