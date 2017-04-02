import msgpack
import time
import click

import wflowapi

def yield_redis_msg_until(pubsub,breaker):
    while True:
        message = pubsub.get_message()
        # if our result is ready (failed or successful)
        # or one of the parents failed we're done
        if breaker():
            return
        if message:
            yield message      
        time.sleep(0.001)  # be nice to the system :)    

def yield_socketmsg_until(pubsub,namespace = '/',breaker = lambda: False):
    for m in yield_redis_msg_until(pubsub,breaker):
        if m['type'] == 'message':
            data =  msgpack.unpackb(m['data'])[0]
            extras =  msgpack.unpackb(m['data'])[1]
            if(data['nsp'] == namespace):
                yield (data,extras)

def yield_room_msg_until(pubsub,room = None,breaker = lambda: False):
    for data,extras in yield_socketmsg_until(pubsub,namespace = '/monitor',breaker = breaker):
        if room: 
            if room not in extras['rooms']:    
                continue
        yield extras['rooms'],data['data'][1]

def yield_from_redis(room = None, breaker = lambda: False):
    pubsub = wflowapi.logpubsub()
    for rooms,msgdata in yield_room_msg_until(pubsub,room,breaker):
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

