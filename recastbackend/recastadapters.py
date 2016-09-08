import json
import yaml
def null_result(resultdir,**kwargs):
    return {
        'lower_2sig_expected_CLs':None,
        'lower_1sig_expected_CLs':None,
        'expected_CLs':None,
        'upper_1sig_expected_CLs':None,
        'upper_2sig_expected_CLs':None,
        'observed_CLs':None,
        'log_likelihood_at_reference':None
    }

def standard_result(resultdir,**kwargs):
    result = null_result(resultdir)
    data = json.load(open('{}/{}'.format(resultdir,kwargs['jsonfilepath'])))
    result.update(**data)
    return result


def pMSSMFormat_BestSR(resultdir,**kwargs):
    result = null_result(resultdir)
    yamldata = yaml.load(kwargs['yamlfilepath'])
    best_obs, best_exp = None, None
    for SR,SRData in yamldata.iteritems():
        print SR,SRData
        model, CLs_obs, CLs_exp = SRData
        if CLs_exp < best_exp or best_exp is None:
            best_obs, best_exp = CLs_obs, CLs_exp
    result.update(
        expected_CLs = best_exp,
        observed_CLs = best_obs
    )
    return result
