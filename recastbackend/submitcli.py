import click
import os
import yaml

from recastbackend.submission import yadage_submission
from recastbackend.listener import yield_from_redis
import wflowapi

def track_result(processing_id):
    for msgdata,_ in yield_from_redis(room = processing_id, breaker = lambda: wflowapi.workflow_status([processing_id]) in ['SUCCESS','FAILURE']):
        click.secho('{date} :: {msg}'.format(**msgdata))

@click.group()
def submit():
    pass

@submit.command()
@click.argument('input_url')
@click.argument('workflow')
@click.argument('outputs')
@click.argument('outputdir')
@click.option('-p','--presetyml', default = '')
@click.option('-t','--toplevel', default = 'from-github/pseudocap')
@click.option('-q','--queue', default = 'recast_yadage_queue')
@click.option('--track/--no-track',default = False)
def yadage(input_url,workflow,outputs,outputdir,track,queue,toplevel,presetyml):
    if presetyml:
        toload = open(presetyml) if os.path.exists(presetyml) else presetyml
        presetpars = yaml.load(toload)
        if not type(presetpars) == dict:
            raise click.ClickException(click.style('Sorry, but your presets don\'t appear to be a dictionary',fg = 'red'))
    else:
        presetpars = {}

    ctx, processing_id = yadage_submission(input_url,outputdir,'fromcli',outputs.split(','), workflow,toplevel,presetpars,queue)
    click.secho('submitted job with guid: {}'.format(processing_id),fg = 'green')
    if track:
        track_result(processing_id)
