from rest_framework import serializers

from rwanda.purchase.models import ServicePurchase, Deliverable, DeliverableFile
from rwanda.service.models import Service, ServiceOption, ServiceCategory


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "__all__"


class ServicePurchaseBaseSerializer(serializers.ModelSerializer):
    has_been_accepted = serializers.BooleanField()
    service_title = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = ServicePurchase
        fields = "__all__"


class PurchaseSerializer(ServicePurchaseBaseSerializer):
    can_be_approved = serializers.BooleanField()
    can_be_canceled = serializers.BooleanField()
    can_be_in_dispute = serializers.BooleanField()


class OrderSerializer(ServicePurchaseBaseSerializer):
    can_be_accepted = serializers.BooleanField()
    can_be_delivered = serializers.BooleanField()


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
