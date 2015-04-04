import redis
import celery
import emitter
from datetime import datetime
import logging

def socketlog(jobguid,msg):
  red = redis.StrictRedis(host = celery.current_app.conf['CELERY_REDIS_HOST'],
                            db = celery.current_app.conf['CELERY_REDIS_DB'], 
                          port = celery.current_app.conf['CELERY_REDIS_PORT'])
  io  = emitter.Emitter({'client': red})

  msg_data = {'date':datetime.now().strftime('%Y-%m-%d %X'),'msg':msg}

  io.Of('/monitor').In(str(jobguid)).Emit('room_msg',msg_data)

class RecastLogger(logging.StreamHandler):
  def __init__(self,jobid):
    self.jobid = jobid
    logging.StreamHandler.__init__(self)
    
  def emit(self, record):
    socketlog(self.jobid,'{} -- {}'.format(record.levelname,record.msg))


def setupLogging(jobguid):
  #setup logging
  log = logging.getLogger('RECAST')
  recastlogger = RecastLogger(jobguid)
  log.setLevel(logging.INFO)
  log.addHandler(recastlogger)
  return log,recastlogger
  
