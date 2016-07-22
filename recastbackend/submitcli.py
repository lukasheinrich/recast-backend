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
def cap(input_url,workflow,outputdir,track,queue,toplevel):
    ctx = backendcontexts.common_context(input_url,os.path.abspath(outputdir),backend = 'capbackend')
    backendcontexts.cap_context(ctx,workflow,toplevel)

    result = submit_celery(ctx,queue)
    click.secho('submitted job with guid: {}'.format(ctx['jobguid']),fg = 'green')
    if track:
        track_result(result,ctx['jobguid'])



@click.argument('input_url')
@click.argument('name')
@click.argument('queue')
@click.argument('outputdir')
@click.option('--track/--no-track',default = False)
def none_submit(input_url,name,queue,outputdir,track):
    print "hello"
    
    print yield_from_celery
    
    # if not name in analysis_names_map:
    #   click.secho('analysis not known', fg = 'red')
    #   return
    #
    # analysis_name = analysis_names_map[name]['module']
    # resultlist = analysis_names_map[name]['resultlist']
    #
    # app.set_current()
    #
    # jobguid,result =  submit_generic_dedicated(analysis_name,
    #                                            queue,
    #                                            input_url,
    #                                            os.path.abspath(outputdir),
    #                                                resultlist = resultlist)
    # return
    # map_job_to_celery(jobguid,result.id)

