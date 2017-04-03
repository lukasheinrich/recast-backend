import msgpack
import click
import wflowapi

def yield_socketmsg_until(namespace = '/', breaker = None):
    for m in wflowapi.log_msg_stream(breaker):
        if m['type'] == 'message':
            data =  msgpack.unpackb(m['data'])[0]
            extras =  msgpack.unpackb(m['data'])[1]
            if(data['nsp'] == namespace):
                yield (data,extras)

def yield_room_msg_until(room = None, breaker = None):
    for data,extras in yield_socketmsg_until(namespace = '/monitor',breaker = breaker):
        if room: 
            if room not in extras['rooms']:    
                continue
        yield extras['rooms'],data['data'][1]

def yield_from_redis(room = None, breaker = None):
    for rooms,msgdata in yield_room_msg_until(room,breaker):
        yield msgdata,rooms

@click.command()
def listen():
    while True:
        try:
            click.secho('connected! start listening',fg = 'green')
            for msgdata,rooms in yield_from_redis():
                info = click.style('received message to rooms {rooms}: '.format(rooms = rooms),
                                   fg = 'black')
                msg   = click.style('{date} -- {msg}'.format(**msgdata),fg = 'blue')
                click.secho(info + msg)
        except KeyboardInterrupt:
            click.echo('\nGoodbye!')
            return

