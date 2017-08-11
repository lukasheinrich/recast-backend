import json
import pkg_resources
import copy
import os
from .recastconfig import backendconfig

import recastapi.analysis.read
def checkmate_catalogue():
    template = {
        'analysisid': None,
        'configname': 'checkmate',
        'required_interface': 'hepmc_with_xsec',
        'config': {
            'toplevel': 'from-github/phenochain/checkmate_workflow',
            'workflow': 'analysis_flow.yml',
            'preset_pars':{
                'analysis': None
            }
        }
    }
    pub2recast = json.load(open(pkg_resources.resource_filename(
                        'recastbackend',
                        'resources/pub_to_recast.json')
                ))
    pub2checkmate  = json.load(open(pkg_resources.resource_filename(
                        'recastbackend','resources/pub_to_checkmate.json')
                ))

    checkmate_downstreams = []
    for pubkey,checkmate_analysis in pub2checkmate.iteritems():
        specific = copy.deepcopy(template)
        specific['pubkey'] = pubkey
        specific['config']['preset_pars'] = {'analysis': checkmate_analysis}
        checkmate_downstreams.append(specific)
    return checkmate_downstreams

def rivet_catalogue():
    ''''this will spit out combo configs for all rivet analyses'''
    template = {
        'analysisid': None,
        'configname': 'rivetanalysis',
        'required_interface': 'hepmcfiles',
        'config': {
            'toplevel': 'from-github/phenoana/generic_rivet',
            'workflow': 'rivetanflow.yml',
            'preset_pars':{
                'analysis': None
            }
        }
    }

    in2rivet  = json.load(open(pkg_resources.resource_filename(
                        'recastbackend','resources/inspire_to_rivet.json')
                ))

    rivet_downstreams = []
    for inspire_id, rivet_analyses in in2rivet.iteritems():
        for analysis in rivet_analyses + ['MC_GENERIC']:
            specific = copy.deepcopy(template)
            specific['pubkey'] = 'inspire/{}'.format(inspire_id)
            specific['configname'] = 'rivet_{}'.format(analysis.lower())
            specific['config']['preset_pars'] = {'analysis': analysis}
            rivet_downstreams.append(specific)
    return rivet_downstreams

def recastcatalogue():
    catalogue_file = os.environ['RECAST_CATALOGUE_FILE'] 
    return {int(k):v for k,v in json.load(open(catalogue_file)).iteritems()}

def build_catalogue():
    # for now we'll just reload the file each time later we might reference a database or public repo
    # that can receive pull requests

    # the goal is to return a list of configurations for analyes that come from the frontend
    # it will be indexed by the scan request ID

    # {
    #     '<analysisid>': {
    #         '<configA>': {
    #               'request_format: ''
    #               'wflowplugin': ''
    #               'config': {...}
    #          }
    #         '<configB>': {}
    #         '<configC>': {}
    #     }
    # }

    bckcfg = backendconfig()

    #1. first get all the full stack workflows and index them by analysis
    configdata = {}
    for x in bckcfg['recast_singlepass_wflowconfigs']:
        recast_analysis = recastapi.analysis.read.analysis_by_pub_identifier(*x['pubkey'].split('/'))
        if not recast_analysis:
            continue

        anid = recast_analysis['id']
        configdata.setdefault(anid,{})[x['configname']] = {
            'wflowplugin': x['wflowplugin'],
            'config': x['config'],
            'request_format': x['request_format']
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
        'config': 'from-request',
        'request_format': None
    }

    downstream_cfgs = comboflowcfg['downstream_configs'] + rivet_catalogue() + checkmate_catalogue()

    for downstream in downstream_cfgs:


        recast_analysis = recastapi.analysis.read.analysis_by_pub_identifier(*downstream['pubkey'].split('/'))
        if not recast_analysis:
            continue

        anid = recast_analysis['id']

        for possible_upstream in [fromrequest]+upstream_by_iface.get(downstream['required_interface'],[]):
            comboname = '{}-{}'.format(possible_upstream['configname'],downstream['configname'])
            config = {
                'adapter': possible_upstream['config'], 
                'analysis': downstream['config']
            }
            configdata.setdefault(anid,{})[comboname] = {
                'wflowplugin':'yadagecombo',
                'config': config,
                'request_format': possible_upstream['request_format']
            }
    return configdata
