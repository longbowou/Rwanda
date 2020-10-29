from rest_framework import serializers

from rwanda.purchase.models import Litigation


class LitigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Litigation
        fields = "__all__"
