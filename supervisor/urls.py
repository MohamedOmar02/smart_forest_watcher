from django.urls    import path
from .              import views
from camera_management import views as cam_views


app_name = 'supervisor'

urlpatterns = [
        #######* Dashboard / Global endpoints ##########
    path('', views.index, name='dashboard_super'),
    path('get_all_assets/', views.get_all_assets, name='get_all_assets'),
    
        #######* CRUD OF CLIENT  ##########
    path('list_client/', views.list_clients, name="list_client"),
    path('add_client/', views.add_client, name="add_client"),
    path('update_client/<int:pk>/', views.update_client, name="update_client"),
    path('delete_client/<int:pk>/', views.delete_client, name="delete_client"),

        #######* CRUD OF Project  ##########
    path('project_list/', views.list_project, name='list_project'),
    path('add_project/', views.add_project, name= 'add_project'),
    path('update_project/<int:project_id>', views.update_project, name='update_project'),
    path('delete_project/<int:pk>', views.delete_project, name='delete_project'),
    path('add_parcelle/', views.parcelle_create, name = 'add_parcelle'),
    path('get_parcelles_for_project/', views.get_parcelles_for_project, name='get_parcelles_for_project'),

        #######* Node Related  ##########
    path('add_node/', views.node_create, name='add_node'),
    path('get_parcelles_with_nodes_for_project/', views.get_parcelles_with_nodes_for_project, name='get_parcelles_with_nodes_for_project'),
    path('get_project_details/<int:project_id>/', views.get_project_details, name='get_project_details'),

        #######* Camera Related  ##########
    path('add_camera/', cam_views.add_camera, name='add_camera'),
    path('get_cameras_for_project/', cam_views.list_cameras_for_project, name='get_cameras_for_project'),
    path('update_parcels_nodes/', views.update_parcels_nodes, name='update_parcels_nodes'),
]


