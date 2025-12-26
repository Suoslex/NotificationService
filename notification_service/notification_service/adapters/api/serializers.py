from rest_framework import serializers

from notification_service.adapters.db import models


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.NotificationModel
        fields = ["uuid", "user_id", "title", "text", "type"]

