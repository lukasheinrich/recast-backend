import zipfile
import os
import shutil
import importlib
import logging
import requests
import recastapi.request
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

def prepare_job(jobguid,jobinfo):
  workdir = 'workdirs/{}'.format(jobguid)

  input_url = jobinfo['run-condition'][0]['lhe-file']
  log.info('downloading input files')

  filepath = download_file(input_url,workdir)

  log.info('downloaded done (at: {})'.format(filepath))

  with zipfile.ZipFile(filepath)as f:
    f.extractall('{}/inputs'.format(workdir)) 


def setup(ctx):
  jobguid = ctx['jobguid']
  request_uuid = ctx['requestguid']
  parameter_pt = ctx['parameter_pt']

  log.info('setting up for {requestguid}:{parameter_pt}:{backend}'.format(**ctx))

  request_info = recastapi.request.request(request_uuid)
  jobinfo = request_info['parameter-points'][parameter_pt]

  prepare_workdir(request_uuid,jobguid)
  prepare_job(jobguid,jobinfo)

def prepare_workdir(fileguid,jobguid):
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
    if os.path.isfile(resultpath):
      shutil.copyfile(resultpath,'{}/{}'.format(resultdir,result))
    elif os.path.isdir(resultpath):
      shutil.copytree(resultpath,'{}/{}'.format(resultdir,result))
    else:
      log.error('result does not exist or is neither file nor folder!')
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
    onsuccess(ctx)
  except:
    log.error('something went wrong :(!')
    raise
  finally:
    log.info('''it's a wrap! cleaning up.''')
    teardownfunc(ctx)
    logger.removeHandler(handler)
    
