"""Additional tests for API views."""

from uuid import uuid4

import pytest
from unittest.mock import Mock, patch
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError

from notification_service.adapters.api.views import SendNotificationView


class TestSendNotificationViewAdditional:
    """Additional tests for SendNotificationView to cover edge cases."""

    @patch("notification_service.adapters.api.views.get_unit_of_work")
    def test_post_validation_error(self, mock_get_uow):
        """Test POST request with validation error."""
        mock_uow = Mock()
        mock_get_uow.return_value = mock_uow

        request = Mock(spec=Request)
        request.data = {
            "uuid": "invalid-uuid",
            "user_uuid": str(uuid4()),
            "title": "Test",
            "text": "Test text",
        }

        view = SendNotificationView()

        with pytest.raises(ValidationError):
            view.post(request)

    @patch("notification_service.adapters.api.views.get_unit_of_work")
    def test_post_missing_required_fields(self, mock_get_uow):
        """Test POST request with missing required fields."""
        mock_uow = Mock()
        mock_get_uow.return_value = mock_uow

        request = Mock(spec=Request)
        request.data = {
            "uuid": str(uuid4())
        }

        view = SendNotificationView()

        with pytest.raises(ValidationError):
            view.post(request)
