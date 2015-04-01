import recastbackend.backendtasks  
import uuid
import recastapi.request

def prechain(request_uuid,point,jobguid,queuename):
  request_info = recastapi.request.request(request_uuid)
  jobinfo = request_info['parameter-points'][point]

  pre = ( recastbackend.backendtasks.prepare_workdir.subtask((request_uuid,jobguid),queue=queuename) |
          recastbackend.backendtasks.prepare_job.subtask((jobinfo,),queue=queuename)
        )
  return pre

def postchain(request_uuid,point,queuename,resultlist):           
  post = ( recastbackend.backendtasks.postresults.subtask((request_uuid,point,resultlist),queue=queuename) )
  return post

def wrapped_chain(request_uuid,point,analysis_chain,resultlist,queuename):
  jobguid = uuid.uuid1()
  
  pre  =  recastbackend.backendtasks.prechain(request_uuid,point,jobguid,queuename)
  post =  postchain(request_uuid,point,queuename,resultlist)

  chain = (pre | analysis_chain | post)
  return (jobguid,chain)

