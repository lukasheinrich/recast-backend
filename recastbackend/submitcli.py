import click
import recastbackend.utils
from recastbackend.submission import production_celery_submit
from recastbackend.submitter import wait_and_echo
from recastbackend.productionapp import app

@click.command()
@click.argument('uuid')
@click.argument('parameter')
@click.argument('backend')
def submit(uuid,parameter,backend):
    app.set_current()
    jobguid,result =  production_celery_submit(uuid,parameter,backend)
    return wait_and_echo(result)
