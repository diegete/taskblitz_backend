from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Tarea,Proyecto



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_type']

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id','title', 'owner', 'members']

    def validate_members(self, members):
        if not isinstance(members, list):
            raise serializers.ValidationError("Los miembros deben ser una lista de IDs de usuarios.")
        return members

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    proyectos = ProyectoSerializer(many=True, read_only= True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile','proyectos']
        

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user
        
class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'carga', 'proyecto']

    def validate_carga(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('La carga debe estar entre 1 y 10.')
        return value
