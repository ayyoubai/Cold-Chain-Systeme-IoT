from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('DHT', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(name='Incident', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=180)),
            ('description', models.TextField()),
            ('summary', models.TextField(blank=True)),
            ('location', models.CharField(blank=True, max_length=180)),
            ('severity', models.CharField(choices=[('low','Faible'),('medium','Moyenne'),('high','Élevée'),('critical','Critique')], default='medium', max_length=20)),
            ('status', models.CharField(choices=[('new','Nouveau'),('acknowledged','Pris en charge'),('in_progress','En cours'),('resolved','Résolu')], default='new', max_length=20)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('is_archived', models.BooleanField(default=False)),
            ('archived_at', models.DateTimeField(blank=True, null=True)),
            ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_incidents', to=settings.AUTH_USER_MODEL)),
            ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_incidents', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering':['-created_at']}),
        migrations.CreateModel(name='IncidentComment', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('content', models.TextField()),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_comments', to=settings.AUTH_USER_MODEL)),
            ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='DHT.incident')),
        ], options={'ordering':['created_at']}),
        migrations.CreateModel(name='IncidentReceipt', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('received_at', models.DateTimeField(auto_now_add=True)),
            ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='DHT.incident')),
            ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_receipts', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering':['-received_at'], 'unique_together':{('incident','operator')}}),
    ]
