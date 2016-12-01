import logging
import recastbackend.backendtasks
import backendcontexts
from catalogue import recastcatalogue
import messaging
from fromenvapp import app
from jobstate import map_job_to_celery,register_job

logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)

def submit_celery(ctx,queue):
    app.set_current()
    result = recastbackend.backendtasks.run_analysis.apply_async((
                                                     recastbackend.backendtasks.setupFromURL,
                                                     recastbackend.backendtasks.generic_onsuccess,
                                                     recastbackend.backendtasks.cleanup,ctx),
                                                     queue = queue,)
#                                                     countdown = 3)

    messaging.socketlog(ctx['jobguid'],'registered. processed by celery id: {}'.format(result.id))
    map_job_to_celery(ctx['jobguid'],result.id)
    return result

def submit_recast_request(basicreqid,analysisid,wflowconfigname):
    log.info('submitting recast request for basic request #%s part of analysisid: %s wflowconfig %s ',basicreqid,analysisid,wflowconfigname)
    ctx = None

    allconfigs = recastcatalogue()
    thisconfig = allconfigs[int(analysisid)][wflowconfigname]
    print 'doing nothing flow now....',thisconfig
    if thisconfig['wflowplugin'] == 'yadageworkflow':
        print 'ok we can run this via the yadage workers... '
        ctx = backendcontexts.yadage_context_for_recast(basicreqid,wflowconfigname,thisconfig)
        log.info('submitting context %s',ctx)
        result = submit_celery(ctx,'recast_cap_queue')
        register_job(basicreqid,wflowconfigname,ctx['jobguid'])
        return ctx['jobguid'],result.id
    else:
        raise RuntimeError('do not know how to construct context for plugin: %s',thisconfig['wflowplugin'])
