from django.urls import path
from .views import *


app_name='app'


urlpatterns = [
	path('', index_view, name="index"),
	path('_send_command', recieve_command, name="send_command"),
	path('_system_shutdown', system_shutdown, name="system_shutdown"),
	path('_get_module_data', send_module_data, name='get_module_data'),
]