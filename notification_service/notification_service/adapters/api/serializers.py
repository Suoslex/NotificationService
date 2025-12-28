from rest_framework import serializers

from notification_service.adapters.db import models


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for notification model.

    Converts notification model to JSON format and vice versa.
    """
    class Meta:
        model = models.NotificationModel
        fields = ["uuid", "user_uuid", "title", "text", "type"]

