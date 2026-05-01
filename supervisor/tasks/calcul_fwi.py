from celery import shared_task
from django.utils import timezone
from supervisor.models import Node, Data
from supervisor.fwi import FWI
from supervisor.tasks.Pediction_ml import predict_single_fwi

@shared_task(name="calculate_fwi_task")
def calculate_fwi_task(d):
    device_id = d["device_id"]
    nodes = Node.objects.filter(reference=device_id)
    if not nodes.exists(): 
        return

    fwi = FWI()
    wind = fwi.calculate_wind(d["temperature"], d["humidity"], d["pressure"])
    
    for node in nodes:
        last = Data.objects.filter(node=node).order_by('-published_date').first()
        ffmc_prev = last.ffmc if last else 85
        dmc_prev  = last.dmc  if last else 6

        # Calculs FWI
        ffmc = fwi.FFMC(d["temperature"], d["humidity"], wind, d["rain"], ffmc_prev)
        dmc  = fwi.DMC(d["temperature"], d["humidity"], d["rain"], dmc_prev)
        isi  = fwi.ISI(wind, ffmc)
        isi  = float(isi.real)  # Corrige le problème du nombre complexe
        fwi_v = fwi.FWI(isi)
        fwi_v = float(fwi_v.real)  # Assure que fwi_v reste un nombre réel

        # Création de la ligne Data
        row = Data.objects.create(
            temperature=d["temperature"],
            humidity=d["humidity"],
            pressur=d["pressure"],
            gaz=d["gaz"],
            wind=wind,
            ffmc=ffmc,
            dmc=dmc,
            isi=isi,
            fwi=fwi_v,
            rain=d["rain"],
            published_date=timezone.now(),
            node=node
        )

        # Appel du job Celery pour la prédiction
        predict_single_fwi.delay(row.idData)

'''from celery import shared_task
from django.utils import timezone
from supervisor.models import Node, Data
from supervisor.fwi import FWI
from supervisor.tasks.Pediction_ml import predict_single_fwi

@shared_task(name="calculate_fwi_task")
def calculate_fwi_task(d):
    device_id = d["device_id"]
    nodes = Node.objects.filter(reference=device_id)
    if not nodes.exists(): return

    fwi = FWI()
    wind = fwi.calculate_wind(d["temperature"], d["humidity"], d["pressure"])
    for node in nodes:
        last = Data.objects.filter(node=node).order_by('-published_date').first()
        ffmc_prev = last.ffmc if last else 85
        dmc_prev  = last.dmc  if last else 6

        ffmc = fwi.FFMC(d["temperature"], d["humidity"], wind, d["rain"], ffmc_prev)
        dmc  = fwi.DMC(d["temperature"], d["humidity"], d["rain"], dmc_prev)
        isi  = fwi.ISI(wind, ffmc)
        fwi_v = fwi.FWI(isi)

        row = Data.objects.create(
            temperature=d["temperature"], humidity=d["humidity"], pressur=d["pressure"],
            gaz=d["gaz"], wind=wind, ffmc=ffmc, dmc=dmc, isi=isi, fwi=fwi_v,
            rain=d["rain"], published_date=timezone.now(), node=node
        )
        predict_single_fwi.delay(row.idData)  # Job 2'''
