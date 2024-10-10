from django.urls import include,path
from .views import * 
from rest_framework import routers

router = routers.DefaultRouter()



urlpatterns = [
    path('create-task/', create_task, name='create-task'), #url tareas 
    path('get-tasks/', get_user_tasks, name='get-tasks'), #url tareas
    path('asignar-tarea/', AsignarTareaView.as_view(), name='asignar-tarea'),
    path('available-employees/<int:project_id>/', AvailableEmployeesView.as_view(), name='available_employees'),
    path('sent-invitation/', SendInvitationView.as_view(), name='sent-invitation'),
    path('manage-invitation/', ManageInvitationView.as_view(), name='manage-invitation'),
    path('get-tasks-by-usuario/',get_user_tasks_by_project , name='get-tasks'),
    path('get-members-details/',get_members_details , name='get-tasks'),
    path('api/users/', create_user, name='create_user'), #url usuarios
    path('login/' , LoginView.as_view(), name='login'), # cuando se use una clase de debe especificar con .as_view para usar su url
    path('api/user-data/',get_user_data, name='get_data'),  # url usuarios data
    path('', test_url, name='test'), # url acceder a admin
    path('test2/', test_2, name='test2'), #  url prueba
    path('crear-proyectos/', Crear_Proyectos, name='crear-proyectos'),
    
    
]