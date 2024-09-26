from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
#tambien uso en auth
from rest_framework.decorators import api_view,permission_classes
#
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from .models import *
from .serializer import * 
#dependencias para login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
###
def is_jefe(user):
    return user.profile.user_type == 'jefe'

@user_passes_test(is_jefe)
def assign_task(request):
    if request.method == 'POST':
        # Aquí iría la lógica para crear y asignar una tarea
        # Ejemplo básico de cómo manejar la asignación de tareas:
        task_title = request.POST.get('title')
        task_description = request.POST.get('description')
        task_assigned_to = request.POST.get('assigned_to')
        task_due_date = request.POST.get('due_date')
        task_priority = request.POST.get('priority')

        # Crear la nueva tarea
        Tarea.objects.create(
            title=task_title,
            description=task_description,
            assigned_to_id=task_assigned_to,
            assigned_by=request.user,
            due_date=task_due_date,
            priority=task_priority,
        )

        return redirect('some_view_name')  # Redirigir a alguna vista después de asignar la tarea

    # En caso de GET, renderiza un formulario para asignar tareas
    return render(request, 'assign_task.html')


# metodo para renderizar algun template que se tenga 

def test_url(request):
    if request.method =='GET':
        return render(request,'prueba.html')
# metodo para retornar a una url especifica 
def test_2(request):
    if request.method =='GET':
        return redirect('http://127.0.0.1:8000/test')
    
@api_view(['POST']) # especificación de tipo de petición
def create_user(request):
    serializer = UserSerializer(data=request.data) # transformamos el objeto a json con el serializer
    if serializer.is_valid(): # validamos que es un modelo valido 
        serializer.save() # guardamos el modelo en la bdd
        return Response(serializer.data, status=status.HTTP_201_CREATED) # respondemos con un 201 creado
    print(serializer.errors)# mostramos el error en caso de existir 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # retornamos el error en caso de ocurrir


# genreamos la clase de vista login
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        #definimos los parametros a buscar en la bdd
        username = request.data.get('username')
        password = request.data.get('password')
        # validamos que existan todos los datos.
        user = authenticate(username=username, password=password)
        #validamos que exista el usuario.
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'userdata':{
                    'username':user.username,
                    'useremail': user.email,
                    #enviamos los datos del usuario que se logea 
                    
                }
            })
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
## api_view permite declarar que tipo de petición se realizara
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # permission_clases isAuthenticated verifica que exita el token de auth otorgado en 
#la función login
def get_user_data(request):
    user = request.user
    user_data = {
        'username': user.username,
        'email': user.email,
        'user_type': getattr(user.profile, 'user_type', None),
        'name': getattr(user.profile, 'name', None),
    }
    return Response(user_data)

