from django.contrib.gis.db          import models
from supervisor.models.parcelle     import Parcelle


class Node(models.Model):
    name            = models.CharField(max_length=30)
    position        = models.PointField(null=True)
    latitude        = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reference       = models.CharField(max_length=50, null=True)
    node_range      = models.BigIntegerField(null=True,blank=True)
    sensors         = models.CharField(max_length=50, null=True)
    RSSI            = models.BigIntegerField(null=True)
    Battery_value   = models.BigIntegerField(null=True)
    status          = models.CharField(max_length=50, null=True)
    FWI             = models.FloatField(null=True,default= 0) 
    detection       = models.BigIntegerField(null=True)
    parcelle        = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='nodes')



    def __str__(self):
     return f'{self.name}' 
    