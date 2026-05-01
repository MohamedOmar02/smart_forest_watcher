from django                         import forms
from supervisor.models.project      import Project
from supervisor.models.parcelle     import Parcelle



class ParcelleForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=True,
        empty_label='Select Project',
        widget=forms.Select(attrs={
            'name': 'project',
            'class': 'form-control',
            'id': 'id_project'
        })
    )
    
    class Meta:
        model = Parcelle
        fields = ['name', 'project']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ploygon Name',
                'required': True,
                'id': 'id_name_polygon'
                }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].widget.choices = [
            (project.polygon_id, f"{project.name} (lat: {project.city.latitude}, lon: {project.city.longitude})", 
             {'data-latitude': project.city.latitude, 'data-longitude': project.city.longitude})
            for project in Project.objects.all() if project.city
        ]

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('This field is required.')
        return name