from rest_framework import serializers
from .models import Joriro


class JoriroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joriro
        fields = "__all__"
