# a method that can be used to write CLI to submit celery workflows to an app

import click
import redis
import celery
from recastbackend.listener import yieldsocketmsg_until

def get_parents(child):
  x = child.parent
  while x:
    yield x
    x = x.parent

def wait_and_echo(result):
  red = redis.StrictRedis(host = celery.current_app.conf['CELERY_REDIS_HOST'],
                            db = celery.current_app.conf['CELERY_REDIS_DB'], 
                          port = celery.current_app.conf['CELERY_REDIS_PORT'])
  pubsub = red.pubsub()
  pubsub.subscribe('socket.io#emitter')


  def result_ready_or_failed():
    return (result.ready() or any(map(lambda x:x.failed(),get_parents(result))))

  for data,extras in yieldsocketmsg_until(pubsub,namespace = '/monitor',breaker = result_ready_or_failed):
    info = click.style('received message to rooms {rooms}: '.format(rooms = extras['rooms']), fg = 'black')
    msg   = click.style('{date} -- {msg}'.format(**(data['data'][1])),fg = 'blue')
    click.secho(info + msg)

  if result.successful():
    click.secho('chain suceeded',fg = 'green')
  else:
    click.secho('chain failed somewhere',fg = 'red')
