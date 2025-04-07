from rest_framework import serializers
from Superviseur.models import DetectionResult, Cam, Zone
from django.contrib.auth import authenticate


class DetectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionResult
        fields = '__all__'


class CamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cam
        fields = ['coords_cam']



class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['coords_polys']



class ClientLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user:
                # If user is authenticated, return user object
                attrs['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        return attrs
