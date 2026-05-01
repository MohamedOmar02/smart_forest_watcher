from django.contrib.gis.db import models
from supervisor.models.node import Node
from django.utils import timezone

class Data(models.Model):  
    idData          = models.AutoField(primary_key=True)  
    temperature     = models.BigIntegerField(null=True)
    humidity        = models.BigIntegerField(null=True)
    pressur         = models.BigIntegerField(null=True)
    gaz             = models.BigIntegerField(null=True)
    detection       = models.BigIntegerField(null=True)
    wind            = models.FloatField(default=0, null=True)
    rain            = models.FloatField(default=0, null=True)
    ffmc            = models.FloatField(null=True)
    dmc             = models.FloatField(null=True)
    isi             = models.FloatField(null=True)
    fwi             = models.FloatField(null=True)        # FWI traditionnel
    fwi_predit      = models.FloatField(null=True)        # FWI ML prédit
    published_date  = models.DateTimeField(blank=True, null=True)
    node            = models.ForeignKey(Node, on_delete=models.CASCADE, null=True, related_name='datas')

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return (f'node : {self.node}, Temperature: {self.temperature}, Humidity: {self.humidity}, '
                f'Pressur: {self.pressur}, Gaz: {self.gaz}, Wind: {self.wind}, Rain: {self.rain}, '
                f'FWI: {self.fwi}, FWI_Predit: {self.fwi_predit}, Date: {self.published_date}')



