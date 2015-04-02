import recastapi.request
from recastbackend.catalogue import implemented_analyses

from recastbackend.submitter import celery_submit_wrapped
import recastbackend.utils

from recastbackend.productionapp import app as celery_app

def dedicated_submit(uuid,parameter):
  request_info = recastapi.request.request(uuid)
  analysis_uuid = request_info['analysis-uuid']

  if analysis_uuid not in implemented_analyses:
    raise NotImplementedError

  workflowmodulename = implemented_analyses[analysis_uuid]['workflow']
  queuename = implemented_analyses[analysis_uuid]['queue']

  jobguid,result = celery_submit_wrapped(uuid,parameter,recastbackend.utils.wrapped_chain,queue = queuename,modulename = workflowmodulename)
  return jobguid,result
  

def submit_recast_request(uuid,parameter,backend):
  supported_backends = ['dedicated']
  celery_app.set_current()

  print 'submitting {}/{} on {}'.format(uuid,parameter,backend)
  
  if backend not in supported_backends:
    print "backend {} not implemented".format(backend)
    raise NotImplementedError

  if backend == 'dedicated':
    return dedicated_submit(uuid,parameter)
