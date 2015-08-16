import click

from recastbackend.submitter import wait_and_echo
from recastbackend.fromenvapp import app
from recastbackend.backendtasks import run_analysis

import recastbackend.backendtasks
import uuid
import os

analysis_names_map = {
  'EwkTwoLepton':'recastdilepton.backendtasks'
}

def submit_dedicated(analysis_name,queue,input_url,outputdir):
    jobguid = str(uuid.uuid1())

    ctx = {'jobguid': jobguid,
            'inputURL':input_url,
            'entry_point':'{}:recast'.format(analysis_name),
            'results':
            '{}:resultlist'.format(analysis_name),
            'backend':'dedicated',
            'shipout_base':outputdir}

    result = run_analysis.apply_async((recastbackend.backendtasks.setupFromURL,
                                       recastbackend.backendtasks.generic_onsuccess,
                                       recastbackend.backendtasks.cleanup,ctx),
                                       queue = queue)
    return jobguid,result

from recastbackend.jobstate import map_job_to_celery

@click.command()
@click.argument('input_url')
@click.argument('name')
@click.argument('queue')
@click.argument('outputdir')
def submit(input_url,name,queue,outputdir):
    if not name in analysis_names_map:
      click.secho('analysis not known', fg = 'red')
      return
      
    analysis_name = analysis_names_map[name]

    app.set_current()
    jobguid,result =  submit_dedicated(analysis_name,queue,input_url,os.path.abspath(outputdir))
    map_job_to_celery(jobguid,result.id)
    return wait_and_echo(result)
