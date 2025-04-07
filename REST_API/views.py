from rest_framework import generics
from Superviseur.models import DetectionResult, Cam, Zone, Projet
from .serializers import DetectionResultSerializer, ClientLoginSerializer, CamSerializer, ZoneSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


class DetectionResult(generics.ListAPIView):
    queryset = DetectionResult.objects.all()
    serializer_class = DetectionResultSerializer


@api_view(['GET'])
def get_camera_coordinates(request, cameraName):
    try:
        camera = Cam.objects.get(cam_ID=cameraName)
        serializer = CamSerializer(camera)
        return Response(serializer.data)
    except Cam.DoesNotExist:
        return Response(status=404)


@api_view(['GET'])
def ZoneByProjet(request, cameraName):
    try:
        projet_name = Projet.objects.filter(cam__cam_ID=cameraName).values('name_project').first()['name_project']
        zones = Zone.objects.filter(name_project__name_project=projet_name)
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data)
    except (Projet.DoesNotExist, KeyError):
        return Response(status=status.HTTP_404_NOT_FOUND)


class ClientLoginAPIView(APIView):
    serializer_class = ClientLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        # Create or get token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)

        # Return token in response
        return Response({'token': token.key}, status=status.HTTP_200_OK)