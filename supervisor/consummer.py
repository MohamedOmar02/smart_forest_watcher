import os
import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from supervisor.tasks.calcul_fwi import calculate_fwi_task
#يعمل connexion مع TTN
TTN_HOST = "eu1.cloud.thethings.network"
TTN_PORT = 8883
TTN_USER = os.environ.get("TTN_USER","lorae5app2@ttn")   
TTN_PASS = os.environ.get("TTN_PASS","NNSXS.7SPGHIMTGOGDQCROYRSD67YPZL4P5PZQ3MQJRCY.QBM3MPQHNDZWHOBTDDEUVQT2EBHP6ECICHBEWRZWWCGPMUY2FAKA")  # ton mot de passe TTN

class MQTTConsumer(AsyncWebsocketConsumer):
    #accepte connexion WebSocket (frontend)
    async def connect(self):
        await self.accept()
        self.client = mqtt.Client()
        self.client.username_pw_set(TTN_USER, TTN_PASS)
        self.client.tls_set()
        self.client.on_message = self.on_message
        self.client.connect(TTN_HOST, TTN_PORT, 60)
        self.client.subscribe("#", qos=1)
        self.client.loop_start()
        print("MQTT connected to TTN")

    async def disconnect(self, close_code):
        if hasattr(self, "client"):
            self.client.loop_stop()

    def on_message(self, client, userdata, message):
        try:
            parsed = json.loads(message.payload)
            up = parsed.get("uplink_message", {})
            dp = up.get("decoded_payload", {})
            data = {
                "device_id": parsed["end_device_ids"]["device_id"],
                "temperature": dp.get("temperature"),
                "humidity": dp.get("humidity"),
                "gaz": dp.get("gaz"),
                "pressure": dp.get("pressur"),
                "rain": dp.get("rain", 0),
                "rssi": (up.get("rx_metadata") or [{}])[0].get("rssi"),
            }
            # Envoie vers Celery
            calculate_fwi_task.delay(data)
        except Exception as e:
            print("MQTT parse error:", e)


#MQTTConsumer = récepteur temps réel des données TTN
#se connecte à TTN (MQTT)
#reçoit les données des capteurs
#extrait les valeurs
#envoie au worker Celery (calculate_fwi_task)


