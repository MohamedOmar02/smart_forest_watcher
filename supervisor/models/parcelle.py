from django.contrib.gis.db      import models
from supervisor.models.project  import Project

class Parcelle(models.Model):
    name = models.CharField(max_length=30)
    polygon = models.PolygonField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='parcelle')

    def __str__(self):
        if self.project:
            return f'Parcelle of project: {self.project.name}'
        else:
            return 'Parcelle with no project assigned for now'
