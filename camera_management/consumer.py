"""
WebSocket consumer — pushes camera fire alerts to the browser in real time.

URL: ws/cameras/
Group: "camera_alerts"

Same pattern as supervisor.consumer_redis.FrontWSConsumer.
The Celery task (alert_worker) calls channel_layer.group_send() → this
consumer forwards the event text to every connected browser tab.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer

CAMERA_GROUP = "camera_alerts"


class CameraAlertConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(CAMERA_GROUP, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(CAMERA_GROUP, self.channel_name)

    # Receives events sent by the Celery task via group_send
    async def camera_message(self, event):
        await self.send(text_data=event["text"])
