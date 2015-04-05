import celery
import redis

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

