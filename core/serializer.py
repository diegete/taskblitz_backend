from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Tarea
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']  

# class ProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()  

#     class Meta:
#         model = Profile
#         fields = ['user', 'user_type', 'name', 'last_name']

#     def create(self, validated_data):
#         user_data = validated_data.pop('user')
#         user = User.objects.create(**user_data)
#         profile = Profile.objects.create(user=user, **validated_data)
#         return profile

#     def update(self, instance, validated_data):
#         user_data = validated_data.pop('user')
#         user = instance.user

  
#         user.username = user_data.get('username', user.username)
#         user.email = user_data.get('email', user.email)
#         user.save()

#         # Actualizar el perfil
#         instance.user_type = validated_data.get('user_type', instance.user_type)
#         instance.name = validated_data.get('name', instance.name)
#         instance.last_name = validated_data.get('last_name', instance.last_name)
#         instance.save()
#         return instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_type']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)
        return user
        
# class TareaSerializer(serializers.ModelSerializer):
#     assigned_to = serializers.StringRelatedField()  
#     assigned_by = serializers.StringRelatedField()

#     class Meta:
#         model = Task
#         fields = ['id', 'title', 'description', 'assigned_to', 'assigned_by', 'due_date', 'priority', 'completed']
