import json
from collections import Counter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from .forms import IncidentForm, CommentForm, OperatorForm, OperatorEditForm
from .models import Incident, IncidentReceipt, IncidentComment


def admin_required(view):
    return login_required(user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view))


def login_view(request):
    if request.user.is_authenticated:
        return redirect('incidents-dashboard')
    error = ''
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('incidents-dashboard')
        error = 'Identifiant ou mot de passe incorrect.'
    return render(request, 'DHT/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def _filter_dates(queryset, request):
    start = parse_date(request.GET.get('start', '') or '')
    end = parse_date(request.GET.get('end', '') or '')
    if start: queryset = queryset.filter(created_at__date__gte=start)
    if end: queryset = queryset.filter(created_at__date__lte=end)
    return queryset, start, end


@login_required
def dashboard(request):
    incidents, start, end = _filter_dates(Incident.objects.filter(is_archived=False), request)
    incidents = incidents.select_related('created_by', 'assigned_to')
    status_counts = {key: incidents.filter(status=key).count() for key, _ in Incident.STATUS_CHOICES}
    severity_counts = {key: incidents.filter(severity=key).count() for key, _ in Incident.SEVERITY_CHOICES}
    chart_rows = list(incidents.order_by('created_at').values('created_at', 'severity', 'status'))
    chart_rows = [{'date': r['created_at'].strftime('%Y-%m-%d'), 'severity': r['severity'], 'status': r['status']} for r in chart_rows]
    recent = incidents[:10]
    context = {'incidents': recent, 'total': incidents.count(), 'status_counts': status_counts,
               'severity_counts': severity_counts, 'chart_data': json.dumps(chart_rows),
               'start': start.isoformat() if start else '', 'end': end.isoformat() if end else '',
               'form': IncidentForm(), 'is_admin': request.user.is_staff}
    return render(request, 'DHT/incidents_dashboard.html', context)


@login_required
def incident_create(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.summary = generate_summary(incident.description)
            incident.save()
            messages.success(request, f'Incident INC-{incident.id} créé.')
            return redirect('incident-detail', pk=incident.pk)
    else: form = IncidentForm()
    return render(request, 'DHT/incident_form.html', {'form': form, 'heading': 'Créer un incident'})


@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    comment_form = CommentForm()
    if request.method == 'POST' and 'comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.incident = incident
            comment.author = request.user
            comment.save()
            messages.success(request, 'Commentaire ajouté.')
            return redirect('incident-detail', pk=pk)
    has_receipt = incident.receipts.filter(operator=request.user).exists()
    return render(request, 'DHT/incident_detail.html', {'incident': incident, 'comment_form': comment_form,
                 'has_receipt': has_receipt, 'is_admin': request.user.is_staff})


@login_required
@require_POST
def acknowledge_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk, is_archived=False)
    IncidentReceipt.objects.get_or_create(incident=incident, operator=request.user)
    if incident.status == 'new':
        incident.status = 'acknowledged'
        incident.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'Accusé de réception enregistré.')
    return redirect('incident-detail', pk=pk)


@login_required
@require_POST
def update_status(request, pk):
    incident = get_object_or_404(Incident, pk=pk, is_archived=False)
    new_status = request.POST.get('status')
    if new_status in dict(Incident.STATUS_CHOICES):
        incident.status = new_status
        incident.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Statut mis à jour.')
    return redirect('incident-detail', pk=pk)


@login_required
@require_POST
def archive_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    incident.is_archived = True
    incident.archived_at = timezone.now()
    incident.save(update_fields=['is_archived', 'archived_at', 'updated_at'])
    messages.success(request, 'Incident archivé.')
    return redirect('incident-archives')


@login_required
def archives(request):
    queryset, start, end = _filter_dates(Incident.objects.filter(is_archived=True), request)
    return render(request, 'DHT/incident_archives.html', {'incidents': queryset.select_related('assigned_to', 'created_by'),
                 'start': start.isoformat() if start else '', 'end': end.isoformat() if end else ''})


@admin_required
def operators(request):
    if request.method == 'POST':
        form = OperatorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte opérateur créé avec succès.')
            return redirect('operators')
    else: form = OperatorForm()
    users = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    return render(request, 'DHT/operators.html', {'form': form, 'operators': users})


@admin_required
def operator_toggle(request, pk):
    if request.method != 'POST': return redirect('operators')
    user = get_object_or_404(User, pk=pk, is_staff=False, is_superuser=False)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    messages.success(request, 'Compte opérateur mis à jour.')
    return redirect('operators')


def generate_summary(description):
    """Résumé extractif local (sans API IA): limite les espaces et extrait les premières phrases utiles."""
    text = ' '.join((description or '').strip().split())
    if not text: return 'Aucune description disponible.'
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    summary = '. '.join(sentences[:2])
    if len(summary) > 300: summary = summary[:297].rstrip() + '...'
    return summary + ('.' if summary and not summary.endswith(('.', '!', '?')) else '')


@login_required
def summary_api(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    return JsonResponse({'summary': incident.summary or generate_summary(incident.description)})

# Page de monitoring DHT11 d'origine, conservée séparément du portail incidents.
import os
from django.http import HttpResponse, FileResponse

def test(request):
    return HttpResponse('Je suis Zakaria')

def sensor_dashboard(request):
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'DHT', 'dashboard.html')
    return FileResponse(open(file_path, 'rb'), content_type='text/html')

@admin_required
def operator_edit(request, pk):
    operator = get_object_or_404(User, pk=pk, is_staff=False, is_superuser=False)
    if request.method == 'POST':
        form = OperatorEditForm(request.POST, instance=operator)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte opérateur modifié.')
            return redirect('operators')
    else:
        form = OperatorEditForm(instance=operator)
    return render(request, 'DHT/operator_edit.html', {'form': form, 'operator': operator})
