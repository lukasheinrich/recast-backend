import click
import uuid
import os

from recastbackend.fromenvapp import app
from recastbackend.submission import submit_generic_dedicated
from recastbackend.jobstate import map_job_to_celery
from recastbackend.listener import yield_from_celery


analysis_names_map = {
  'EwkTwoLepton':'recastdilepton.backendtasks'
}

@click.command()
@click.argument('input_url')
@click.argument('name')
@click.argument('queue')
@click.argument('outputdir')
@click.option('--track/--no-track',default = False)
def submit(input_url,name,queue,outputdir,track):
    if not name in analysis_names_map:
      click.secho('analysis not known', fg = 'red')
      return
    
    analysis_name = analysis_names_map[name]
    
    app.set_current()
    jobguid,result =  submit_generic_dedicated(analysis_name,
                                               queue,
                                               input_url,
                                               os.path.abspath(outputdir))
    map_job_to_celery(jobguid,result.id)
    click.secho('submitted job with guid: {}'.format(jobguid),fg = 'green')
    if track:
      for msgdata,_ in yield_from_celery(app,jobguid, lambda: result.ready()):
        click.secho('{date} :: {msg}'.format(**msgdata))
          
