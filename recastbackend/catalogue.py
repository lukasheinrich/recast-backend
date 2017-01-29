from recastconfig import backendconfig

def recastcatalogue():
    # for now we'll just reload the file each time later we might reference a database or public repo
    # that can receive pull requests

    # the goal is to return a list of configurations for analyes that come from the frontend
    # it will be indexed by the scan request ID

    # {
    #     '<analysisid>':{
    #         '<configA>':{}
    #         '<configB>':{}
    #     }
    # }

    bckcfg = backendconfig()


    #1. first get all the full stack workflows and index them by analysis
    configdata = {}
    for x in bckcfg['recast_wflowconfigs']:
        configdata.setdefault(x['analysisid'],{})[x['configname']] = {
            'wflowplugin': x['wflowplugin'],
            'config': x['config']
    }

    #2. second get all downstream workflows by analysis
    comboflowcfg = bckcfg['recast_combo_workflows']['yadage_combos']

    #sort upstreams by interface type
    upstream_by_iface = {}
    for upstream in comboflowcfg['upstream_configs']:
        upstream_by_iface.setdefault(upstream['analysis_interface'],[]).append(
            upstream
        )

    fromrequest = {
        'configname': 'requestwflow',
        'config': 'from-request'
    }

    for downstream in comboflowcfg['downstream_configs']:
        anid = downstream['analysisid']

        for possible_upstream in [fromrequest]+upstream_by_iface.get(downstream['required_interface'],[]):
            comboname = '{}/{}'.format(possible_upstream['configname'],downstream['configname'])
            config = {
                'adapter': possible_upstream['config'], 
                'analysis': downstream['config']
            }
            configdata.setdefault(anid,{})[comboname] = {
                'wflowplugin':'yadagecombo',
                'config': config
            }

    return configdata
