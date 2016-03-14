import uuid

def common_context(input_url,outputdir,backend):
    jobguid = str(uuid.uuid1())
    ctx = {
        'jobguid': jobguid,
        'inputURL':input_url,
        'shipout_base':outputdir,
        'backend':backend
    }
    return ctx

capresults = {
    'ewk_analyses/ewkdilepton_analysis/example_workflow.yml':['workflow.gif','results.yaml','out.yield'],
    'pheno_workflows/madgraph_delphes.yml':['workflow.gif','output.root','output.root'],
    'complex_analysis/fullworkflow.yml':['plots','fit.workspace.root']
}

def cap_context(common_context,workflow):
    ctx = common_context
    ctx.update(**{
        'entry_point':'recastcap.backendtasks:recast',
        'workflow':workflow,
        'resultlist':capresults[workflow]
    })
    return ctx
    
def rivet_context(common_context,analysis):
    ctx = common_context
    ctx.update(**{
        'entry_point':'recastrivet.backendtasks:recast',
        'results':'recastrivet.backendtasks:results',
        'analysis':analysis
    })
    return ctx


dedicated_plugins = {
  '858fb12c-b62f-9954-1997-a6ff8c27be0e':'recastdmhiggs.backendtasks',
  '3ad4efdb-0170-fb94-75a5-8a1279386745':'recasthype.backendtasks',
  '19c471ff-2514-eb44-0d82-59563cc38dab':'recastsusyhiggs.backendtasks',
  '09986001-6348-2fa4-59f8-f1d1b4a65776':'recastfullchain.backendtasks',
}
    
def dedicated_context(common_context,recast_analysis_id):
    raise NotImplementedError('need to implement dedicated context')

    

    