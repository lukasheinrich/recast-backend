import click
import logging
import os
import yaml
import recastbackend.wflowapi
import recastbackend.backendcontexts

from .submission import submit_workflow

def yadage_submission(input_url,outputdir,configname,outputs,workflow,toplevel,presetpars,queue):
    ctx = recastbackend.backendcontexts.common_context(input_url,outputdir,configname)
    ctx = recastbackend.backendcontexts.yadage_context(
        ctx,workflow,
        toplevel,
        presetpars,
        explicit_results = recastbackend.backendcontexts.generic_yadage_outputs() + outputs
    )
    return ctx, submit_workflow(ctx,queue)

def track_result(processing_id):
    for msg in recastbackend.wflowapi.log_msg_stream(
        breaker = lambda: recastbackend.wflowapi.workflow_status([processing_id])[0] in ['SUCCESS','FAILURE']
        ):
        if msg['msg_type'] == 'wflow_log' and msg['wflowguid'] == processing_id:
            click.secho('{date} :: {msg}'.format(**msg))

@click.group()
def submit():
    pass

@submit.command()
@click.argument('workflow')
@click.argument('outputs')
@click.argument('outputdir')
@click.option('-i','--input_url', default = None)
@click.option('-p','--presetyml', default = '')
@click.option('-t','--toplevel', default = 'from-github/pseudocap')
@click.option('-q','--queue', default = 'yadage_queue')
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
