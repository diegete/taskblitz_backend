from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Tarea,Proyecto,AsignacionTarea,Invitation



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_type']

class ProyectoSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
        model = Proyecto
        fields = ['id','title', 'owner', 'members','created_at','prioridad']

    def validate_members(self, members):
        if not isinstance(members, list):
            raise serializers.ValidationError("Los miembros deben ser una lista de IDs de usuarios.")
        return members
    
    def to_representation(self, instance):
        # Al devolver los datos, mostramos los miembros completos
        representation = super().to_representation(instance)
        representation['members'] = UserSerializer(instance.members, many=True).data
        return representation

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    proyectos = ProyectoSerializer(many=True, read_only= True)
    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'profile','proyectos']
        

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user
        
class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = ['id','titulo', 'descripcion', 'carga', 'proyecto','asignada','fechaInicio','fechamax']

    def validate_carga(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('La carga debe estar entre 1 y 10.')
        return value


class AsignacionTareaSerializer(serializers.ModelSerializer):
    tarea = TareaSerializer()  # Aquí usamos el nested serializer para obtener los detalles completos de la tarea
    
    class Meta:
        model = AsignacionTarea
        fields = ['tarea', 'usuario', 'asignado_por', 'fecha_asignacion']
    def create(self, validated_data):
        # Aquí puedes agregar validaciones adicionales si es necesario.
        return AsignacionTarea.objects.create(**validated_data)


class InvitationSerializer(serializers.ModelSerializer):
    project = ProyectoSerializer()
    class Meta:
        model = Invitation
        fields = ['id', 'project', 'invited_user', 'status', 'created_at']
        