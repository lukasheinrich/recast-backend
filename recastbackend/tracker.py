
import json
import datetime
import click
import importlib
from recastbackend.listener import wait_and_echo
from recastbackend.backendtasks import run_analysis
from recastbackend.jobstate import get_result_obj
from recastbackend.messaging import get_stored_messages

@click.command()
@click.argument('jobguid')
@click.option('-c','--celeryapp',default = 'recastbackend.fromenvapp:app')
def track(celeryapp,jobguid):
  try:
    module,attr = celeryapp.split(':')
    mod = importlib.import_module(module)
    app = getattr(mod,attr)
    app.set_current()
    
    stored = get_stored_messages(jobguid)
    click.secho('=====================',fg = 'black')
    click.secho('What happened so far:',fg = 'black')
    click.secho('=====================',fg = 'black')
    for m in stored:
      msg   = click.style('{date} -- {msg}'.format(**json.loads(m)),fg = 'black')
      click.secho(msg)
      
    click.secho('=====================',fg = 'green')
    click.secho('Tuning in live at {}: '.format(datetime.datetime.now().strftime('%Y-%m-%d %X')), fg = 'green')
    click.secho('=====================',fg = 'green')
    wait_and_echo(get_result_obj(jobguid), room = jobguid)
    
  except KeyboardInterrupt:
    click.secho('bye bye.')
    return
