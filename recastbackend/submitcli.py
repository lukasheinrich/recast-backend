import click
import recastbackend.utils
from recastbackend.submitter import agnostic_submit
from recastbackend.productionapp import app

@click.command()
@click.argument('uuid')
@click.argument('parameter')
@click.argument('queue')
@click.argument('modulename')
def submit(uuid,parameter,queue,modulename):
    return agnostic_submit(uuid,parameter,recastbackend.utils.wrapped_chain,queue,modulename)
