import importlib
import pickle
import pkg_resources
import recastapi.request
import uuid
import recastbackend.backendtasks
from recastbackend.catalogue import implemented_analyses
from recastbackend.backendtasks import run_analysis
from recastbackend.productionapp import app

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

  if backend == 'dedicated':
    if analysis_uuid not in implemented_analyses:
      raise NotImplementedError

    queuename = implemented_analyses[analysis_uuid]['queue']
    workflownamemodule = implemented_analyses[analysis_uuid]['workflow']
    ctx.update(
      entry_point   = '{}:recast'.format(workflownamemodule),
      results       = '{}:resultlist'.format(workflownamemodule)
    )

    return (queuename, ctx)

  if backend == 'rivet':
    rivetnameToUUID = pickle.loads(pkg_resources.resource_string('recastrivet','rivetmap.pickle'))
    UUIDtoRivet = {v:k for k,v in rivetnameToUUID.iteritems()}
    if analysis_uuid not in UUIDtoRivet:
      raise NotImplementedError

    ctx.update(
      entry_point   = 'recastrivet.backendtasks:recast',
      results       = 'recastrivet.backendtasks:resultlist',
      analysis      = analysis
    )

    return ('rivet_queue',ctx)


def production_celery_submit(request_uuid,parameter,backend):
  app.set_current()

  queue,ctx = get_queue_and_context(request_uuid,parameter,backend)
  
  result =  run_analysis.apply_async((recastbackend.backendtasks.setup,
                                      recastbackend.backendtasks.onsuccess,
                                      recastbackend.backendtasks.cleanup,ctx),
                                      queue = queue)
  return (ctx['jobguid'],result)

def submit_recast_request(request_uuid,parameter,backend):
  print 'submitting {}/{} on {}'.format(request_uuid,parameter,backend)

  return production_celery_submit(request_uuid,parameter,backend)
