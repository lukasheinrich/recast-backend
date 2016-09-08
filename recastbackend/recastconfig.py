import pkg_resources
import os
import yaml
defaultconfigfile = pkg_resources.resource_filename('recastbackend','resources/backendconfig.yml')
configfile = os.environ.get('RECAST_BACKENDCONFIGFILE',defaultconfigfile)
configdata = yaml.load(open(configfile))


cap_result_config   = {x['workflow']:x['results'] for x in configdata['capbackend_config']['results']}
cap_adapter_config   = {x['workflow']:x['recastresult'] for x in configdata['capbackend_config']['results']}
cap_workflow_config = {x['analysis_id']:x for x in configdata['capbackend_config']['recast_workflow_config']}
