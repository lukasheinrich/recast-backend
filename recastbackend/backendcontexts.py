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
    'pheno_workflows/madgraph_delphes.yml':['workflow.gif','output.root','output.root']
}

def add_cap_context(ctx,workflow):
    ctx.update(**{
        'entry_point':'recastcap.backendtasks:recast',
        'workflow':workflow,
        'resultlist':capresults[workflow]
    })
    return ctx