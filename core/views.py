from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
#tambien uso en auth
from rest_framework.decorators import api_view,permission_classes
# permiso
from django.views.decorators.csrf import csrf_exempt
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
# vistar tareas
@api_view(['POST'])
def create_task(request):
    print(request.data)  # Revisa los datos recibidos
    serializer = TareaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    print(serializer.errors)  # Agregar esta línea
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tasks(request):
    user = request.user

    # Obtener tareas en los proyectos donde el usuario es miembro
    proyectos = Proyecto.objects.filter(members=user)
    tareas = Tarea.objects.filter(proyecto__in=proyectos)  # Filtrar tareas que pertenecen a esos proyectos

    # Serializar las tareas
    tareas_serializadas = TareaSerializer(tareas, many=True).data

    return Response({'tareas': tareas_serializadas})


# tests 
def test_url(request):
    if request.method =='GET':
        return render(request,'prueba.html')
# metodo para retornar a una url especifica 
def test_2(request):
    if request.method =='GET':
        return redirect('http://127.0.0.1:8000/test')
    
#vistar crear ususario
@api_view(['POST']) 
def create_user(request):
    serializer = UserSerializer(data=request.data) # transformamos el objeto a json con el serializer
    if serializer.is_valid(): # validamos que es un modelo valido 
        serializer.save() # guardamos el modelo en la bdd
        return Response(serializer.data, status=status.HTTP_201_CREATED) # respondemos con un 201 creado
    print(serializer.errors)# mostramos el error en caso de existir 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # retornamos el error en caso de ocurrir

# vista login
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
# vista traer datos del usuario
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tasks_by_project(request):
    project_id = request.GET.get('project_id')  # Obtener el ID del proyecto desde la URL
    user = request.user

    # Filtrar las tareas del usuario para el proyecto seleccionado
    asignaciones = AsignacionTarea.objects.filter(usuario=user, tarea__proyecto_id=project_id)
    
    # Serializar los datos
    serializer = AsignacionTareaSerializer(asignaciones, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# vista crear proyectos
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Crear_Proyectos(request):
    print(request.data)  # Agrega esto para ver los datos que llegan
    data = request.data.copy()
    data['owner'] = request.user.id
    
    if not data.get('members'):
        data['members'] = [request.user.id]  # Asegúrate de que el owner sea miembro también

    serializer = ProyectoSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# vista asignar tareas 

class AsignarTareaView(APIView):
    def post(self, request):
        tarea_id = request.data.get('tarea')
        miembro_id = request.data.get('miembro')  # Cambiado a 'miembro'
        asignado_por = request.user  # Usuario autenticado que realiza la asignación

        try:
            tarea = Tarea.objects.get(id=tarea_id)
            usuario = User.objects.get(id=miembro_id)  # Cambiado aquí

            # Verificar si la tarea ya está asignada
            if tarea.asignada:
                return Response({"error": "La tarea ya ha sido asignada y no se puede volver a asignar."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # Crear la asignación
            asignacion = AsignacionTarea.objects.create(
                tarea=tarea,
                usuario=usuario,
                asignado_por=asignado_por
            )

            # Marcar la tarea como asignada
            tarea.asignada = True
            tarea.save()  # Guardar el cambio en la base de datos

            serializer = AsignacionTareaSerializer(asignacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Tarea.DoesNotExist:
            return Response({"error": "Tarea no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "Miembro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        
@api_view(['POST'])
def get_members_details(request):
    ids = request.data.get('ids', [])
    members = User.objects.filter(id__in=ids)
    serializer = UserSerializer(members, many=True)
    return Response(serializer.data)

# invitaciones a proyecto 
class AvailableEmployeesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Proyecto.objects.get(id=project_id)
        except Proyecto.DoesNotExist:
            return Response({'error': 'Proyecto no encontrado'}, status=404)

        # Filtrar empleados que aún no han sido invitados ni están en el proyecto
        invited_users = Invitation.objects.filter(project=project).values_list('invited_user_id', flat=True)
        
        # Filtrar empleados en el modelo Profile donde el user_type sea "empleado" y que no hayan sido invitados
        available_employees = Profile.objects.filter(
            user_type='empleado'
        ).exclude(user_id__in=invited_users)

        # Devolver la lista de empleados disponibles con su id y username
        return Response([{'id': employee.user.id, 'username': employee.user.username} for employee in available_employees])
    

class SendInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('proyecto')
        invited_user_id = request.data.get('invited_user')
        print("Proyecto:", project_id)
        print("Invitado:", invited_user_id)


        # Verifica si ambos campos están presentes
        if not project_id or not invited_user_id:
            return Response({'error': 'Proyecto o usuario no proporcionados'}, status=400)
        
            
        try:
            # Verifica si existen los objetos en la base de datos
            project = Proyecto.objects.get(id=project_id)
            invited_user = User.objects.get(id=invited_user_id)
        except Proyecto.DoesNotExist:
            return Response({'error': 'El proyecto no existe'}, status=400)
        except User.DoesNotExist:
            return Response({'error': 'El usuario no existe'}, status=400)

        # Crea la invitación
        invitation = Invitation.objects.create(project=project, invited_user=invited_user)
        return Response(InvitationSerializer(invitation).data, status=201)



class ManageInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        action = request.data.get('action')  # "accept" o "reject"
        
        try:
            invitation = Invitation.objects.get(id=invitation_id)
        except Invitation.DoesNotExist:
            return Response({'error': 'Invitación no encontrada'}, status=404)
        
        if action == 'accept':
            invitation.status = 'accepted'
        elif action == 'reject':
            invitation.status = 'rejected'
        else:
            return Response({'error': 'Acción no válida'}, status=400)
        
        invitation.save()
        return Response(InvitationSerializer(invitation).data)



