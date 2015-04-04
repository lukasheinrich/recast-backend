import click
from recastbackend.submission import production_celery_submit
from recastbackend.submitter import wait_and_echo
from recastbackend.productionapp import app

def production_dedicated_celery_submit(uuid,parameter,modulename):
  queue = 'celery'
  jobguid = '0.0.0.0'
  app.set_current()

  ctx = dict(
      jobguid       = jobguid,
      requestguid   = uuid,
      parameter_pt  = parameter,
      entry_point   = '{}:recast'.format(modulename),
      results       = '{}:resultlist'.format(modulename),
      backend       = 'dedicated'
  )

  result =  run_analysis.apply_async((recastbackend.backendtasks.setup,
                                      recastbackend.backendtasks.onsuccess,
                                      recastbackend.backendtasks.cleanup,
                                      ctx),
                                      queue = queue)
  return (jobguid,result)

@click.command()
@click.argument('uuid')
@click.argument('parameter')
@click.argument('backend')
def submit(uuid,parameter,backend):
    app.set_current()
    jobguid,result =  production_celery_submit(uuid,parameter,backend)
    return wait_and_echo(result)
