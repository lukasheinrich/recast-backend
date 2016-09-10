import yaml
import pkg_resources
backendconfig = yaml.load(pkg_resources.resource_stream('recastbackend','resources/backendconfig.yml'))

backends = [
    {
        'name':'capbackend',
        'analyses':backendconfig['capbackend_config']['recast_workflow_config']
    }
]

def getBackends(analysid_id):
    return [b['name'] for b in backends if analysid_id in [a['analysis_id'] for a in b['analyses']]]
