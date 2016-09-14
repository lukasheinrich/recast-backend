from recastbackend.recastconfig import yadage_adapter_config
import importlib

import catalogue

def extract_result(resultdir,analysisid,wflowconfigname):
    wflowconfig = catalogue.recastcatalogue()[int(analysisid)][wflowconfigname]
    if wflowconfig['wflowplugin'] == 'yadageworkflow':
        return extract_yadageworkflow_result(resultdir,wflowconfig['config'])
    raise RuntimeError

def extract_yadageworkflow_result(resultdir,wflowconfig):
    wflowkey = '{}:{}'.format(wflowconfig['toplevel'],wflowconfig['workflow'])
    aconf = yadage_adapter_config()[wflowkey]
    modulename,attr = aconf.pop('adapter').split(':')
    module = importlib.import_module(modulename)
    adapter = getattr(module,attr)
    return adapter(resultdir,**aconf)
