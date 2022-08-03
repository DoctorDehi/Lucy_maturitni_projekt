from .models import *

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

import os
from threading import Thread
from time import sleep
from datetime import datetime, timedelta, timezone


# Create your views here.
@login_required
def index_view(request):
	return render(request, 'app/index.html')


@require_http_methods(["POST"])
def recieve_command(request):
	# continue only if user is logged in
	if request.user.is_authenticated:	
		# insert command into database
		try:
			com_exec = CommandExecution(
					command=Command.objects.get(
						system_name=request.POST.get('command'),
					),
					value=request.POST.get('value'),
					timestamp=int(request.POST.get('timestamp'))
			)
			print("Command %s recieved" % request.POST.get('command'))
			com_exec.save()
			response = {"status" : "OK", "message" : ""}
		except ObjectDoesNotExist:
			response = {"status" : "ERROR", "message" : "Error: Command doesn't exist"}

		except ValueError:
			response = {"status" : "ERROR", "message" : "Error: Uknown error"}
		
	else:
		response = {"status" : "ERROR", "message" : "Error: You must be logged in to send commands!"}
	return JsonResponse(response)


def system_shutdown(request):
	if request.user.is_authenticated:
		try:
			def shutdown_thread_function():
				sleep(2)
				os.system("sudo shutdown -h now")

			shutdown_thread = Thread(target = shutdown_thread_function)
			shutdown_thread.start()

			response = HttpResponse("Ok")
		except Exception as e:
			response = HttpResponse("Error: %s" % e)
			response.status_code = 500
	else:
		response = HttpResponse("Error: You are not allowed to do this!")
		response.status_code = 403
	return response


def get_variable_text(module_value):
	if module_value.unit:
		return "%s [%s]" % (module_value.variable, module_value.unit)
	else:
		return module_value.variable

def send_module_data(request):
	newest_values = ModuleValue.objects.filter(timestamp__gte=(datetime.now(timezone.utc) - timedelta(minutes=1))).order_by('-timestamp')
	if not newest_values:
		return JsonResponse({ "module_data" : {} })
	else:	
		module_data = {}
		for module_value in newest_values:
			# if module isn't in module data dict
			if not module_value.module.display_name in module_data.keys():
				
				module_data[module_value.module.display_name] = { get_variable_text(module_value) : module_value.value }
			else:
				# if module is in module data dict but the variable isn't
				if not module_value.variable in module_data[module_value.module.display_name].keys():
					module_data[module_value.module.display_name][get_variable_text(module_value)] = module_value.value

		return JsonResponse({ "module_data" : module_data}, safe=False)