import redis
from recastbackend.productionapp import app as productionapp
import msgpack
import time
import click


def yield_redis_msg_until(pubsub, breaker = lambda: False):
  while True:
    message = pubsub.get_message()
    # if our result is ready (failed or successful)
    # or one of the parents failed we're done
    if breaker():
      return
    if message:
      yield message      
    time.sleep(0.001)  # be nice to the system :)    


def yieldsocketmsg(pubsub,namespace = '/'):
  for m in yield_redis_msg_until(pubsub):
    if m['type'] == 'message':
      data =  msgpack.unpackb(m['data'])[0]
      extras =  msgpack.unpackb(m['data'])[1]
      if(data['nsp'] == namespace):
        yield (data,extras)


def get_socket_pubsub():
  red = redis.StrictRedis(host = productionapp.conf['CELERY_REDIS_HOST'],
                            db = productionapp.conf['CELERY_REDIS_DB'], 
                          port = productionapp.conf['CELERY_REDIS_PORT'])
  pubsub = red.pubsub()
  pubsub.subscribe('socket.io#emitter')
  return pubsub

click.command()
def listen():
  while True:
    try:
      pubsub = get_socket_pubsub()
      click.secho('connected! start listening',fg = 'green')

      for data,extras in yieldsocketmsg(pubsub,namespace = '/monitor'):
        info = click.style('received message to rooms {rooms}: '.format(rooms = extras['rooms']), fg = 'black')
        msg   = click.style('{date} -- {msg}'.format(**(data['data'][1])),fg = 'blue')
        click.secho(info + msg)

    except redis.exceptions.ConnectionError:
      click.echo('could not connect. sleeping.')
      time.sleep(1)
    except KeyboardInterrupt:
      click.echo('Goodbye')
      return

