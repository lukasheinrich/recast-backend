import uuid
import recastbackend.resultaccess
import recastapi.request.read
from recastbackend.recastconfig import yadage_result_config
#, yadage_workflow_config

def common_context(input_url,outputdir,wflowconfigname):
    jobguid = str(uuid.uuid1())
    ctx = {
        'jobguid': jobguid,
        'inputURL':input_url,
        'shipout_base':outputdir,
        'wflowconfigname':wflowconfigname
    }
    return ctx

def generic_yadage_outputs():
    return ['_adage','_yadage']

def yadage_context(common_context,workflow,toplevel = 'from-github/pseudocap', preset_pars = {}):
    wflowkey = '{}:{}'.format(toplevel,workflow)
    ctx = common_context
    ctx.update(**{
        'entry_point':'recastcap.backendtasks:recast',
        'toplevel':toplevel,
        'workflow':workflow,
        'resultlist':generic_yadage_outputs() + yadage_result_config()[wflowkey],
        'fixed_pars':preset_pars
    })
    return ctx

def yadage_context_for_recast(basicreqid,wflowconfigname,wflowconfig):
    fileurl = recastapi.request.read.request_archive_for_request(basicreqid,dry_run = True)
    outputdir = recastbackend.resultaccess.basicreqpath(basicreqid)
    ctx = common_context(fileurl,outputdir,wflowconfigname)
    wflowconfig = wflowconfig['config']
    ctx = yadage_context(ctx,wflowconfig['workflow'],wflowconfig['toplevel'],wflowconfig.get('preset_pars',{}))
    return ctx
