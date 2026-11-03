
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Dht11
from .serializers import DHT11serialize


# API GET : récupérer toutes les mesures
@api_view(['GET'])
def Dlist(request):

    mesures = Dht11.objects.all().order_by('-dt')

    serializer = DHT11serialize(mesures, many=True)

    return Response(
        {"data": serializer.data},
        status=status.HTTP_200_OK
    )


# API POST : enregistrer une nouvelle mesure
@api_view(['POST'])
def dht_post(request):

    serializer = DHT11serialize(data=request.data)

    if serializer.is_valid():

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
