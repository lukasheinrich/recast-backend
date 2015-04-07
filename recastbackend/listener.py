import redis
import msgpack
import time
import click
import celery


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


def yieldsocketmsg_until(pubsub,namespace = '/',breaker = lambda: False):
  for m in yield_redis_msg_until(pubsub,breaker):
    if m['type'] == 'message':
      data =  msgpack.unpackb(m['data'])[0]
      extras =  msgpack.unpackb(m['data'])[1]
      if(data['nsp'] == namespace):
        yield (data,extras)


def get_socket_pubsub():
  red = redis.StrictRedis(host = celery.current_app.conf['CELERY_REDIS_HOST'],
                            db = celery.current_app.conf['CELERY_REDIS_DB'], 
                          port = celery.current_app.conf['CELERY_REDIS_PORT'])
  pubsub = red.pubsub()
  pubsub.subscribe('socket.io#emitter')
  return pubsub

click.command()
def listen():
  while True:
    try:
      pubsub = get_socket_pubsub()
      click.secho('connected! start listening',fg = 'green')

      for data,extras in yieldsocketmsg_until(pubsub,namespace = '/monitor'):
        info = click.style('received message to rooms {rooms}: '.format(rooms = extras['rooms']), fg = 'black')
        msg   = click.style('{date} -- {msg}'.format(**(data['data'][1])),fg = 'blue')
        click.secho(info + msg)

    except redis.exceptions.ConnectionError:
      click.echo('could not connect. sleeping.')
      time.sleep(1)
    except KeyboardInterrupt:
      click.echo('Goodbye')
      return

