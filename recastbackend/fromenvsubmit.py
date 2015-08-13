import click

from recastbackend.submitter import wait_and_echo
from recastbackend.fromenvapp import app
from recastbackend.backendtasks import run_analysis

import recastbackend.backendtasks
import uuid

analysis_names_map = {
  'EwkTwoLepton':'recastdilepton.backendtasks'
}

def submit_dedicated(analysis_name,queue,input_url):
    jobguid = str(uuid.uuid1())

    ctx = {'jobguid': jobguid,
            'inputURL':input_url,
            'entry_point':'{}:recast'.format(analysis_name),
            'results':
            '{}:resultlist'.format(analysis_name),
            'backend':'dedicated'}

    result = run_analysis.apply_async((recastbackend.backendtasks.setupFromURL,
                                       recastbackend.backendtasks.dummy_onsuccess,
                                       recastbackend.backendtasks.cleanup,ctx),
                                       queue = queue)
    return jobguid,result

@click.command()
@click.argument('input_url')
@click.argument('name')
@click.argument('queue')
def submit(input_url,name,queue):
    if not name in analysis_names_map:
      click.secho('analysis not known', fg = 'red')
      return
      
    analysis_name = analysis_names_map[name]

    app.set_current()
    jobguid,result =  submit_dedicated(analysis_name,queue,input_url)
    return wait_and_echo(result)
