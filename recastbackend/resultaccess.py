import os

def resultfilepath(basicreqid,backend,path):
    base_path = basicreqpath(basicreqid).rstrip('/')
    base_path += '/{}'.format(backend)
    return '{}/{}'.format(base_path,path)

def basicreqpath(basicreqid):
    path = os.environ['RECAST_RESULT_BASE'].rstrip('/')
    path += '/results/{}'.format(basicreqid)
    return path
