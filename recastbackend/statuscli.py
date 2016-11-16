import click
from recastbackend.fromenvapp import app as celeryapp
celeryapp.set_current()

from recastbackend.jobstate import get_redis,get_celery_status,get_celery_id
import re


def getjobstatus(jobid):
    celerytask = get_celery_id(jobid)
    status = get_celery_status(celerytask)
    return status

@click.group()
def status():
    pass

@status.command()
@click.argument('jobid')
def jobstatus(jobid):
    celerytask = get_celery_id(jobid)
    status = get_celery_status(celerytask)
    click.secho('Job {} (Celery {}) status: {}'.format(jobid,celerytask,status), fg = 'blue')

@status.command()
def jobs():
    r = get_redis()
    joblist = [x.group(0).split(':')[1] for x in [re.match('recast:.*:celery',x) for x in r.keys()] if x]
    for x in joblist:
        click.secho('{} - {}'.format(x,getjobstatus(x)))


if __name__ == '__main__':
    status()
