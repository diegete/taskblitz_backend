Instalar dependencias
Utiliza el siguiente comando en la consola para instalar todas las dependencias del proyecto:

pip install -r requirements.txt


Iniciar el servidor

Ejecuta el siguiente comando para iniciar el servidor de desarrollo:
python manage.py runserver
Configurar recuperación de cuenta


Configurar recuperación de cuenta
Para habilitar la funcionalidad de recuperación de cuenta por correo:

Configura una instancia en la nube para alojar el proyecto.
Genera una contraseña de aplicación desde una cuenta de Google.
Agrega las credenciales en el archivo settings.py, incluyendo las siguientes variables relacionadas con el servicio de correo electrónico:
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_BACKEND
SOCIALACCOUNT_PROVIDERS
client_id
secret
Nota: Si no deseas probar esta funcionalidad, puedes omitir la configuración de la nube y la contraseña de aplicación.

