from django.contrib.auth.models         import User
from django.http                        import HttpResponse, JsonResponse
from django.shortcuts                   import render, redirect, get_object_or_404
from django.contrib.auth.decorators     import login_required
from django.contrib                     import messages
from authentication.decorators          import supervisor_required
from supervisor.forms                   import ClientForm
from client.models                      import Client
from django.core.exceptions             import ValidationError
import json


@login_required(login_url='supervisor_login')
@supervisor_required
def list_clients(request):
    clients = Client.objects.all()
    form = ClientForm()
    return render(request, 'website/clients/list_client.html', {'clients': clients, 'form': form})


@login_required(login_url='supervisor_login')
@supervisor_required
def add_client(request):
    show_modal = False
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                client = form.save(commit=False)
                client.save()
                form.save_m2m()
                messages.success(request, 'Client added successfully.')
                return redirect('supervisor:list_client')
            except ValidationError as e:
                show_modal = True
                form.add_error(None, e)
        else:
            show_modal = True
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm()
    clients = Client.objects.all()
    return render(request, 'website/clients/list_client.html', {'form': form, 'clients': clients, 'show_modal': show_modal})



@login_required(login_url='supervisor_login')
@supervisor_required
def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    user = get_object_or_404(User, pk=client.user.pk) 

    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            client = form.save(commit=False)
            # Update the user associated with the client
            user.username = form.cleaned_data.get('username')
            user.email = form.cleaned_data.get('email')
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data.get('password'))
            user.save()
            client.user = user
            client.save()
            messages.success(request, 'Client updated successfully.')

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                client_data = {
                    'pk': client.pk,
                    'firstName': client.firstName,
                    'lastName': client.lastName,
                    'username': user.username,
                    'email': user.email,
                    'phone': client.phone,
                    'image': client.image.url if client.image else ''
                }
                return JsonResponse({'success': True, 'client': client_data})
            return redirect('supervisor:list_client')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            messages.error(request, 'Please correct the errors below.')
    else:
        client_data = {
            'firstName': client.firstName,
            'lastName': client.lastName,
            'email': client.email,
            'phone': client.phone,
            'username': client.username,
            'image': client.image.url if client.image else ''
        }
        return HttpResponse(json.dumps(client_data), content_type="application/json")
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    return render(request, 'website/clients/list_client.html', {'form': form, 'clients': Client.objects.all()})



@login_required(login_url='supervisor_login')
@supervisor_required
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    return redirect('supervisor:list_client')
