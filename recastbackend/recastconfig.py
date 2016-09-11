import pkg_resources
import os
import yaml

def backendconfig():
    defaultconfigfile = pkg_resources.resource_filename('recastbackend','resources/backendconfig.yml')
    configfile = os.environ.get('RECAST_BACKENDCONFIGFILE',defaultconfigfile)
    configdata = yaml.load(open(configfile))
    return configdata

def yadage_result_config():
    yadagepluginconf = backendconfig()['plugin_configs']['yadageworkflow']
    return {x['workflow']:x['results'] for x in yadagepluginconf['results']}

def yadage_adapter_config():
    yadagepluginconf = backendconfig()['plugin_configs']['yadageworkflow']
    return {x['workflow']:x['recastresult'] for x in yadagepluginconf['results']}
