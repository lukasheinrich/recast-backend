import os

def resultfilepath(requestId,parameter_pt,backend,path):
    content_path = os.environ['RECAST_CONTENT_PATH_TEMPL'].format(requestId,parameter_pt)
    content_path += '/'+backend
    return '{}/{}'.format(content_path,path)
