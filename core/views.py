from datetime import date,datetime
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
#tambien uso en auth
from rest_framework.decorators import api_view,permission_classes
# permiso
from django.views.decorators.csrf import csrf_exempt
#
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from .models import *
from .serializer import * 
#dependencias para login
from rest_framework import viewsets,generics,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
#
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

###

#  time out.

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetRequestView(APIView):
    def post(self, request):
        print("Datos recibidos en el backend:", request.data)
        email = request.data.get('email')  # Obtén el email del cuerpo de la solicitud
        print("Email recibido:", email)
        
        if not email:
            return Response({'error': 'El campo email es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = get_random_string(50)
            user.profile.reset_password_token = token
            user.profile.save()

            reset_link = f"http://localhost:4200/auth/password-reset/{token}"
            send_mail(
                'Restablecimiento de Contraseña',
                f'Usa este enlace para restablecer tu contraseña: {reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            return Response({'message': 'Correo de restablecimiento enviado.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(APIView):
    def post(self, request, token):
        print("Token recibido:", token)
        print("Datos recibidos:", request.data)

        password = request.data.get('new_password')  # Cambiado a 'new_password'
        confirm_password = request.data.get('confirm_password')

        if not password or not confirm_password:
            print("Error: Falta password o confirm_password.")
            return Response({'error': 'Los campos de contraseña son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            print("Error: Las contraseñas no coinciden.")
            return Response({'error': 'Las contraseñas no coinciden.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = Profile.objects.get(reset_password_token=token)  # Verifica el token
            print("Usuario encontrado para el token:", user_profile.user)

            # Actualiza la contraseña
            user = user_profile.user
            user.password = make_password(password)
            user.save()

            # Limpia el token
            user_profile.reset_password_token = None
            user_profile.save()

            print("Contraseña actualizada exitosamente.")
            return Response({'message': 'Contraseña actualizada exitosamente.'}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            print("Error: Token inválido o expirado.")
            return Response({'error': 'Token inválido o expirado.'}, status=status.HTTP_404_NOT_FOUND)




class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, id):
    try:
        # Obtener la tarea o retornar 404 si no existe
        tarea = get_object_or_404(Tarea, id=id)

        # Serializar la tarea con los nuevos datos
        serializer = TareaSerializer(tarea, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)  # Código 200 para "OK"
        
        return Response(serializer.errors, status=400)  # Código 400 para errores de validación

    except ValidationError as e:
        return Response({'error': str(e)}, status=400)  # Manejo explícito de errores de validación

    except Exception as e:
        return Response({'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)  
    
    
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
# REVISAR CREAR USUARIO ALGO FALLA NO TEMA DE PROYECT VIEW
@api_view(['POST'])
def create_user(request):
    print("Datos recibidos:", request.data)  # Imprimir los datos que llegan
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        print("Usuario creado:", user.username)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Errores del serializador:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        miembro_id = request.data.get('miembro')  # ID del perfil del miembro
        asignado_por = request.user  # Usuario autenticado que realiza la asignación

        try:
            tarea = Tarea.objects.get(id=tarea_id)
            usuario = User.objects.get(id=miembro_id)
            perfil = Profile.objects.get(user=usuario)

            if tarea.asignada:
                return Response(
                    {"error": "La tarea ya ha sido asignada y no se puede volver a asignar."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            nueva_carga = perfil.cargaTrabajo + tarea.carga
            if nueva_carga > 10:
                return Response(
                    {"error": "La carga máxima por trabajador es 10. No se puede asignar esta tarea."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            asignacion = AsignacionTarea.objects.create(
                tarea=tarea,
                usuario=usuario,
                asignado_por=asignado_por
            )

            tarea.asignada = True
            tarea.save()
            perfil.cargaTrabajo = nueva_carga
            perfil.save()

            # Crear notificación
            Notification.objects.create(
                user=usuario,
                message=f"Se te ha asignado la tarea '{tarea.titulo}'."
            )
            

            serializer = AsignacionTareaSerializer(asignacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error al asignar la tarea o crear la notificación: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            print(f"Notificación creada para {usuario.username}")
        except Tarea.DoesNotExist:
            return Response({"error": "Tarea no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "Miembro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Verificar tareas vencidas para este usuario
        check_overdue_tasks(user)

        notifications = Notification.objects.filter(user=user, read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        notification_id = request.data.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            return Response({"message": "Notificación marcada como leída."})
        except Notification.DoesNotExist:
            return Response({"error": "Notificación no encontrada."}, status=status.HTTP_404_NOT_FOUND)



def check_overdue_tasks(user=None):
    print(f"Usuario recibido: {user}")
    today = date.today()  # Fecha de hoy sin la hora
    print(f"Fecha actual: {today}")

    # Convertir today's date a datetime para comparar solo las fechas
    today_at_midnight = datetime.combine(today, datetime.min.time())
    print(f"Fecha de hoy a medianoche: {today_at_midnight}")

    # Filtrar tareas vencidas asignadas a usuarios (empleados)
    overdue_tasks = (
        Tarea.objects.filter(asignaciontarea__usuario=user, fechamax__lt=today_at_midnight, estado=False)
        if user else
        Tarea.objects.filter(fechamax__lt=today_at_midnight, estado=False)
    )

    # Verifica cuántas tareas se están recuperando
    print(f"Tareas vencidas encontradas: {overdue_tasks.count()}")

    for task in overdue_tasks:
        print(f"Tarea encontrada: {task.titulo}, Fecha máxima: {task.fechamax}, Estado: {task.estado}")

        # Obtener el usuario al que se le enviará la notificación (empleado asignado)
        target_user = user if user else task.asignaciontarea_set.first().usuario
        print(f"Usuario al que se le enviará la notificación: {target_user.username}")

        message = f"La tarea '{task.titulo}' está fuera de plazo."

        # Verificar si ya existe una notificación para evitar duplicados
        existing_notification = Notification.objects.filter(
            user=target_user,
            message=message,
            type='overdue_task'
        ).first()

        if existing_notification:
            print("Ya existe una notificación para esta tarea.")
        else:
            print("Creando nueva notificación...")

            # Crear la notificación si no existe ya una igual
            Notification.objects.get_or_create(
                user=target_user,
                message=message,
                type='overdue_task',
                defaults={'read': False}
            )

    print("Proceso de verificación de tareas vencidas completado.")

    



        
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
        ).exclude(user_id__in=invited_users) # validador para no enviar varias invitaciones a 1 mismo empleado

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
            # Agregar al usuario al proyecto
            project = invitation.project  # Asumimos que hay un campo 'project' en Invitation
            user = invitation.invited_user  # Asumimos que hay un campo 'user' en Invitation

            # Relacionar el usuario con el proyecto
            project.members.add(user)  
            project.save()

        elif action == 'reject':
            invitation.status = 'rejected'
        
        else:
            return Response({'error': 'Acción no válida'}, status=400)

        invitation.save()
        return Response(InvitationSerializer(invitation).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_invitations(request):
    user = request.user  # Obtenemos el usuario autenticado
    pending_invitations = Invitation.objects.filter(invited_user=user, status='pending')  # Invitaciones pendientes

    
    # Serializamos las invitaciones para convertirlas en un formato JSON
    serializer = InvitationSerializer(pending_invitations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all().order_by('-prioridad', '-created_at')
    serializer_class = ProyectoSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def actualizar_prioridad(request, proyecto_id):
    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
        nueva_prioridad = request.data.get('prioridad')
        if nueva_prioridad not in [1, 3, 5]:
            return Response({'error': 'Prioridad inválida.'}, status=400)
        proyecto.prioridad = nueva_prioridad
        proyecto.save()
        return Response({'mensaje': 'Prioridad actualizada correctamente.'})
    except Proyecto.DoesNotExist:
        return Response({'error': 'Proyecto no encontrado.'}, status=404)
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_progress(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)

    # Validar el nuevo estado de avance
    avance = request.data.get('avance')
    if avance not in ['iniciada', 'Cursando', 'finalizada']:
        return Response({'error': 'Avance no válido'}, status=400)

    # Si el avance es "finalizada", descontar la carga al usuario
    if avance == 'finalizada' and not tarea.estado:  # Solo si aún no estaba finalizada
        try:
            # Obtener la asignación de la tarea para acceder al usuario asignado
            asignacion = AsignacionTarea.objects.get(tarea=tarea)
            perfil = Profile.objects.get(user=asignacion.usuario)

            # Descontar la carga de trabajo
            perfil.cargaTrabajo = max(perfil.cargaTrabajo - tarea.carga, 0)  # Evitar carga negativa
            perfil.save()  # Guardar cambios en el perfil

            # Cambiar el estado de la tarea a completada
            tarea.estado = True

        except AsignacionTarea.DoesNotExist:
            return Response({'error': 'Asignación no encontrada para esta tarea.'}, status=404)

    # Actualizar el avance de la tarea y guardar
    tarea.avance = avance
    tarea.save()

    # Devolver la tarea actualizada como respuesta
    serializer = TareaSerializer(tarea)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, proyecto_id):
    messages = Message.objects.filter(proyecto_id=proyecto_id).order_by('timestamp')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, proyecto_id):
    user = request.user
    content = request.data.get('content')
    if not content:
        return Response({'error': 'El contenido no puede estar vacío'}, status=status.HTTP_400_BAD_REQUEST)

    proyecto = Proyecto.objects.get(id=proyecto_id)
    message = Message.objects.create(proyecto=proyecto, user=user, content=content)
    serializer = MessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UpdateUserData(request):
    user = request.user
    data = request.data
    if data.get('name'):
        user.first_name = data.get('name')
        if data.get('email'):
            user.email = data.get('email')
            user.username = data.get('email')
            user.save()
            return Response({'message': 'Datos actualizados correctamente'}, status=status.HTTP_200_OK)
        return Response({'error': 'No se pudo actualizar los datos'}, status=status.HTTP_400_BAD_REQUEST)
    

class ProjectMetricsView(APIView):
    def get(self, request, project_id):
        try:
            proyecto = Proyecto.objects.get(id=project_id)
            metrics = proyecto.get_metrics()  # Obtén las métricas desde el método
 
            return Response(metrics, status=status.HTTP_200_OK)
        except Proyecto.DoesNotExist:
            return Response({"error": "Proyecto no encontrado"}, status=status.HTTP_404_NOT_FOUND)