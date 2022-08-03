from django.db import models
from datetime import datetime


class Command(models.Model):
	system_name = models.CharField(max_length=120)
	name = models.CharField(max_length=120)
	description = models.CharField(max_length=250)
	flag = models.BooleanField(default=True)

	def __str__(self):
		return self.system_name


class CommandExecution(models.Model):
	command = models.ForeignKey("Command", on_delete=models.CASCADE)
	value = models.IntegerField(default=0)
	#timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	#imestamp = models.DateTimeField()
	timestamp = models.BigIntegerField()
	state = models.CharField(max_length=250, default="Created")
	result = models.CharField(max_length=250, default="Processing")
	note = models.CharField(max_length=1000)


class Module(models.Model):
	name = models.CharField(max_length=250, unique=True)
	display_name = models.CharField(max_length=250)
	description = models.CharField(max_length=500, blank=True)
	error = models.CharField(max_length=250, blank=True)
	last_update = models.DateTimeField(default=datetime.now)

	def __str__(self):
		return self.display_name


class ModuleValue(models.Model):
	module = models.ForeignKey("Module", on_delete=models.CASCADE)
	variable = models.CharField(max_length=100)
	data_type = models.CharField(max_length=10)
	value = models.CharField(max_length=100)
	unit = models.CharField(max_length=10, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)
