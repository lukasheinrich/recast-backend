# a method that can be used to write CLI to submit celery workflows to an app

import click
import redis
import celery
from recastbackend.listener import yieldsocketmsg_until

def wait_and_echo(result, room = None):
  red = redis.StrictRedis(host = celery.current_app.conf['CELERY_REDIS_HOST'],
                            db = celery.current_app.conf['CELERY_REDIS_DB'], 
                          port = celery.current_app.conf['CELERY_REDIS_PORT'])
  pubsub = red.pubsub()
  pubsub.subscribe('socket.io#emitter')

  for data,extras in yieldsocketmsg_until(pubsub,namespace = '/monitor',breaker = lambda: result.ready()):
    if room:
      if not room in extras['rooms']:
        continue

    info = click.style('received message to rooms {rooms}: '.format(rooms = extras['rooms']), fg = 'black')
    msg   = click.style('{date} -- {msg}'.format(**(data['data'][1])),fg = 'blue')
    click.secho(info + msg)

  if result.successful():
    click.secho('chain suceeded',fg = 'green')
  else:
    click.secho('chain failed somewhere',fg = 'red')
