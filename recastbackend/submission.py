import logging
import os
import json
import backendcontexts
import requests
from catalogue import recastcatalogue

from recastcelery.messaging import socketlog
from recastbackend.jobstate import map_job_to_celery,register_job

logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)

def submit_workflow(ctx, queue):
    ctx['queue'] = queue
    log.info('submitting to workflow server: %s',ctx)
    resp = requests.post(os.environ['RECAST_WORKFLOW_SERVER']+'/workflow_submit',
                         data = json.dumps(ctx), headers = {'content-type': 'application/json'})
    celery_id = resp.json()['id']
    map_job_to_celery(ctx['jobguid'],celery_id)
    socketlog(ctx['jobguid'],'workflow registered. processed by celery id: {}'.format(celery_id))

# def submit_celery(ctx,queue):
#     app.set_current()
#     result = recastcelery.backendtasks.run_analysis.apply_async((
#                                                      recastcelery.backendtasks.setupFromURL,
#                                                      recastcelery.backendtasks.generic_onsuccess,
#                                                      recastcelery.backendtasks.cleanup,ctx),
#                                                      queue = queue,)

#     socketlog(ctx['jobguid'],'registered. processed by celery id: {}'.format(result.id))
#     map_job_to_celery(ctx['jobguid'],result.id)
#     return result

def submit_recast_request(basicreqid,analysisid,wflowconfigname):
    log.info('submitting recast request for basic request #%s part of analysisid: %s wflowconfig %s ',basicreqid,analysisid,wflowconfigname)
    ctx = None

    allconfigs = recastcatalogue()
    thisconfig = allconfigs[int(analysisid)][wflowconfigname]
    if thisconfig['wflowplugin'] == 'yadageworkflow':
        ctx = backendcontexts.yadage_context_for_recast(basicreqid,wflowconfigname,thisconfig)
        log.info('submitting context %s',ctx)
        result = submit_workflow(ctx,'recast_yadage_queue')
        register_job(basicreqid,wflowconfigname,ctx['jobguid'])
        return ctx['jobguid'],result.id
    elif thisconfig['wflowplugin'] == 'yadagecombo':
        ctx = backendcontexts.yadage_comboctx_for_recast(basicreqid,wflowconfigname,thisconfig)
        log.info('submitting context %s',ctx)
        result = submit_workflow(ctx,'recast_yadage_queue')
        register_job(basicreqid,wflowconfigname,ctx['jobguid'])
        return ctx['jobguid'],result.id
    else:
        raise RuntimeError('do not know how to construct context for plugin: %s',thisconfig['wflowplugin'])

def yadage_submission(input_url,outputdir,configname,outputs,workflow,toplevel,presetpars,queue):
    ctx = backendcontexts.common_context(input_url,outputdir,configname)
    ctx = backendcontexts.yadage_context(
        ctx,workflow,
        toplevel,
        presetpars,
        explicit_results = backendcontexts.generic_yadage_outputs() + outputs
    )
    log.info('submitting context %s',ctx)
    return ctx, submit_workflow(ctx,queue)
