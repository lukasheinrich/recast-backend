import click
from .jobdb import all_jobs, job_details

@click.group()
def status():
    pass

@status.command()
@click.argument('jobguid')
def jobdetails(jobguid):
    details = job_details(jobguid)
    click.secho('Job {}  status: {}'.format(
        jobguid,
        details['status']
    ), fg = 'blue')

@status.command()
def jobs():
    joblist = all_jobs()
    for x in joblist:
        click.secho('{} - {}'.format(x,job_details(x)['status']))


if __name__ == '__main__':
    status()
