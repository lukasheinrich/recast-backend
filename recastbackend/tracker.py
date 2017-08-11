import json
import datetime
import click
import recastbackend.wflowapi

@click.command()
@click.argument('jobguid')
@click.option('-e','--exit')
def track(jobguid,exit):
    try:
        stored = recastbackend.wflowapi.get_workflow_messages(jobguid,'log')
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

        for msgdata,_ in yield_from_redis(
                room = jobguid,
                breaker = lambda: recastbackend.wflowapi.workflow_status([jobguid])[0] in ['SUCCESS','FAILURE']):
            click.secho('{date} :: {msg}'.format(**msgdata))

    except KeyboardInterrupt:
        click.secho('bye bye.')
        return
