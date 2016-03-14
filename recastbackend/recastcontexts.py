import backendcontexts
from recastapi.request import request

def context_from_request(request_uuid,parameter,backend,condition_index,outputdir):
    request_info = request(request_uuid)
    point_info   = request_info['parameter-points'][parameter]
    basic_info   = point_info['run-condition'][condition_index]
    input_url    = basic_info['lhe-file']
    common_ctx = backendcontexts.common_context(input_url,outputdir,backend)
    print common_ctx
    raise NotImplementedError('need to have code to get backend specific context from request')