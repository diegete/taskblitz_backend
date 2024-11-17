from django.contrib import admin
from .models import Profile, Tarea, Proyecto,AsignacionTarea,Invitation

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    search_fields = ('user__username', 'name', 'email')

class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'descripcion', 'carga', 'proyecto')
    search_fields = ('titulo', 'descripcion', 'carga', 'proyecto')

class ProyectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner')
    search_fields = ('title', 'owner', 'members','created_at')

class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('id','tarea_id', 'asignado_por_id','usuario_id')

class invitationAdmin(admin.ModelAdmin):
    list_display= ('id','status','project')


# Registra solo los modelos personalizados
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Tarea, TareaAdmin)
admin.site.register(Proyecto,ProyectAdmin)
admin.site.register(AsignacionTarea,AsignacionAdmin)
admin.site.register(Invitation, invitationAdmin)