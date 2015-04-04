import importlib
import pickle
import pkg_resources

from recastbackend.catalogue import implemented_analyses

from recastbackend.productionapp import app

def get_chain_and_queue_and_results(analysis_uuid,backend):
  if not backend in ['dedicated','rivet']:
    raise NotImplementedError

  if backend == 'dedicated':
    if analysis_uuid not in implemented_analyses:
      raise NotImplementedError

    queuename = implemented_analyses[analysis_uuid]['queue']
    workflowmodulename = implemented_analyses[analysis_uuid]['workflow']
    module = importlib.import_module(workflowmodulename)
    chain = module.get_chain(queuename)
    return (queuename, chain, module.resultlist)

  if backend == 'rivet':
    queuename = 'rivet_queue'
    module = importlib.import_module('recastrivet.backendtasks')

    rivetnameToUUID = pickle.loads(pkg_resources.resource_string('recastrivet','rivetmap.pickle'))
    UUIDtoRivet = {v:k for k,v in rivetnameToUUID.iteritems()}
    if analysis_uuid not in UUIDtoRivet:
      raise NotImplementedError

    chain = module.get_chain(queuename,UUIDtoRivet[analysis_uuid])
    return (queuename, chain, module.resultlist)

def production_celery_submit(uuid,parameter,backend):
  pass

def submit_recast_request(uuid,parameter,backend):
  celery_app.set_current()
    
  print 'submitting {}/{} on {}'.format(uuid,parameter,backend)

  return production_celery_submit(uuid,parameter,backend)
