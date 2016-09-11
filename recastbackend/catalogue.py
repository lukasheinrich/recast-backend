import yaml
import pkg_resources
from recastconfig import backendconfig

def recastcatalogue():
    # for now we'll just reload the file each time later we might reference a database or public repo
    # that can receive pull requests

    # the goal is to return a list of configurations for scan requests that come from the frontend
    # it will be indexed by the scan request ID

    # {
    #     '<scanreq>':{
    #         '<configA>':{}
    #         '<configB>':{}
    #     }
    # }
    configdata = {}
    for x in backendconfig()['recast_wflowconfigs']:
        configdata.setdefault(x['scanid'],{}).setdefault(x['configname'],{
            'wflowplugin': x['wflowplugin'],
            'config': x['config']
        })
    return configdata
