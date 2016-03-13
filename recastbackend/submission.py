import recastapi.request
import uuid
import recastbackend.backendtasks
from recastbackend.catalogue import all_backend_catalogue
from recastbackend.backendtasks import run_analysis
from recastbackend.productionapp import app

from recastbackend.jobstate import persist_job


import recastbackend.messaging

import logging
logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)


def get_queue_and_context(request_uuid,parameter,backend):
  if not backend in ['dedicated','rivet']:
    raise NotImplementedError

  request_info = recastapi.request.request(request_uuid)
  analysis_uuid = request_info['analysis-uuid']

  ctx = dict(
    jobguid       = str(uuid.uuid1()),
    requestguid   = request_uuid,
    parameter_pt  = parameter,
    backend       = backend,
  )
    
  if analysis_uuid not in all_backend_catalogue[backend]:
    raise NotImplementedError
    
  queuename = all_backend_catalogue[backend][analysis_uuid]['queue']
  workflownamemodule = all_backend_catalogue[backend][analysis_uuid]['workflow']
  ctx.update(
     entry_point   = '{}:recast'.format(workflownamemodule),
     results       = '{}:resultlist'.format(workflownamemodule)
  )
     
  if backend == 'dedicated':
    return (queuename, ctx)
    
  if backend == 'rivet':
    ctx.update(analysis = all_backend_catalogue[backend][analysis_uuid]['analysis'])
    return (queuename, ctx)
    

def production_celery_submit(request_uuid,parameter,backend):
  app.set_current()

  queue,ctx = get_queue_and_context(request_uuid,parameter,backend)
  
  # submit the job (with countdown to let this call finish)
  result =  run_analysis.apply_async(
                                     (
                                       recastbackend.backendtasks.setup,
                                       recastbackend.backendtasks.onsuccess,
                                       recastbackend.backendtasks.cleanup,
                                       ctx
                                     ),
                                     queue = queue,
                                     countdown=10
                                    )

  print "persisting job"
  persist_job(ctx,result.id)

  #push initial message
  recastbackend.messaging.socketlog(ctx['jobguid'],'registered. processed by celery id: {}'.format(result.id))

  
  return (ctx['jobguid'],result)


def submit_generic_dedicated(analysis_name,queue,input_url,outputdir,resultlist = None):
    jobguid = str(uuid.uuid1())

    ctx = {
        'jobguid': jobguid,
        'inputURL':input_url,
        'entry_point':'{}:recast'.format(analysis_name),
        'backend':'dedicated',
        'shipout_base':outputdir
    }

    if resultlist:
        ctx.update(resultlist = resultlist)
    else:
	    ctx.update(results = '{}:resultlist'.format(analysis_name))

    print 'submitting ctx {}'.format(ctx)
    result = None
    # result = run_analysis.apply_async((recastbackend.backendtasks.setupFromURL,
    #                                    recastbackend.backendtasks.generic_onsuccess,
    #                                    recastbackend.backendtasks.cleanup,ctx),
    #                                    queue = queue)
    return jobguid,result

def submit_recast_request(request_uuid,parameter,backend):
  print 'submitting {}/{} on {}'.format(request_uuid,parameter,backend)

  return production_celery_submit(request_uuid,parameter,backend)
