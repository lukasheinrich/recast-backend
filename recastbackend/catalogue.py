
backends = [
    {
        'name':'capbackend',
        'analyses':[
            {'analysis_id':1},
            {'analysis_id':4}
        ]
    }
]

def getBackends(analysid_id):
    return [b['name'] for b in backends if analysid_id in [a['analysis_id'] for a in b['analyses']]]
