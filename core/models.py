from django.db import models
from django.contrib.auth.models import User
from pydantic import ValidationError

class Profile(models.Model):
    USER_TYPES = (
        ('jefe', 'Jefe'),
        ('empleado', 'Empleado'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    cargaTrabajo = models.IntegerField(default=0, null=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.user.username
    def clean(self): 
        if self.cargaTrabajo > 10:
            return ValidationError('La carga máxima por trabajador es 10')
    
class Proyecto(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(User, related_name='owned_projects', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    prioridad = models.IntegerField(default=1, choices=[(1, 'Baja'), (3, 'Media'), (5, 'Alta')], null=True)
    def save(self, *args, **kwargs):
        # Asegurarse de que solo los usuarios de tipo jefe puedan crear un proyecto
        if not self.owner.profile.user_type == 'jefe':
            raise ValueError("Solo los jefes pueden crear proyectos.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class Tarea(models.Model):
    AVANCE_TYPE =(
        ('iniciada', 'Iniciada'),
        ('en curso', 'En Curso'),
        ('finalizada', 'Finalizada'),
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    carga = models.IntegerField()  # Peso de la tarea de 1 a 10
    proyecto = models.ForeignKey(Proyecto, related_name='tareas', on_delete=models.CASCADE)
    asignada = models.BooleanField(null=True)
    fechaInicio = models.DateField(null=True)
    fechamax = models.DateField(null=True)
    avance = models.CharField(max_length=15, choices=AVANCE_TYPE, null= True)
    estado = models.BooleanField(default=False, null=True)


    def __str__(self):
        return self.titulo

    def clean(self):
        # Validar que la carga esté entre 1 y 10
        if self.carga < 1 or self.carga > 10:
            raise ValidationError('La carga debe estar entre 1 y 10.')

# Tabla intermedia entre Tarea y Usuario para asignar tareas a los usuarios
    

class AsignacionTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    asignado_por = models.ForeignKey(User, related_name='asignaciones_hechas', on_delete=models.SET_NULL, null=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tarea: {self.tarea.titulo}, Asignada a: {self.usuario.username}"


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
    ]
    
    project = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitación a {self.invited_user.username} para unirse a {self.project.title}"

class Message(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."