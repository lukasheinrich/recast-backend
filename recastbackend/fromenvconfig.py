BROKER_URL = 'redis://localhost'
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
CELERY_IMPORTS = ('recastbackend.backendtasks',)
CELERY_TRACK_STARTED = True
