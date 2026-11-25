
from .models import Dht11
from .serializers import DHT11serialize

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings
from django.core.cache import cache

import json
import urllib.request


# ==================================================
# CONFIGURATION DES SEUILS
# ==================================================

TEMP_MAX = 25
HUM_MAX = 70


# ==================================================
# FONCTION : ENVOYER UNE ALERTE TELEGRAM
# ==================================================

def envoyer_telegram(message):

    token = settings.TELEGRAM_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("Telegram : TOKEN ou CHAT_ID manquant")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message
    }

    try:

        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=10) as response:

            resultat = json.loads(response.read().decode("utf-8"))

            if resultat.get("ok"):
                print("Notification Telegram envoyee !")
                return True

            print("Erreur Telegram :", resultat)
            return False

    except Exception as e:

        print("Erreur envoi Telegram :", e)
        return False


# ==================================================
# FONCTION : VERIFIER LES ALERTES
# ==================================================

def verifier_alertes(temperature, humidite):

    # ----------------------------------------------
    # ALERTE TEMPERATURE
    # ----------------------------------------------

    if temperature > TEMP_MAX:

        if not cache.get("alerte_temperature"):

            message = (
                "🚨 ALERTE TEMPERATURE !\n\n"
                f"Temperature actuelle : {temperature} °C\n"
                f"Seuil maximum : {TEMP_MAX} °C\n\n"
                "Attention : temperature elevee detectee !"
            )

            if envoyer_telegram(message):
                cache.set("alerte_temperature", True, timeout=None)

    else:

        # Reinitialiser lorsque la temperature revient normale
        cache.delete("alerte_temperature")


    # ----------------------------------------------
    # ALERTE HUMIDITE
    # ----------------------------------------------

    if humidite > HUM_MAX:

        if not cache.get("alerte_humidite"):

            message = (
                "🚨 ALERTE HUMIDITE !\n\n"
                f"Humidite actuelle : {humidite} %\n"
                f"Seuil maximum : {HUM_MAX} %\n\n"
                "Attention : humidite elevee detectee !"
            )

            if envoyer_telegram(message):
                cache.set("alerte_humidite", True, timeout=None)

    else:

        # Reinitialiser lorsque l'humidite revient normale
        cache.delete("alerte_humidite")


# ==================================================
# API GET : RECUPERER TOUTES LES MESURES
# ==================================================

@api_view(['GET'])
def Dlist(request):

    mesures = Dht11.objects.all().order_by('-dt')

    serializer = DHT11serialize(mesures, many=True)

    return Response({
        "data": serializer.data
    })


# ==================================================
# API POST : ENREGISTRER UNE NOUVELLE MESURE
# ==================================================

@api_view(['POST'])
def dht_post(request):

    serializer = DHT11serialize(data=request.data)

    if serializer.is_valid():

        # Enregistrer la mesure dans SQLite
        data = serializer.save()

        temperature = data.temp
        humidite = data.hum

        print("Nouvelle mesure enregistree :")
        print("Temperature :", temperature, "°C")
        print("Humidite :", humidite, "%")

        # Vérifier les seuils et envoyer les alertes
        verifier_alertes(temperature, humidite)

        return Response({
            "message": "Mesure enregistree avec succes",
            "data": DHT11serialize(data).data
        }, status=201)

    return Response(serializer.errors, status=400)
