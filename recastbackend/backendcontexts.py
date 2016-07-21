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

def generic_outputs():
    return ['_adage','_yadage']

capresults = {
    'from-github/pseudocap:ewk_analyses/ewkdilepton_analysis/ewk_dilepton_recast_workflow.yml':
        generic_outputs() + ['histfitprepare/out.yield','histfitprepare/out.root','fit/fit.tgz','postproc/results.yml'],
    'from-github/phenochain:madgraph_delphes.yml':
        generic_outputs() + ['pythia/output.hepmc','delphes/output.lhco','delphes/output.root'],
    'from-github/higgmcproduction:rootflow-combined.yml':
        generic_outputs() + ['rootmerge/anamerged.root'],
}

def cap_context(common_context,workflow,toplevel = 'from-github/pseudocap'):
    wflowkey = '{}:{}'.format(toplevel,workflow)
    ctx = common_context
    ctx.update(**{
        'entry_point':'recastcap.backendtasks:recast',
        'toplevel':toplevel,
        'workflow':workflow,
        'resultlist':capresults[wflowkey]
    })
    return ctx
