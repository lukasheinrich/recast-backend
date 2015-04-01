from celery import Celery
app = Celery('productionapp')
app.config_from_object('recastbackend.productionconfig')
