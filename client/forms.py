from django import forms
from supervisor.models.project      import Project

class SelectProjectForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),  
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'}),
            empty_label="Select Project"
    )

    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client', None)
        super(SelectProjectForm, self).__init__(*args, **kwargs)
        if client:
            self.fields['project'].queryset = Project.objects.filter(client=client)

#win bich ya3mil selecte mte3 projet mte3o client 