import click
import os
import yaml
from recastbackend.fromenvapp import app

from recastbackend.submission import submit_celery
from recastbackend.listener import yield_from_celery
import backendcontexts

def track_result(result,jobguid):
    for msgdata,_ in yield_from_celery(app,jobguid, lambda: result.ready()):
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
@click.option('-q','--queue', default = 'recast_cap_queue')
@click.option('--track/--no-track',default = False)
def yadage(input_url,workflow,outputs,outputdir,track,queue,toplevel,presetyml):
    outputdir = outputdir
    ctx = backendcontexts.common_context(input_url,outputdir,'fromcli')
    explicit_results = backendcontexts.generic_yadage_outputs() + outputs.split(',')

    if presetyml:
        toload = open(presetyml) if os.path.exists(presetyml) else presetyml
        presetpars = yaml.load(toload)
        if not type(presetpars) == dict:
            raise click.ClickException(click.style('Sorry, but your presets don\'t appear to be a dictionary',fg = 'red'))
    else:
        presetpars = {}

    ctx = backendcontexts.yadage_context(
        ctx,workflow,
        toplevel,
        presetpars,
        explicit_results = explicit_results
    )
    result = submit_celery(ctx,queue)
    click.secho('submitted job with guid: {}'.format(ctx['jobguid']),fg = 'green')
    if track:
        track_result(result,ctx['jobguid'])
