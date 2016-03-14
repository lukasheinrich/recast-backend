import logging
import recastbackend.backendtasks
import messaging
from fromenvapp import app
from jobstate import map_job_to_celery

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
    
def submit_recast_request(request_uuid,parameter,backend):
    raise NotImplementedError('we are changing things right now. The implementation will be back soon')

