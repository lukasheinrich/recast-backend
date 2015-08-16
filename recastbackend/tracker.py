import recastbackend.messaging
import json
import datetime
import click
import importlib
from recastbackend.submitter import wait_and_echo
from recastbackend.backendtasks import run_analysis
from recastbackend.jobstate import get_celery_id 


@click.command()
@click.argument('celeryapp')
@click.argument('jobguid')
def track(celeryapp,jobguid):
  module,attr = celeryapp.split(':')
  mod = importlib.import_module(module)
  app = getattr(mod,attr)
  app.set_current()

  stored = recastbackend.messaging.get_stored_messages(jobguid)
  click.secho('what happened so far',fg = 'white')
  for m in stored:
    msg   = click.style('{date} -- {msg}'.format(**json.loads(m)),fg = 'white')
    click.secho(msg)

  celery_id = get_celery_id(jobguid)
  result = run_analysis.AsyncResult(celery_id)

  click.secho('tuning in live at {}: '.format(datetime.datetime.now().strftime('%Y-%m-%d %X')), fg = 'green')
  wait_and_echo(result, room = jobguid)

