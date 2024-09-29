from django.urls import include,path
from .views import * 
from rest_framework import routers

router = routers.DefaultRouter()



urlpatterns = [
    path('assign-task/', assign_task, name='assign_task'), #url tareas 
    path('api/users/', create_user, name='create_user'), #url usuarios
    path('login/' , LoginView.as_view(), name='login'), # cuando se use una clase de debe especificar con .as_view para usar su url
    path('api/user-data/',get_user_data, name='get_data'),  # url usuarios data
    path('', test_url, name='test'), # url acceder a admin
    path('test2/', test_2, name='test2'), #  url prueba
    path('crear-proyectos/', Crear_Proyectos, name='crear-proyectos'),
    
    
]