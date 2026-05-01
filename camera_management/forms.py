from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions  import ValidationError
from .models import Camera
from supervisor.models.parcelle import Parcelle


class CameraForm(forms.ModelForm):
    """
    Mirrors NodeForm.
    The supervisor clicks a point on the Leaflet map → hidden fields are
    filled automatically by JavaScript, exactly like the Node flow.
    """

    camera_id = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class':       'form-control form-control-sm',
            'id':          'cameraId',
            'placeholder': 'Unique camera identifier (e.g. cam-001)',
            'style':       'height: calc(1.5em + .75rem + 3px);',
        })
    )

    api_key = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class':       'form-control form-control-sm',
            'id':          'cameraApiKey',
            'placeholder': 'Secret key shared with the Raspberry Pi',
            'style':       'height: calc(1.5em + .75rem + 3px);',
        })
    )

    class Meta:
        model  = Camera
        fields = [
            'name', 'camera_id', 'api_key',
            'location_description',
            'latitude', 'longitude', 'position',
            'parcelle', 'project',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'id':    'cameraName',
                'style': 'height: calc(1.5em + .75rem + 3px);',
            }),
            'location_description': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'id':    'cameraDesc',
                'style': 'height: calc(1.5em + .75rem + 3px);',
            }),
            # Hidden — filled by JS after Leaflet marker drop
            'latitude':  forms.HiddenInput(attrs={'id': 'cam_latitude'}),
            'longitude': forms.HiddenInput(attrs={'id': 'cam_longitude'}),
            'position':  forms.HiddenInput(attrs={'id': 'cameraPosition'}),
            'parcelle':  forms.HiddenInput(attrs={'id': 'cam_parcelle'}),
            'project':   forms.HiddenInput(attrs={'id': 'cam_project'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        position     = cleaned_data.get('position')
        parcelle     = cleaned_data.get('parcelle')

        if position and parcelle:
            try:
                parcelle_obj = Parcelle.objects.get(id=parcelle.id)
                # Swap axes to match the node validation pattern
                point = Point(position.y, position.x)
                if not parcelle_obj.polygon.contains(point):
                    raise ValidationError("The camera must be placed inside the parcelle polygon.")
            except Parcelle.DoesNotExist:
                raise ValidationError("Parcelle not found.")
        return cleaned_data
