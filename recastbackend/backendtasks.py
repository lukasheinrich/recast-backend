from celery import shared_task
import celery
import zipfile
import os
import shutil
import recastapi.request
import json
import uuid
import importlib

from recastbackend.logging import socketlog  
import requests
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

@shared_task
def postresults(jobguid,requestId,parameter_point,resultlister):
  workdir = 'workdirs/{}'.format(jobguid)
  resultdir = 'results/{}/{}'.format(requestId,parameter_point)
  
  if(os.path.exists(resultdir)):
    shutil.rmtree(resultdir)
    
  os.makedirs(resultdir)  

  for result,resultpath in ((r,os.path.abspath('{}/{}'.format(workdir,r))) for r in resultlister()):
    if os.path.isfile(resultpath):
      shutil.copyfile(resultpath,'{}/{}'.format(resultdir,result))
    if os.path.isdir(resultpath):
      shutil.copytree(resultpath,'{}/{}'.format(resultdir,result))

  socketlog(jobguid,'uploading resuls')

  #also copy to server
  subprocess.call('''ssh {user}@{host} "mkdir -p {base}/results/{requestId}/{point} && rm -rf {base}/results/{requestId}/{point}/dedicated"'''.format(
    user = BACKENDUSER,
    host = BACKENDHOST,
    base = BACKENDBASEPATH,
    requestId = requestId,
    point = parameter_point)
  ,shell = True)
  subprocess.call(['scp', '-r', resultdir,'{user}@{host}:{base}/results/{requestId}/{point}/dedicated'.format(
    user = BACKENDUSER,
    host = BACKENDHOST,
    base = BACKENDBASEPATH,
    requestId = requestId,
    point = parameter_point
  )])
  
  socketlog(jobguid,'done')
  return requestId

    
@shared_task
def prepare_job(jobguid,jobinfo):
  print "job info is {}".format(jobinfo)
  print "job uuid is {}".format(jobguid)
  workdir = 'workdirs/{}'.format(jobguid)

  input_url = jobinfo['run-condition'][0]['lhe-file']
  socketlog(jobguid,'downloading input files')

  filepath = download_file(input_url,workdir)

  print "downloaded file to: {}".format(filepath)
  socketlog(jobguid,'downloaded input files')


  with zipfile.ZipFile(filepath)as f:
    f.extractall('{}/inputs'.format(workdir)) 
  
  return jobguid

@shared_task
def prepare_workdir(fileguid,jobguid):
  uploaddir = 'uploads/{}'.format(fileguid)
  workdir = 'workdirs/{}'.format(jobguid)
  
  os.makedirs(workdir)

  socketlog(jobguid,'prepared workdir')

  return jobguid