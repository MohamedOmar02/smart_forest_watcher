import json
from channels.generic.websocket import AsyncWebsocketConsumer

FRONT_GROUP = "fwi_front"

class FrontWSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(FRONT_GROUP, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(FRONT_GROUP, self.channel_name)

    async def fwi_message(self, event):  
        await self.send(text_data=event["text"])


#definit websocekot 
#ya3mil canal mebin serveur wil frontend plsieur client peut avoire meme donner 
#yab3ith donner mil back lil front en temps reel bil websocket
#group yjama3 websocket(les client ili 3mal connection fi wost site o yistana fi donner bich tjih ) barcha canal lil les client 









'''import json
from channels.generic.websocket import AsyncWebsocketConsumer

FRONT_GROUP = "fwi_front"

class FrontWSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(FRONT_GROUP, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(FRONT_GROUP, self.channel_name)

    async def fwi_message(self, event):
        await self.send(text_data=event["text"])'''
