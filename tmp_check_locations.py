import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from supervisor.models.localisation import Localisation
print('count', Localisation.objects.count())
for loc in Localisation.objects.all()[:50]:
    print(loc.id, str(loc), loc.latitude, loc.longitude)
