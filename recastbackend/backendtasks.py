import zipfile
import os
import shutil
import importlib
import logging
import requests
import glob2
import socket

from recastbackend.messaging import setupLogging

from fabric.api import env
from fabric.operations import run, put
from fabric.tasks import execute

from celery import shared_task

env.use_ssh_config = True

def generic_upload_results(resultdir,user,host,port,base,wflowconfigname):
    #make sure the directory for this point is present

    def fabric_command():
        run('mkdir -p {}'.format(base))
        run('(test -d {base}/{wflowconfigname} && rm -rf {base}/{wflowconfigname}) || echo "not present yet" '.format(base = base,wflowconfigname = wflowconfigname))
        run('mkdir {base}/{wflowconfigname}'.format(base = base, wflowconfigname = wflowconfigname))
        put('{}/*'.format(resultdir),'{base}/{wflowconfigname}'.format(base = base, wflowconfigname = wflowconfigname))

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
        globresult = glob2.glob(resultpath)
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

    jobguid = ctx['jobguid']
    wflowconfigname = ctx['wflowconfigname']
    shipout_base = ctx['shipout_base']

    log.info('success for job %s, gathering results... ',jobguid)

    resultdir = isolate_results(jobguid,getresultlist(ctx))

    log.info('uploading results to {}:{}'.format(os.environ['RECAST_SHIP_HOST'],shipout_base))
    generic_upload_results(resultdir,
                           os.environ['RECAST_SHIP_USER'],
                           os.environ['RECAST_SHIP_HOST'],
                           os.environ['RECAST_SHIP_PORT'],
                           shipout_base,
                           wflowconfigname)

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

def delete_all_but_log(directory, cutoff_size_MB = 50):
    """
    deletes all files in directory except *.log and *.txt which are
    assumed to be logfiles, except when they are too large,
    in which case they are shredded, too
    """
    bytes_per_megabyte = 1048576.0 #(2**20)

    for parent,directories,files in os.walk(directory):
        for fl in files:
            fullpath = '/'.join([parent,fl])
            islog = (fl.endswith('.log') or fl.endswith('.txt'))
            size_MB = os.stat(fullpath).st_size/bytes_per_megabyte
            if islog:
                if size_MB < cutoff_size_MB:
                    continue
                log.warning('size of log-like file %s is too large (%s MB), will be deleted',fullpath,size_MB)
            os.remove(fullpath)


def cleanup(ctx):
    workdir = 'workdirs/{}'.format(ctx['jobguid'])
    log.info('cleaning up workdir: %s',workdir)

    quarantine_base = os.environ.get('RECAST_QUARANTINE_DIR','/tmp/recast_quarantine')
    rescuedir = '{}/{}'.format(quarantine_base,ctx['jobguid'])
    log.info('log files will be in %s',rescuedir)
    try:
        if os.path.isdir(workdir):
            delete_all_but_log(workdir)
            shutil.move(workdir,rescuedir)
    except:
        #this is again pretty harsh, but we really want to make sure the workdir is gone
        if os.path.isdir(workdir):
            shutil.rmtree(workdir)
        log.exception('Error in cleanup function for jobid %s, the directory is gone.', ctx['jobguid'])
        raise RuntimeError('Error in cleanup, ')
    assert not os.path.isdir(workdir)

@shared_task
def run_analysis(setupfunc,onsuccess,teardownfunc,ctx):
    run_analysis_standalone(setupfunc,onsuccess,teardownfunc,ctx)

def run_analysis_standalone(setupfunc,onsuccess,teardownfunc,ctx,redislogging = True):
    try:
        jobguid = ctx['jobguid']

        if redislogging:
            logger, handler = setupLogging(jobguid)
        log.info('running analysis on worker: %s %s',socket.gethostname(),os.environ.get('RECAST_DOCKERHOST',''))

        setupfunc(ctx)
        try:
            pluginmodule,entrypoint = ctx['entry_point'].split(':')
            log.info('setting up entry point %s',ctx['entry_point'])
            m = importlib.import_module(pluginmodule)
            entry = getattr(m,entrypoint)
        except AttributeError:
            log.error('could not get entrypoint: %s',ctx['entry_point'])
            raise

        log.info('and off we go with job %s!',jobguid)
        entry(ctx)
        log.info('back from entry point run onsuccess')
        onsuccess(ctx)
    except:
        log.exception('something went wrong :(!')
        #re-raise exception
        raise
    finally:
        log.info('''it's a wrap for job %s! cleaning up.''',jobguid)
        teardownfunc(ctx)
        if redislogging:
            logger.removeHandler(handler)
