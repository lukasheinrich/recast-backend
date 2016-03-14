import click

from recastbackend.fromenvapp import app

app.set_current()

from recastbackend.submission import submit_celery
from recastbackend.listener import yield_from_celery
import backendcontexts

@click.group()
def submit():
    pass

@submit.command()
@click.argument('input_url')
@click.argument('outputdir')
@click.argument('workflow')
@click.option('-q','--queue', default = 'recast_cap_queue')
@click.option('--track/--no-track',default = False)
def cap(input_url,outputdir,workflow,track,queue):
    ctx = backendcontexts.common_context(input_url,outputdir,backend = 'capdata')
    backendcontexts.cap_context(ctx,workflow)
    
    submit_celery
    print ctx

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
    # click.secho('submitted job with guid: {}'.format(jobguid),fg = 'green')
    # if track:
    #     for msgdata,_ in yield_from_celery(app,jobguid, lambda: result.ready()):
    #         click.secho('{date} :: {msg}'.format(**msgdata))
          
