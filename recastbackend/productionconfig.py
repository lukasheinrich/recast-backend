BROKER_URL = 'redis://recast-demo'
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "recast-demo"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
CELERY_IMPORTS = ('recastbackend.backendtasks',)
