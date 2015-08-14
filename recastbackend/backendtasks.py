import zipfile
import os
import shutil
import importlib
import logging
import requests
import recastapi.request
import glob
from recastbackend.messaging import setupLogging

from fabric.api import env
from fabric.operations import run, put
from fabric.tasks import execute

env.use_ssh_config = True

def upload_results(resultdir,requestId,point,backend):
  #make sure the directory for this point is present
  
  def fabric_command():
    base = '/home/analysis/recast/recaststorage/results/{requestId}/{point}'.format(requestId = requestId, point = point)
    run('mkdir -p {}'.format(base))
    run('(test -d {base}/{backend} && rm -rf {base}/{backend}) || echo "not present yet" '.format(base = base,backend = backend))
    run('mkdir {base}/{backend}'.format(base = base, backend = backend))
    put('{}/*'.format(resultdir),'{base}/{backend}'.format(base = base, backend = backend))
  
  execute(fabric_command,hosts = 'analysis@recast-demo')

def generic_upload_results(resultdir,user,host,port,base,backend):
  #make sure the directory for this point is present

  def fabric_command():
    run('mkdir -p {}'.format(base))
    run('(test -d {base}/{backend} && rm -rf {base}/{backend}) || echo "not present yet" '.format(base = base,backend = backend))
    run('mkdir {base}/{backend}'.format(base = base, backend = backend))
    put('{}/*'.format(resultdir),'{base}/{backend}'.format(base = base, backend = backend))

  execute(fabric_command,hosts = '{user}@{host}:{port}'.format(user = user,host = host,port = port))


from celery import shared_task

log = logging.getLogger('RECAST')

def download_file(url,download_dir):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    download_path = '{}/{}'.format(download_dir,local_filename)
    with open(download_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return download_path    


def prepare_job_fromURL(jobguid,input_url):
  workdir = 'workdirs/{}'.format(jobguid)

  filepath = download_file(input_url,workdir)

  log.info('downloaded done (at: {})'.format(filepath))

  with zipfile.ZipFile(filepath)as f:
    f.extractall('{}/inputs'.format(workdir))

def prepare_job(jobguid,jobinfo):
  input_url = jobinfo['run-condition'][0]['lhe-file']
  prepare_job_fromURL(jobguid,input_url)

def setup(ctx):
  jobguid = ctx['jobguid']
  request_uuid = ctx['requestguid']
  parameter_pt = ctx['parameter_pt']

  log.info('setting up for {requestguid}:{parameter_pt}:{backend}'.format(**ctx))

  request_info = recastapi.request.request(request_uuid)
  jobinfo = request_info['parameter-points'][parameter_pt]

  prepare_workdir(jobguid)
  prepare_job(jobguid,jobinfo)

def setupFromURL(ctx):
  jobguid = ctx['jobguid']

  log.info('setting up for context {}'.format(ctx))

  prepare_workdir(jobguid)
  prepare_job_fromURL(jobguid,ctx['inputURL'])


def prepare_workdir(jobguid):
  workdir = 'workdirs/{}'.format(jobguid)
  os.makedirs(workdir)
  log.info('prepared workdir')

def isolate_results(jobguid,resultlister):
  workdir = 'workdirs/{}'.format(jobguid)
  resultdir = '{}/results'.format(workdir)
  
  if(os.path.exists(resultdir)):
    shutil.rmtree(resultdir)
    
  os.makedirs(resultdir)  

  for result,resultpath in ((r,os.path.abspath('{}/{}'.format(workdir,r))) for r in resultlister()):
    globresult = glob.glob(resultpath)
    if not globresult:
      log.warning('no matches for glob {}'.format(resultpath))
    for thing in globresult:
      if os.path.isfile(thing):
        shutil.copyfile(thing,'{}/{}'.format(resultdir,os.path.basename(thing)))
      elif os.path.isdir(thing):
        shutil.copytree(thing,'{}/{}'.format(resultdir,os.path.basename(thing)))
      else:
        log.error('result {} (path: {}, glob element: {})  does not exist or is neither file nor folder!'.format(result,resultpath,thing))
        raise RuntimeError

  return resultdir
  

def onsuccess(ctx):
  log.info('success!')

  jobguid = ctx['jobguid']
  resultlistname = ctx['results']
  backend = ctx['backend']
  requestId = ctx['requestguid']
  parameter_point = ctx['parameter_pt']

  modulename,attr = resultlistname.split(':')
  module = importlib.import_module(modulename)
  resultlister = getattr(module,attr)
  
  resultdir = isolate_results(jobguid,resultlister)
  log.info('uploading results')

  upload_results(resultdir,requestId,parameter_point,backend)

  log.info('done')
  return requestId

def generic_onsuccess(ctx):
  log.info('success!')

  jobguid = ctx['jobguid']
  resultlistname = ctx['results']
  backend = ctx['backend']

  modulename,attr = resultlistname.split(':')
  module = importlib.import_module(modulename)
  resultlister = getattr(module,attr)

  resultdir = isolate_results(jobguid,resultlister)
  log.info('uploading results')


  shipout_base = ctx['shipout_base']

  generic_upload_results(resultdir,os.environ['RECAST_SHIP_USER'],os.environ['RECAST_SHIP_HOST'],os.environ['RECAST_SHIP_PORT'],shipout_base,backend)

  log.info('done with uploading results')


def cleanup(ctx):
  workdir = 'workdirs/{}'.format(ctx['jobguid'])
  
  log.info('cleaning up workdir: {}'.format(workdir))
  
  if os.path.isdir(workdir):
    shutil.rmtree(workdir)

@shared_task
def run_analysis(setupfunc,onsuccess,teardownfunc,ctx):
  try:
    jobguid = ctx['jobguid']

    logger, handler = setupLogging(jobguid)

    setupfunc(ctx)
    try:
      pluginmodule,entrypoint = ctx['entry_point'].split(':')
      m = importlib.import_module(pluginmodule)
      entry = getattr(m,entrypoint)
    except AttributeError:
      log.error('could not get entrypoint: {}'.format(ctx['entry_point']))
      raise
      
    log.info('and off we go!')
    entry(ctx)
    log.info('back from entry point run onsuccess')
    onsuccess(ctx)
  except:
    log.error('something went wrong :(!')
    raise
  finally:
    log.info('''it's a wrap! cleaning up.''')
    teardownfunc(ctx)
    logger.removeHandler(handler)
    
