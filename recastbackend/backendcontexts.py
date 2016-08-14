import uuid
import pkg_resources
import recastbackend.resultaccess

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


import yaml
configdata = yaml.load(open(pkg_resources.resource_filename('recastbackend','resources/backendconfig.yml')))
cap_result_config   = {x['workflow']:x['results'] for x in configdata['capbackend_config']['results']}
cap_workflow_config = {x['analysis_id']:x for x in configdata['capbackend_config']['recast_workflow_config']}

def cap_context(common_context,workflow,toplevel = 'from-github/pseudocap'):
    wflowkey = '{}:{}'.format(toplevel,workflow)
    ctx = common_context
    ctx.update(**{
        'entry_point':'recastcap.backendtasks:recast',
        'toplevel':toplevel,
        'workflow':workflow,
        'resultlist':cap_result_config[wflowkey]+generic_yadage_outputs()
    })
    return ctx

import recastapi.request.get


def cap_context_for_recast(basicreqid,analysisid):
    fileurl = recastapi.request.get.download_file(basicreqid,dry_run=True)['file_link']
    outputdir = recastbackend.resultaccess.basicreqpath(basicreqid)
    ctx = common_context(fileurl,outputdir,'capbackend')
    wflowconfig = cap_workflow_config[analysisid]
    ctx = cap_context(ctx,wflowconfig['workflow'],wflowconfig['toplevel'])
    return ctx
