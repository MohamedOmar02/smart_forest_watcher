from celery import Celery
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

app = Celery('predict_worker')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_routes = {
    'predict_single_fwi': {'queue': 'predict_fwi'},
}

app.autodiscover_tasks(['supervisor.tasks'])

if __name__ == '__main__':
    app.start()

# هذا Worker Celery
# يربط مع Django
# يقرأ من Redis
# ينفّذ tasks
# يخصّ prediction (FWI)