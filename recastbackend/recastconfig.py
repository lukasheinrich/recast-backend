import pkg_resources
import os
import yaml
import urllib2

def backendconfig():
	url = os.environ.get('RECAST_BACKENDCONFIGURL',None)
	if not url:
		defaultconfigfile = pkg_resources.resource_filename('recastbackend','resources/backendconfig.yml')
		configfile = os.environ.get('RECAST_BACKENDCONFIGFILE',defaultconfigfile)
		url = 'file://'+os.path.realpath(configfile)
	configdata = yaml.load(urllib2.urlopen(url))
	return configdata

def yadage_result_config():
    yadagepluginconf = backendconfig()['plugin_configs']['yadageworkflow']
    return {x['workflow']:x['results'] for x in yadagepluginconf['results']}

def yadage_adapter_config():
    yadagepluginconf = backendconfig()['plugin_configs']['yadageworkflow']
    return {x['workflow']:x['recastresult'] for x in yadagepluginconf['results']}
