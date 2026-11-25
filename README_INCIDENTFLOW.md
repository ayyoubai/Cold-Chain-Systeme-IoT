# IncidentFlow – évolution du projet IoT

Cette version ajoute la gestion d'incidents à l'application Django existante, sans retirer l'API ni la page de monitoring DHT11.

## Installation Windows
1. Décompresser le dossier et ouvrir le terminal dans sa racine.
2. `py -m venv .venv`
3. `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. Copier `.env.example` vers `.env`, puis définir une clé `DJANGO_SECRET_KEY`.
6. `python manage.py migrate`
7. Créer deux comptes administrateurs : lancer deux fois `python manage.py createsuperuser`.
8. `python manage.py runserver`
9. Ouvrir `http://127.0.0.1:8000/login/`.

## Pages
- `/` : dashboard IncidentFlow (connexion obligatoire)
- `/incidents/create/` : création incident
- `/archives/` : archives et filtre par dates
- `/operators/` : gestion des comptes opérateurs, réservée aux administrateurs
- `/monitoring/` : page de monitoring DHT11 originale
- `/admin/` : administration Django

Les administrateurs sont les utilisateurs Django `is_staff`/superuser. La page `/operators/` leur permet de créer des comptes opérateurs et de les désactiver/réactiver. Les opérateurs ont des droits standard.

Le résumé de l'incident est actuellement extractif (les premières phrases du descriptif), sans API IA externe.
