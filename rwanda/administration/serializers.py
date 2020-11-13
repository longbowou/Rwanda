from rest_framework import serializers

from rwanda.purchase.models import Litigation
from rwanda.service.models import ServiceCategory


class LitigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Litigation
        fields = "__all__"


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "__all__"
