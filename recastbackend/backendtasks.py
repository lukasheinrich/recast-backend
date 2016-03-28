import zipfile
import os
import shutil
import importlib
import logging
import requests
import glob
import socket

from recastbackend.messaging import setupLogging

from fabric.api import env
from fabric.operations import run, put
from fabric.tasks import execute

from celery import shared_task

env.use_ssh_config = True

def generic_upload_results(resultdir,user,host,port,base,backend):
    #make sure the directory for this point is present
    
    def fabric_command():
        run('mkdir -p {}'.format(base))
        run('(test -d {base}/{backend} && rm -rf {base}/{backend}) || echo "not present yet" '.format(base = base,backend = backend))
        run('mkdir {base}/{backend}'.format(base = base, backend = backend))
        put('{}/*'.format(resultdir),'{base}/{backend}'.format(base = base, backend = backend))
    
    execute(fabric_command,hosts = '{user}@{host}:{port}'.format(user = user,host = host,port = port))



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
    log.info('downloaded done (at: %s)',filepath)
    
    with zipfile.ZipFile(filepath)as f:
        f.extractall('{}/inputs'.format(workdir))

def setupFromURL(ctx):
    jobguid = ctx['jobguid']
    
    log.info('setting up for context %s',ctx)
    
    prepare_workdir(jobguid)
    prepare_job_fromURL(jobguid,ctx['inputURL'])


def prepare_workdir(jobguid):
    workdir = 'workdirs/{}'.format(jobguid)
    os.makedirs(workdir)
    log.info('prepared workdir %s',workdir)

def isolate_results(jobguid,resultlist):
    workdir = 'workdirs/{}'.format(jobguid)
    resultdir = '{}/results'.format(workdir)
    
    if(os.path.exists(resultdir)):
        shutil.rmtree(resultdir)
        
    os.makedirs(resultdir)  
    
    for result,resultpath in ((r,os.path.abspath('{}/{}'.format(workdir,r))) for r in resultlist):
        globresult = glob.glob(resultpath)
        if not globresult:
            log.warning('no matches for glob %s',resultpath)
        for thing in globresult:
            if os.path.isfile(thing):
                shutil.copyfile(thing,'{}/{}'.format(resultdir,os.path.basename(thing)))
            elif os.path.isdir(thing):
                shutil.copytree(thing,'{}/{}'.format(resultdir,os.path.basename(thing)))
            else:
                log.error('result %s (path: %s, glob element: %s)  does not exist or is neither file nor folder!',
                          result,resultpath,thing)
                raise RuntimeError
    return resultdir
  

def getresultlist(ctx):
    """
    result list can either be provided as module:attricbut nullary function
    under the key 'results' or as an actual list of strings under key 'resultlist'  
    """
    if 'results' in ctx:
        resultlistname = ctx['results']
        modulename,attr = resultlistname.split(':')
        module = importlib.import_module(modulename)
        resultlister = getattr(module,attr)    
        return resultlister()
    if 'resultlist' in ctx:
        return ctx['resultlist']
  

def generic_onsuccess(ctx):
    log.info('success!')
    
    jobguid       = ctx['jobguid']
    backend       = ctx['backend']
    shipout_base  = ctx['shipout_base']
    
    resultdir = isolate_results(jobguid,getresultlist(ctx))
    
    log.info('uploading results')
    generic_upload_results(resultdir,
                           os.environ['RECAST_SHIP_USER'],
                           os.environ['RECAST_SHIP_HOST'],
                           os.environ['RECAST_SHIP_PORT'],
                           shipout_base,
                           backend)
    
    log.info('done with uploading results')

def dummy_onsuccess(ctx):
    log.info('success!')
    
    jobguid       = ctx['jobguid']
    
    resultdir = isolate_results(jobguid,getresultlist(ctx))
    
    log.info('would be uploading results here..')
    
    for parent,dirs,files in os.walk(resultdir):
        for f in files:
            log.info('would be uploading this file %s','/'.join([parent,f]))
    
    log.info('done with uploading results')

def cleanup(ctx):
    workdir = 'workdirs/{}'.format(ctx['jobguid'])
    log.info('cleaning up workdir: %s',workdir)
   
    if os.path.isdir(workdir):
        #shutil.rmtree(workdir)
        rescuedir = '/tmp/recast_quarantine/{}'.format(ctx['jobguid'])
        shutil.move(workdir,rescuedir)
        assert not os.path.isdir(workdir)
        for p,d,f in os.walk(rescuedir):
            for fl in f:
                if not (fl.endswith('.log') or fl.endswith('.txt')):
                    os.remove('/'.join([p,fl]))


@shared_task
def run_analysis(setupfunc,onsuccess,teardownfunc,ctx):
    run_analysis_standalone(setupfunc,onsuccess,teardownfunc,ctx)

def run_analysis_standalone(setupfunc,onsuccess,teardownfunc,ctx,redislogging = True):
    try:
        jobguid = ctx['jobguid']
        
        if redislogging:
            logger, handler = setupLogging(jobguid)
        log.info('running analysis on worker: %s',socket.gethostname())
                
        setupfunc(ctx)
        try:
            pluginmodule,entrypoint = ctx['entry_point'].split(':')
            log.info('setting up entry point %s',ctx['entry_point'])
            m = importlib.import_module(pluginmodule)
            entry = getattr(m,entrypoint)
        except AttributeError:
            log.error('could not get entrypoint: %s',ctx['entry_point'])
            raise
          
        log.info('and off we go!')
        entry(ctx)
        log.info('back from entry point run onsuccess')
        onsuccess(ctx)
    except:
        log.exception('something went wrong :(!')
        #re-raise exception
        raise
    finally:
        log.info('''it's a wrap! cleaning up.''')
        teardownfunc(ctx)
        if redislogging:
            logger.removeHandler(handler)
    
