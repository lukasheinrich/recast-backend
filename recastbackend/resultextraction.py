from recastbackend.recastconfig import yadage_adapter_config
import importlib

import catalogue

def extract_result(resultdir,scanreqid,wflowconfigname):
    wflowconfig = catalogue.recastcatalogue()[int(scanreqid)][wflowconfigname]
    if wflowconfig['wflowplugin'] == 'yadageworkflow':
        return extract_yadageworkflow_result(resultdir,wflowconfig['config'])
    raise RuntimeError

def extract_yadageworkflow_result(resultdir,wflowconfig):
    print 'extracting results for {} {}'.format(resultdir,wflowconfig)
    wflowkey = '{}:{}'.format(wflowconfig['toplevel'],wflowconfig['workflow'])

    print 'key',wflowkey

    aconf = yadage_adapter_config()[wflowkey]
    print 'adapter config is: {}'.format(aconf)

    modulename,attr = aconf.pop('adapter').split(':')
    module = importlib.import_module(modulename)
    adapter = getattr(module,attr)
    print 'calling {} with {}'.format(resultdir,aconf)
    return adapter(resultdir,**aconf)
