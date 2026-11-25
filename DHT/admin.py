from django.contrib import admin
from .models import Dht11, Incident, IncidentReceipt, IncidentComment

admin.site.register(Dht11)
admin.site.register(Incident)
admin.site.register(IncidentReceipt)
admin.site.register(IncidentComment)
