from django.shortcuts                   import render, redirect
from django.contrib.auth.decorators     import login_required
from authentication.decorators          import client_required
from client.forms                       import SelectProjectForm



@login_required(login_url='client_login')
@client_required
def select_client_of_project(request):
    client = request.user.client  
    if request.method == 'POST':
        form = SelectProjectForm(request.POST, client=client)
        if form.is_valid():
            project_id = form.cleaned_data['project'].polygon_id
            return redirect('dashboard_client', project_id=project_id)
    else:
        form = SelectProjectForm(client=client)
    
    return render(request, 'website/select_project.html', {'form': form})


#Client يدخل الصفحة
#       ↓
#GET request
#      ↓
#يعرض dropdown projets
#       ↓
#Client يختار projet
#       ↓
#POST request
#       ↓
#form.is_valid()
#       ↓
#ياخو project_id
#       ↓
#redirect dashboard

