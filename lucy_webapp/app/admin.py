from django.contrib import admin
from .models import Command, CommandExecution, Module, ModuleValue

class CommandAdmin(admin.ModelAdmin):
    list_display = ['system_name', 'name', 'description', 'flag']

class CommandExecutionAdmin(admin.ModelAdmin):
	list_display = ['id', 'command', 'timestamp', 'state', 'result', 'note']


# Register your models here.
admin.site.register(Command, CommandAdmin)
admin.site.register(CommandExecution, CommandExecutionAdmin)
admin.site.register(Module)
admin.site.register(ModuleValue)
