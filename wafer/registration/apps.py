# Needed due to django 1.7 changed app name restrictions

from django.apps import AppConfig

class RegistrationConfig(AppConfig):
   label = 'wafer.registration'
   name = 'wafer.registration'
