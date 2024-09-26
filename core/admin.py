from django.contrib import admin
from .models import Profile, Tarea, Proyecto

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    search_fields = ('user__username', 'name', 'email')

class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'carga', 'proyecto')
    search_fields = ('titulo', 'descripcion', 'carga', 'proyecto')

class ProyectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner')
    search_fields = ('title', 'owner', 'members','created_at')

# Registra solo los modelos personalizados
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Tarea, TareaAdmin)
admin.site.register(Proyecto,ProyectAdmin)
