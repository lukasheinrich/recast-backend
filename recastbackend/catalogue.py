import pickle
import pkg_resources

implemented_analyses = {
  '858fb12c-b62f-9954-1997-a6ff8c27be0e' :
       {
        'queue':'dmhiggs_queue',
        'blueprint':'recastresultblueprints.dmhiggs_result.blueprint:blueprint'
        },
  '3ad4efdb-0170-fb94-75a5-8a1279386745' :
       {
        'queue':'hype_queue',
        'blueprint':'recastresultblueprints.hype_result.blueprint:blueprint'
       },
  '19c471ff-2514-eb44-0d82-59563cc38dab' :
      {
       'queue':'susy_queue',
       'blueprint':'recastresultblueprints.susyhiggs_result.blueprint:blueprint'
      },
  '09986001-6348-2fa4-59f8-f1d1b4a65776' :
      {
       'queue':'fullchain_queue',
       'blueprint':'recastresultblueprints.fullchain_result.blueprint:blueprint'
      },
}

def rivet_info():
    rivetnameToUUID = pickle.loads(pkg_resources.resource_string('recastbackend','rivetmap.pickle'))
    return {v:{'workflow' :'}',
               'queue'    :'rivet_queue',
               'blueprint':'recastresultblueprints.rivet_result.blueprint:blueprint',
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
