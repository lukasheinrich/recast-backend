import os
from .resultextraction import extract_result
def resultfilepath(basicreqid,wflowconfig,path):
    base_path = basicreqpath(basicreqid).rstrip('/')
    base_path += '/{}'.format(wflowconfig)
    return '{}/{}'.format(base_path,path)

def basicreqpath(basicreqid):
    path = os.environ['RECAST_RESULT_BASE'].rstrip('/')
    path += '/results/{}'.format(basicreqid)
    return path

def basicreq_wflowconfigpath(basicreqid,wflowconfig):
    brpath = basicreqpath(basicreqid)
    return '{}/{}'.format(brpath.rstrip('/'),wflowconfig)

def resultdata(analysisid,wflowconfigname,basicreqid):
    fullpath = basicreq_wflowconfigpath(basicreqid,wflowconfigname)
    if not os.path.exists(fullpath):
    	return None
    return extract_result(fullpath,analysisid,wflowconfigname)
