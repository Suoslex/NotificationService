"""Tests for API serializers."""

import pytest
from uuid import uuid4

from notification_service.adapters.api.serializers import (
    NotificationSerializer,
)
from notification_service.adapters.db.models import NotificationModel
from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus,
)


@pytest.mark.django_db
class TestNotificationSerializer:
    """Tests for NotificationSerializer."""

    def test_serializer_validation_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "uuid": str(uuid4()),
            "user_uuid": str(uuid4()),
            "title": "Test Title",
            "text": "Test Text",
            "type": NotificationType.EMAIL,
        }

        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid() is True
        assert serializer.validated_data["title"] == "Test Title"
        assert serializer.validated_data["text"] == "Test Text"
        assert serializer.validated_data["type"] == NotificationType.EMAIL

    def test_serializer_validation_without_type(self):
        """Test serializer without type field."""
        data = {
            "uuid": str(uuid4()),
            "user_uuid": str(uuid4()),
            "title": "Test Title",
            "text": "Test Text",
        }

        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid() is True

    def test_serializer_validation_missing_required_fields(self):
        """Test serializer validation with missing required fields."""
        data = {"uuid": str(uuid4())}

        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid() is False
        assert "user_uuid" in serializer.errors
        assert "title" in serializer.errors
        assert "text" in serializer.errors

    def test_serializer_to_representation(self):
        """Test serializer representation."""
        notification = NotificationModel.objects.create(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
            status=NotificationStatus.PENDING,
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        assert "uuid" in data
        assert "user_uuid" in data
        assert "title" in data
        assert "text" in data
        assert "type" in data
        assert data["title"] == "Test Title"
        assert data["text"] == "Test Text"
