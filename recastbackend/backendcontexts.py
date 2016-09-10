import uuid
import recastbackend.resultaccess
import recastapi.request.read
from recastbackend.recastconfig import cap_result_config, cap_workflow_config

def common_context(input_url,outputdir,backend):
    jobguid = str(uuid.uuid1())
    ctx = {
        'jobguid': jobguid,
        'inputURL':input_url,
        'shipout_base':outputdir,
        'backend':backend
    }
    return ctx

def generic_yadage_outputs():
    return ['_adage','_yadage']

def cap_context(common_context,workflow,toplevel = 'from-github/pseudocap', preset_pars = {}):
    wflowkey = '{}:{}'.format(toplevel,workflow)
    ctx = common_context
    ctx.update(**{
        'entry_point':'recastcap.backendtasks:recast',
        'toplevel':toplevel,
        'workflow':workflow,
        'resultlist':cap_result_config[wflowkey]+generic_yadage_outputs(),
        'fixed_pars':preset_pars
    })
    return ctx

def cap_context_for_recast(basicreqid,analysisid):
    fileurl = recastapi.request.read.request_archive_for_request(basicreqid,dry_run = True)
    outputdir = recastbackend.resultaccess.basicreqpath(basicreqid)
    ctx = common_context(fileurl,outputdir,'capbackend')
    wflowconfig = cap_workflow_config[analysisid]
    ctx = cap_context(ctx,wflowconfig['workflow'],wflowconfig['toplevel'],wflowconfig.get('preset_pars',{}))
    return ctx
