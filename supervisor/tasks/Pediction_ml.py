import json, joblib, os
from celery import shared_task
from supervisor.models import Data
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

FRONT_GROUP = "fwi_front"

class _ML:
    model = None
    scaler = None

def _get_model():
    if _ML.model is None:
        _ML.model = joblib.load(os.path.join("supervisor", "ml_model", "xgb_fwi_model.joblib"))
    return _ML.model

def _get_scaler():
    if _ML.scaler is None:
        _ML.scaler = joblib.load(os.path.join("supervisor", "ml_model", "fwi_scaler.joblib"))
    return _ML.scaler

@shared_task(name="predict_single_fwi")
def predict_single_fwi(data_id):
    data = Data.objects.get(idData=data_id)
    model, scaler = _get_model(), _get_scaler()

    features = [
        float(data.temperature), float(data.humidity), float(data.wind),
        float(data.rain or 0), float(data.ffmc), float(data.dmc), float(data.isi)
    ]
    X = scaler.transform([features])
    y = float(model.predict(X)[0])
    data.fwi_predit = y
    data.save()

    channel_layer = get_channel_layer()

    # ✅ Payload bien structuré
    payload = json.dumps({
        "message": "MQTT data received",
        "data": {
            "device_id": data.node.reference,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "gaz": data.gaz,
            "pressure": data.pressur,   # ✅ corrigé
            "wind_speed": data.wind,
            "dmc": data.dmc,
            "fwi": data.fwi,
            "fwi_predit": data.fwi_predit,
            "published_date": data.published_date.isoformat()
        }
    })

    async_to_sync(channel_layer.group_send)(
        FRONT_GROUP,
        {"type": "fwi_message", "text": payload}
    )











    



'''import json, joblib, os
from celery import shared_task
from supervisor.models import Data
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

FRONT_GROUP = "fwi_front"

class _ML:
    model = None
    scaler = None

def _get_model():
    if _ML.model is None:
        _ML.model = joblib.load(os.path.join("supervisor","ml_model","xgb_fwi_model.joblib"))
    return _ML.model

def _get_scaler():
    if _ML.scaler is None:
        _ML.scaler = joblib.load(os.path.join("supervisor","ml_model","fwi_scaler.joblib"))
    return _ML.scaler

@shared_task(name="predict_single_fwi")
def predict_single_fwi(data_id):
    data = Data.objects.get(idData=data_id)
    model, scaler = _get_model(), _get_scaler()
    features = [
        float(data.temperature), float(data.humidity), float(data.wind),
        float(data.rain or 0), float(data.ffmc), float(data.dmc), float(data.isi)
    ]
    X = scaler.transform([features])
    y = float(model.predict(X)[0])
    data.fwi_predit = y
    data.save()

    channel_layer = get_channel_layer()
    payload = json.dumps({
        "device_id": data.node.reference,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "wind": data.wind,
        "dmc": data.dmc,
        "fwi": data.fwi,
        "fwi_predit": data.fwi_predit,
        "published_date": data.published_date.isoformat()
    })
    async_to_sync(channel_layer.group_send)(FRONT_GROUP, {"type": "fwi.message", "text": payload})'''
