import os
import importlib

from .recastconfig import yadage_adapter_config
from .catalogue import recastcatalogue

def extract_result(resultdir,analysisid,wflowconfigname):
    wflowconfig = recastcatalogue()[int(analysisid)][wflowconfigname]
    if wflowconfig['wflowplugin'] == 'yadageworkflow':
        return extract_yadageworkflow_result(resultdir,wflowconfig['config'])
    if wflowconfig['wflowplugin'] == 'yadagecombo':
        return extract_yadagecombo_result(resultdir,wflowconfig['config'])
    raise RuntimeError

def extract_yadageworkflow_result(resultdir,wflowconfig):
    wflowkey = '{}:{}'.format(wflowconfig['toplevel'],wflowconfig['workflow'])
    aconf = yadage_adapter_config()[wflowkey]
    modulename,attr = aconf.pop('adapter').split(':')
    module = importlib.import_module(modulename)
    adapter = getattr(module,attr)
    return adapter(resultdir,**aconf)

def extract_yadagecombo_result(resultdir,wflowconfig):
    downstreamkey = '{}:{}'.format(wflowconfig['analysis']['toplevel'],wflowconfig['analysis']['workflow'])
    resultdir = os.path.join(resultdir,'downstream')
    aconf = yadage_adapter_config()[downstreamkey]
    modulename,attr = aconf.pop('adapter').split(':')
    module = importlib.import_module(modulename)
    adapter = getattr(module,attr)
    return adapter(resultdir,**aconf)
