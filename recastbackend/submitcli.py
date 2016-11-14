import click
import os
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
@click.argument('outputdir')
@click.option('-t','--toplevel', default = 'from-github/pseudocap')
@click.option('-q','--queue', default = 'recast_cap_queue')
@click.option('--track/--no-track',default = False)
def yadage(input_url,workflow,outputdir,track,queue,toplevel):
    outputdir = outputdir
    ctx = backendcontexts.common_context(input_url,outputdir,'dummyconfigname')
    wflowconfig = {
        'workflow':'madgraph_delphes.yml',
        'toplevel':'from-github/phenochain',
        'preset_pars':{}
    }
    explicit_results = backendcontexts.generic_yadage_outputs() + ['delphes/out.root']
    ctx = backendcontexts.yadage_context(
        ctx,wflowconfig['workflow'],
        wflowconfig['toplevel'],
        wflowconfig.get('preset_pars',{}),
        explicit_results = explicit_results
    )
    result = submit_celery(ctx,queue)
    click.secho('submitted job with guid: {}'.format(ctx['jobguid']),fg = 'green')
    if track:
        track_result(result,ctx['jobguid'])
