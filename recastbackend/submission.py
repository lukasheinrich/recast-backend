import logging
import recastbackend.backendtasks
import backendcontexts
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
                                                     queue = queue,
                                                     countdown = 3)

    messaging.socketlog(ctx['jobguid'],'registered. processed by celery id: {}'.format(result.id))
    map_job_to_celery(ctx['jobguid'],result.id)
    return result

def submit_recast_request(basicreqid,analysisid,backend):
    log.info('submitting recast request for basic request #%s via analysis: %s backend %s ',basicreqid,analysisid,backend)
    ctx = None
    if backend == 'capbackend':
        ctx = backendcontexts.cap_context_for_recast(basicreqid,analysisid)
        log.info('submitting context %s',ctx)
        result = submit_celery(ctx,'recast_cap_queue')
        register_job(basicreqid,backend,ctx['jobguid'])
        return ctx['jobguid'],result.id
    else:
        raise RuntimeError('do not know how to construct context for backend: %s',backend)
