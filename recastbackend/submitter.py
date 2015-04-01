# a method that can be used to write CLI to submit celery workflows to an app

import click
import importlib
import redis
import celery
import msgpack
import time

def get_parents(child):
  x = child.parent
  while x:
    yield x
    x = x.parent

def pubsub_or_ready(result,pubsub):
  while True:
    message = pubsub.get_message()
    # if our result is ready (failed or successful)
    # or one of the parents failed we're done
    if result.ready() or any(map(lambda x:x.failed(),get_parents(result))):
      return
    if message:
      yield message      
    time.sleep(0.001)  # be nice to the system :)    

def celery_submit_wrapped(uuid,parameter,wrapper_func,queue,modulename):
  analysis_module = importlib.import_module(modulename)
  analysis_chain  = analysis_module.get_chain(queue)
  j,c = wrapper_func(uuid,parameter,analysis_chain,analysis_module.resultlist,queue)
  result = c.apply_async()
  return result
      
def agnostic_submit(uuid,parameter,wrapper_func,queue,modulename):
  result = celery_submit_wrapped(uuid,parameter,wrapper_func,queue,modulename)

  click.secho('submitted chain for module {}'.format(modulename))
  
  red = redis.StrictRedis(host = celery.current_app.conf['CELERY_REDIS_HOST'],
                            db = celery.current_app.conf['CELERY_REDIS_DB'], 
                          port = celery.current_app.conf['CELERY_REDIS_PORT'])
  pubsub = red.pubsub()
  pubsub.subscribe('socket.io#emitter')
  for m in pubsub_or_ready(result,pubsub):
    if m['type'] == 'message':
      data =  msgpack.unpackb(m['data'])[0]
      extras =  msgpack.unpackb(m['data'])[1]
      if(data['nsp'] == '/monitor'):
        click.secho('received message: {date} -- {msg}'.format(**(data['data'][1])),fg = 'blue')
  if result.successful():
    click.secho('chain suceeded',fg = 'green')
  else:
    click.secho('chain failed somewhere',fg = 'red')
