from recastbackend.recastconfig import cap_workflow_config, cap_adapter_config
import importlib
def extract_result(resultdir,analysis_id,backend):
    if backend == 'capbackend':
        return extract_capbackend_result(resultdir,analysis_id)
    raise RuntimeError

def extract_capbackend_result(resultdir,analysis_id):
    print 'extracting results for {} {}'.format(resultdir,analysis_id)
    workflow_config = cap_workflow_config[analysis_id]
    configkey = ':'.join([workflow_config['toplevel'],workflow_config['workflow']])


    aconf = cap_adapter_config[configkey].copy()
    print 'adapter config is: {}'.format(aconf)

    modulename,attr = aconf.pop('adapter').split(':')
    module = importlib.import_module(modulename)
    adapter = getattr(module,attr)
    print 'calling {} with {}'.format(resultdir,aconf)
    return adapter(resultdir,**aconf)
