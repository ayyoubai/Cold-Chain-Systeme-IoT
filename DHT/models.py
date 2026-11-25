from django.db import models
from django.contrib.auth.models import User

class Dht11(models.Model):
    temp = models.FloatField(null=True)
    hum = models.FloatField(null=True)
    dt = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.temp}°C / {self.hum}% - {self.dt}"

class Incident(models.Model):
    SEVERITY_CHOICES = [('low','Faible'),('medium','Moyenne'),('high','Élevée'),('critical','Critique')]
    STATUS_CHOICES = [('new','Nouveau'),('acknowledged','Pris en charge'),('in_progress','En cours'),('resolved','Résolu')]
    title = models.CharField(max_length=180)
    description = models.TextField()
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=180, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_incidents')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"INC-{self.pk or 'NEW'} — {self.title}"


class IncidentReceipt(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='receipts')
    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incident_receipts')
    received_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('incident', 'operator')
        ordering = ['-received_at']


class IncidentComment(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incident_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
