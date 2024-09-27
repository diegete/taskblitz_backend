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
@api_view(['POST'])
def assign_task(request):
    # Verificar si el usuario es jefe
    if not is_jefe(request.user):
        return Response({'detail': 'No tienes permisos para asignar tareas.'}, status=status.HTTP_403_FORBIDDEN)
    
    # Obtener datos del proyecto (si están en el request)
    proyecto_id = request.data.get('proyecto_id')
    
    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return Response({'detail': 'Proyecto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Crear la tarea
    serializer = TareaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(proyecto=proyecto)  # Asignar explícitamente el proyecto
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Mostrar errores en consola si hay problemas
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    # Obtener proyectos donde el usuario es miembro
    proyectos = Proyecto.objects.filter(members=user)

    # Serializar el usuario y sus proyectos
    user_data = UserSerializer(user).data
    user_data['proyectos'] = ProyectoSerializer(proyectos, many=True).data  # Agregar proyectos al JSON

    return Response(user_data)

