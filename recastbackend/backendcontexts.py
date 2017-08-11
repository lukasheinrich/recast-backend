import os

from recastapi.request.read import request_archive_for_request
from .resultaccess import basicreqpath
from .recastconfig import yadage_result_config

def common_context(input_url,outputdir,wflowconfigname):
    ctx = {
        'inputURL':input_url,
        'wflowconfigname':wflowconfigname,
        'shipout_spec': {
            'user': os.environ['RECAST_SHIP_USER'],
            'host': os.environ['RECAST_SHIP_HOST'],
            'port': os.environ['RECAST_SHIP_PORT'],
            'location': os.path.join(outputdir,wflowconfigname)
        }
    }
    return ctx

def common_contxt_for_recast(basicreqid,wflowconfigname):
    fileurl = request_archive_for_request(basicreqid,dry_run = True)
    outputdir = basicreqpath(basicreqid)
    return common_context(fileurl,outputdir,wflowconfigname)

def generic_yadage_outputs():
    return ['_adage','_yadage','**/*.log']

def yadage_context(common_context,workflow,toplevel = 'from-github/pseudocap', preset_pars = None, explicit_results = None):
    wflowkey = '{}:{}'.format(toplevel,workflow)
    ctx = common_context
    ctx.update(
        wflowtype = 'yadage',
        toplevel = toplevel,
        workflow = workflow,
        fixed_pars = preset_pars or {}
    )
    if not explicit_results:
        ctx['resultlist'] = generic_yadage_outputs() + yadage_result_config()[wflowkey]
    else:
        ctx['resultlist'] = explicit_results
    return ctx

def yadage_comboctx(common_context, comboconfig):
    ctx = common_context

    ctx.update(
        wflowtype = 'yadage',
        combinedspec = comboconfig
    )

    downstream_key = '{}:{}'.format(
        comboconfig['analysis']['toplevel'],
        comboconfig['analysis']['workflow']
    )

    downstream_results = yadage_result_config()[downstream_key]
    downstream_results = [os.path.join('downstream',x) for x in downstream_results]
    ctx['resultlist'] = generic_yadage_outputs() + downstream_results
    return ctx

def yadage_context_for_recast(basicreqid,wflowconfigname,wflowconfig):
    wflowconfig = wflowconfig['config']
    ctx = common_contxt_for_recast(basicreqid,wflowconfigname)
    ctx = yadage_context(ctx,wflowconfig['workflow'],wflowconfig['toplevel'],wflowconfig.get('preset_pars',{}))
    return ctx

def yadage_comboctx_for_recast(basicreqid,wflowconfigname,comboconfig):
    ctx = common_contxt_for_recast(basicreqid,wflowconfigname)
    ctx = yadage_comboctx(ctx,comboconfig['config'])
    return ctx
