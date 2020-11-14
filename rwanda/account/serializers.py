from rest_framework import serializers

from rwanda.purchase.models import ServicePurchase, Deliverable, DeliverableFile
from rwanda.service.models import Service, ServiceOption


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServicePurchaseBaseSerializer(serializers.ModelSerializer):
    service_title = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = ServicePurchase
        fields = "__all__"


class PurchaseSerializer(ServicePurchaseBaseSerializer):
    pass


class OrderSerializer(ServicePurchaseBaseSerializer):
    pass

class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = "__all__"


class DeliverableFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverableFile
        fields = "__all__"


class ServiceOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = "__all__"
