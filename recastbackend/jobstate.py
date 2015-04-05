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
  print "pusing onto {} the value {}".format(joblist,jobguid)
  red.rpush(joblist,jobguid) 
  
def map_job_to_celery(jobguid,asyncresult_id):
  #map job id to celery id
  red = get_redis_from_celery(celery.current_app)
  
  jobtocelery = jobguid_to_celery_key(jobguid)
  red.set(jobtocelery,asyncresult_id)
  

def persist_job(ctx,result_id):
  request_uuid,parameter,backend,jobguid = ctx['requestguid'],ctx['parameter_pt'],ctx['backend'],ctx['jobguid']

  #append his job to list of jobs of the request:parameter:backend
  recastbackend.jobstate.register_job(request_uuid,parameter,backend,jobguid)

  #map job id to celery id
  recastbackend.jobstate.map_job_to_celery(jobguid,result_id)

  #push initial message
  recastbackend.messaging.socketlog(jobguid,'registered. processed by celery id: {}'.format(result_id))

