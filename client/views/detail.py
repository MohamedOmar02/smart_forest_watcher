from django.shortcuts               import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http                    import JsonResponse
from authentication.decorators      import client_required
from supervisor.models.data         import Data
from supervisor.models.project      import Project
from supervisor.models.node         import Node
from camera_management.models      import Camera, Detection
from django.utils                   import timezone
import datetime
#lezim ya3mil login
@login_required(login_url='client_login')
#lezim ykoun client mich admin 
@client_required
#yit2akid mil projet mawjoud o teba3 client
def node_detail(request, project_id, node_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
#capteur teba3 machrou3
    node = get_object_or_404(Node, id=node_id, parcelle__project=project)

    #* Filtrer les données pour les dernières 24 heures
    now = timezone.now()
    start_of_period = now - datetime.timedelta(days=1)

    data_entries = Data.objects.filter(node=node, published_date__range=(start_of_period, now))

    #* Créer un dictionnaire pour stocker les valeurs de température, humidité et gaz par intervalles de 1 heure
    temperature_dict = {}
    humidity_dict = {}
    gas_dict = {}
    
    for entry in data_entries:
        interval = entry.published_date.replace(minute=0, second=0, microsecond=0)  # Truncating to the nearest hour
        if interval not in temperature_dict:
            temperature_dict[interval] = []
        if interval not in humidity_dict:
            humidity_dict[interval] = []
        if interval not in gas_dict:
            gas_dict[interval] = []
        
        temperature_dict[interval].append(entry.temperature)
        humidity_dict[interval].append(entry.humidity)
        gas_dict[interval].append(entry.gaz)
    
    # Calculer les valeurs moyennes pour chaque intervalle de 1 heure
    temperatures = [{'interval': interval.isoformat(), 'temperature': sum(values)/len(values)} for interval, values in temperature_dict.items()]
    humidity = [{'interval': interval.isoformat(), 'humidity': sum(values)/len(values)} for interval, values in humidity_dict.items()]
    gas = [{'interval': interval.isoformat(), 'gas': sum(values)/len(values)} for interval, values in gas_dict.items()]
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'temperatures': temperatures,
            'humidity': humidity,
            'gas': gas
        })

    context = {
        'project': project,
        'node': node,
        'temperatures': temperatures,
        'humidity': humidity,
        'gas': gas,
    }

    return render(request, 'website/node_detail.html', context)


