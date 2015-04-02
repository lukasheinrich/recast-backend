#import recastdmhiggs.dmhiggs_backendtasks as dmhiggs_backendtasks
#import recastdmhiggs.dmhiggs_blueprint as dmhiggs_blueprint
#import recasthype.hype_backendtasks as hype_backendtasks
#import recasthype.hype_blueprint as hype_blueprint

import recastsusyhiggs.backendtasks
import recastsusyhiggs.blueprint

implemented_analyses = {
  # dmhiggs_blueprint.RECAST_ANALYSIS_ID :
  #     {
  #      'workflow':dmhiggs_backendtasks,
  #      'queue':'dmhiggs_queue',
  #      'blueprint':dmhiggs_blueprint.blueprint
  #      },
  # hype_blueprint.RECAST_ANALYSIS_ID :
  #     {
  #      'workflow':hype_backendtasks,
  #      'queue':'hype_queue',
  #      'blueprint':hype_blueprint.blueprint
  #     },
  recastsusyhiggs.blueprint.RECAST_ANALYSIS_ID :
      {
       'workflow':'recastsusyhiggs.backendtasks',
       'queue':'susy_queue',
       'blueprint':'recastsusyhiggs.blueprint:blueprint'
      }  

}
