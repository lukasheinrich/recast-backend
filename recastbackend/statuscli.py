import click
from recastcelery.fromenvapp import app as celeryapp
from recastbackend.jobstate import all_jobs, job_status, job_details

celeryapp.set_current()


@click.group()
def status():
    pass

@status.command()
@click.argument('jobguid')
def jobdetails(jobguid):
    details = job_details(jobguid)
    click.secho('Job {} (Celery {}) status: {}'.format(
        jobguid,
        details['celery_task'],
        details['status']
    ), fg = 'blue')

@status.command()
def jobs():
    joblist = all_jobs()
    for x in joblist:
        click.secho('{} - {}'.format(x,job_status(x)))


if __name__ == '__main__':
    status()
