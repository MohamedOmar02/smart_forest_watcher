from django.db import models

class Localisation(models.Model):
    gouvernorat_libelle = models.CharField(max_length=255, blank=True, null=True)
    delegation_libelle  = models.CharField(max_length=255, blank=True, null=True)
    localite_libelle    = models.CharField(max_length=255)
    latitude            = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude           = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        #? Enforce uniqueness based on combination of fields
        unique_together = ['gouvernorat_libelle', 'delegation_libelle', 'localite_libelle']

    def __str__(self):
        return f"{self.localite_libelle} ({self.delegation_libelle}, {self.gouvernorat_libelle})"

    def get_coordinates(self):
        return {'latitude': self.latitude, 'longitude': self.longitude}

