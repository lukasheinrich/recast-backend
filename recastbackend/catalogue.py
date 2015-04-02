#import recastdmhiggs.dmhiggs_backendtasks as dmhiggs_backendtasks
#import recastdmhiggs.dmhiggs_blueprint as dmhiggs_blueprint
#import recasthype.hype_backendtasks as hype_backendtasks
#import recasthype.hype_blueprint as hype_blueprint

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
  '19c471ff-2514-eb44-0d82-59563cc38dab' :
      {
       'workflow':'recastsusyhiggs.backendtasks',
       'queue':'susy_queue',
       'blueprint':'recastsusyhiggs.blueprint:blueprint'
      }  

}
