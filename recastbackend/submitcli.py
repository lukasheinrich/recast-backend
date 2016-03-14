import click
from recastbackend.submission import submit_recast_request
from recastbackend.listener import wait_and_echo
from recastbackend.fromenvapp import app

@click.command()
@click.argument('uuid')
@click.argument('parameter')
@click.argument('backend')
def submit(uuid,parameter,backend):
    app.set_current()
    jobguid,result =  submit_recast_request(uuid,parameter,backend)
    return wait_and_echo(result)
