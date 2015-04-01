import redis
import celery
import emitter
from datetime import datetime

def socketlog(jobguid,msg):
  red = redis.StrictRedis(host = celery.current_app.conf['CELERY_REDIS_HOST'],
                            db = celery.current_app.conf['CELERY_REDIS_DB'], 
                          port = celery.current_app.conf['CELERY_REDIS_PORT'])
  io  = emitter.Emitter({'client': red})

  msg_data = {'date':datetime.now().strftime('%Y-%m-%d %X'),'msg':msg}

  #also print directly
  print "{date} -- {msg}".format(**msg_data)

  io.Of('/monitor').In(str(jobguid)).Emit('room_msg',msg_data)
