from django.urls import include,path
from .views import * 
from rest_framework import routers

router = routers.DefaultRouter()



urlpatterns = [
    path('create-task/', create_task, name='create-task'), #url crear 
    path('update-tasks/<int:id>/', update_task, name='update-task'), #url actualizar tarea
    path('get-tasks/', get_user_tasks, name='get-tasks'), #url obtener
    path('asignar-tarea/', AsignarTareaView.as_view(), name='asignar-tarea'), # url asignar las tareas
    path('available-employees/<int:project_id>/', AvailableEmployeesView.as_view(), name='available_employees'), # url empleados Dis
    path('pending-invitations/',get_pending_invitations, name='pending-invitations' ), # url obtener invitaciones pendientes
    path('sent-invitation/', SendInvitationView.as_view(), name='sent-invitation'), # url enviar invitaciones
    path('manage-invitation/<int:invitation_id>/', ManageInvitationView.as_view(), name='manage-invitation'),# url administra invita
    path('get-tasks-by-usuario/',get_user_tasks_by_project , name='get-tasks-by-usuario'),# url obtener tareas por usuario
    path('get-members-details/',get_members_details , name='get-members-details'),# url detelles usuarios 
    path('api/users/', create_user, name='create_user'), #url crear usuarios
    path('login/' , LoginView.as_view(), name='login'), # cuando se use una clase de debe especificar con .as_view para usar su url
    path('api/user-data/',get_user_data, name='get_data'),  # arriba url login y esta linea = url usuarios data 
    path('', test_url, name='test'), # url acceder a admin
    path('test2/', test_2, name='test2'), #  url prueba
    path('crear-proyectos/', Crear_Proyectos, name='crear-proyectos'),# url crear proyectos
    path('proyecto/<int:proyecto_id>/prioridad/', actualizar_prioridad, name='actualizar_prioridad'),# url prioridad proyectos
    
    
]