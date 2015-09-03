import redis
import msgpack
import time
import click
import celery
import importlib

def yield_redis_msg_until(pubsub,breaker):
  while True:
    message = pubsub.get_message()
    # if our result is ready (failed or successful)
    # or one of the parents failed we're done
    if breaker():
      return
    if message:
      yield message      
    time.sleep(0.001)  # be nice to the system :)    

def yield_socketmsg_until(pubsub,namespace = '/',breaker = lambda: False):
  for m in yield_redis_msg_until(pubsub,breaker):
    if m['type'] == 'message':
      data =  msgpack.unpackb(m['data'])[0]
      extras =  msgpack.unpackb(m['data'])[1]
      if(data['nsp'] == namespace):
        yield (data,extras)

def yield_room_msg_until(pubsub,room = None,breaker = lambda: False):
  for data,extras in yield_socketmsg_until(pubsub,namespace = '/monitor',breaker = breaker):
    if room: 
      if not room in extras['rooms']:    
        continue
    yield  extras['rooms'],data['data'][1]

def get_socket_pubsub(celery_app):
  red = redis.StrictRedis(host = celery_app.conf['CELERY_REDIS_HOST'],
                            db = celery_app.conf['CELERY_REDIS_DB'], 
                          port = celery_app.conf['CELERY_REDIS_PORT'])
  pubsub = red.pubsub()
  pubsub.subscribe('socket.io#emitter')
  return pubsub

def yield_from_celery(app, room = None, breaker = lambda: False):
  pubsub = get_socket_pubsub(app)
  for rooms,msgdata in yield_room_msg_until(pubsub,room,breaker):
    yield msgdata,rooms

def wait_and_echo(result, room = None):
  for msgdata,rooms in yield_from_celery(celery.current_app,room, lambda: result.ready()):
    info = click.style('received message to rooms {rooms}: '.format(rooms = rooms), fg = 'black')
    msg   = click.style('{date} -- {msg}'.format(**msgdata),fg = 'blue')
    click.secho(info + msg)
    
  if result.successful():
    click.secho('chain suceeded',fg = 'green')
  else:
    click.secho('chain failed somewhere',fg = 'red')



@click.command()
@click.option('-c','--celeryapp',default = 'recastbackend.fromenvapp:app') 
def listen(celeryapp):
  module,attr = celeryapp.split(':')
  mod = importlib.import_module(module)
  app = getattr(mod,attr)
  app.set_current()
  while True:
    try:
      click.secho('connected! start listening',fg = 'green')
      
      for msgdata,rooms in yield_from_celery(app):
        info = click.style('received message to rooms {rooms}: '.format(rooms = rooms),
                           fg = 'black')
        msg   = click.style('{date} -- {msg}'.format(**msgdata),fg = 'blue')
        click.secho(info + msg)
    except KeyboardInterrupt:
      click.echo('\nGoodbye!')
      return

