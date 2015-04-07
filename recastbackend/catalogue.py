import pickle
import pkg_resources

implemented_analyses = {
  '858fb12c-b62f-9954-1997-a6ff8c27be0e' :
       {
        'workflow':'recastdmhiggs.backendtasks',
        'queue':'dmhiggs_queue',
        'blueprint':'recastdmhiggs.blueprint:blueprint'
        },
  '3ad4efdb-0170-fb94-75a5-8a1279386745' :
       {
        'workflow':'recasthype.backendtasks',
        'queue':'hype_queue',
        'blueprint':'recasthype.blueprint:blueprint'
       },
  '19c471ff-2514-eb44-0d82-59563cc38dab' :
      {
       'workflow':'recastsusyhiggs.backendtasks',
       'queue':'susy_queue',
       'blueprint':'recastsusyhiggs.blueprint:blueprint'
      }
}

def rivet_info():
  rivetnameToUUID = pickle.loads(pkg_resources.resource_string('recastbackend','rivetmap.pickle'))
  return {v:{'workflow' :'recastrivet.backendtasks',
             'queue'    :'rivet_queue',
             'blueprint':'recastrivet.blueprint:blueprint',
             'analysis' : k} for k,v in rivetnameToUUID.iteritems()}

rivet_analyses = rivet_info()

all_backend_catalogue = {
  'dedicated': implemented_analyses,
  'rivet'    : rivet_analyses
}

def getBackends(analysis_uuid):
  backends = []
  for k in all_backend_catalogue.keys():
    if analysis_uuid in all_backend_catalogue[k]:
      backends+=[k]
  return backends
