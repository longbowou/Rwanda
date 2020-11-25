from rest_framework import serializers

from rwanda.account.models import Refund, RefundWay
from rwanda.administration.models import Parameter
from rwanda.purchase.models import ServicePurchase, Deliverable, DeliverableFile
from rwanda.service.models import Service, ServiceOption
from rwanda.user.models import User


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


class ServiceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOption
        fields = "__all__"


class RefundSerializer(serializers.ModelSerializer):
    can_be_processed = serializers.BooleanField()

    class Meta:
        model = Refund
        fields = "__all__"


class RefundWaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundWay
        fields = "__all__"


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
