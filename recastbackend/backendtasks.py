import zipfile
import os
import shutil
import subprocess
import importlib
import logging
import requests
import recastapi.request
from recastbackend.messaging import setupLogging

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
      log.info('result does not exist or is neither file nor folder!')
      raise RuntimeError

  return resultdir
  

def postresults(jobguid,requestId,parameter_point,resultlister,backend):
  log.info('packaging results')

  isolate_results(jobguid,resultlister)
  log.info('uploading results')

  BACKENDUSER = 'analysis'
  BACKENDHOST = 'recast-demo'
  BACKENDBASEPATH = '/home/analysis/recast/recaststorage'


  #also copy to server
  subprocess.call('''ssh {user}@{host} "mkdir -p {base}/results/{requestId}/{point} && rm -rf {base}/results/{requestId}/{point}/{backend}"'''.format(
    user = BACKENDUSER,
    host = BACKENDHOST,
    base = BACKENDBASEPATH,
    requestId = requestId,
    point = parameter_point,
    backend = backend
    )
  ,shell = True)
  subprocess.call(['scp', '-r', resultdir,'{user}@{host}:{base}/results/{requestId}/{point}/{backend}'.format(
    user = BACKENDUSER,
    host = BACKENDHOST,
    base = BACKENDBASEPATH,
    requestId = requestId,
    point = parameter_point,
    backend = backend
  )])

  #clean up
  shutil.rmtree(workdir)
  shutil.rmtree(resultdir)
  
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

    setupLogging(jobguid)

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