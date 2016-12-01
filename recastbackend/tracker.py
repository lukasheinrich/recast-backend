import json
import datetime
import click
import importlib

from recastbackend.listener import yield_from_redis
from recastbackend.jobstate import get_result_obj, get_stored_messages

@click.command()
@click.argument('jobguid')
@click.option('-e','--exit')
@click.option('-c','--celeryapp',default = 'recastcelery.fromenvapp:app')
def track(celeryapp,jobguid,exit):
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

        if exit:
            return

        click.secho('=====================',fg = 'green')
        click.secho('Tuning in live at {}: '.format(datetime.datetime.now().strftime('%Y-%m-%d %X')), fg = 'green')
        click.secho('=====================',fg = 'green')

        result = get_result_obj(jobguid)
        for msgdata,_ in yield_from_redis(app,jobguid, lambda: result.ready()):
            click.secho('{date} :: {msg}'.format(**msgdata))

    except KeyboardInterrupt:
        click.secho('bye bye.')
        return
