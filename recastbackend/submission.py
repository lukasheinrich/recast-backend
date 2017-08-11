import logging

import backendcontexts
import wflowapi
import jobdb 
from catalogue import recastcatalogue

log = logging.getLogger(__name__)

def submit_workflow(ctx, queue):
    ctx['queue'] = queue
    processing_id = wflowapi.workflow_submit(ctx)
    jobdb.register_bare_job(processing_id)
    return processing_id

def submit_recast_request(basicreqid,analysisid,wflowconfigname):
    log.info('submitting recast request for basic request #%s part of analysisid: %s wflowconfig %s ',basicreqid,analysisid,wflowconfigname)
    ctx = None

    allconfigs = recastcatalogue()
    thisconfig = allconfigs[int(analysisid)][wflowconfigname]
    if thisconfig['wflowplugin'] == 'yadageworkflow':
        ctx = backendcontexts.yadage_context_for_recast(basicreqid,wflowconfigname,thisconfig)
        log.info('submitting context %s',ctx)
        processing_id = submit_workflow(ctx,'yadage_queue')
        jobdb.register_job(basicreqid,wflowconfigname,processing_id)
        return processing_id
    elif thisconfig['wflowplugin'] == 'yadagecombo':
        ctx = backendcontexts.yadage_comboctx_for_recast(basicreqid,wflowconfigname,thisconfig)
        log.info('submitting context %s',ctx)
        processing_id = submit_workflow(ctx,'yadage_queue')
        jobdb.register_job(basicreqid,wflowconfigname,processing_id)
        return processing_id
    else:
        raise RuntimeError('do not know how to construct context for plugin: %s',thisconfig['wflowplugin'])

