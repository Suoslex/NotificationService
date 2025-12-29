"""Tests for API views."""

from uuid import uuid4

from unittest.mock import Mock, patch
from rest_framework.request import Request
from rest_framework.response import Response
from notification_service.adapters.api.views import SendNotificationView
from notification_service.domain.entities import Notification
from notification_service.domain.enums import (
    NotificationType,
    NotificationStatus,
)
from notification_service.application.dtos.notification_status import (
    NotificationStatusDTO,
)


class TestSendNotificationView:
    """Tests for SendNotificationView."""

    @patch("notification_service.adapters.api.views.get_unit_of_work")
    @patch("notification_service.adapters.api.views.SendNotificationUseCase")
    def test_post_new_notification(self, mock_use_case_class, mock_get_uow):
        """Test POST request to create new notification."""
        mock_uow = Mock()
        mock_get_uow.return_value = mock_uow

        notification_entity = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
        )

        status_dto = NotificationStatusDTO(
            uuid=notification_entity.uuid,
            status=NotificationStatus.PENDING,
            was_created=True,
        )

        mock_use_case = Mock()
        mock_use_case.execute.return_value = status_dto
        mock_use_case_class.return_value = mock_use_case

        request = Mock(spec=Request)
        request.data = {
            "uuid": str(notification_entity.uuid),
            "user_uuid": str(notification_entity.user_uuid),
            "title": notification_entity.title,
            "text": notification_entity.text,
            "type": notification_entity.type,
        }

        view = SendNotificationView()
        response = view.post(request)

        assert isinstance(response, Response)
        assert response.status_code == 201
        assert response.data["uuid"] == notification_entity.uuid
        assert response.data["status"] == NotificationStatus.PENDING
        assert response.data["was_created"] is True
        mock_use_case.execute.assert_called_once()

    @patch("notification_service.adapters.api.views.get_unit_of_work")
    @patch("notification_service.adapters.api.views.SendNotificationUseCase")
    def test_post_existing_notification(
        self, mock_use_case_class, mock_get_uow
    ):
        """Test POST request for existing notification."""
        mock_uow = Mock()
        mock_get_uow.return_value = mock_uow

        notification_entity = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=NotificationType.EMAIL,
        )

        status_dto = NotificationStatusDTO(
            uuid=notification_entity.uuid,
            status=NotificationStatus.SENT,
            was_created=False,
        )

        mock_use_case = Mock()
        mock_use_case.execute.return_value = status_dto
        mock_use_case_class.return_value = mock_use_case

        request = Mock(spec=Request)
        request.data = {
            "uuid": str(notification_entity.uuid),
            "user_uuid": str(notification_entity.user_uuid),
            "title": notification_entity.title,
            "text": notification_entity.text,
            "type": notification_entity.type,
        }

        view = SendNotificationView()
        response = view.post(request)

        assert isinstance(response, Response)
        assert response.status_code == 200
        assert response.data["was_created"] is False
        mock_use_case.execute.assert_called_once()

    @patch("notification_service.adapters.api.views.get_unit_of_work")
    @patch("notification_service.adapters.api.views.SendNotificationUseCase")
    def test_post_without_type(self, mock_use_case_class, mock_get_uow):
        """Test POST request without notification type."""
        mock_uow = Mock()
        mock_get_uow.return_value = mock_uow

        notification_entity = Notification(
            uuid=uuid4(),
            user_uuid=uuid4(),
            title="Test Title",
            text="Test Text",
            type=None,
        )

        status_dto = NotificationStatusDTO(
            uuid=notification_entity.uuid,
            status=NotificationStatus.PENDING,
            was_created=True,
        )

        mock_use_case = Mock()
        mock_use_case.execute.return_value = status_dto
        mock_use_case_class.return_value = mock_use_case

        request = Mock(spec=Request)
        request.data = {
            "uuid": str(notification_entity.uuid),
            "user_uuid": str(notification_entity.user_uuid),
            "title": notification_entity.title,
            "text": notification_entity.text,
        }

        view = SendNotificationView()
        response = view.post(request)

        assert isinstance(response, Response)
        assert response.status_code == 201
        mock_use_case.execute.assert_called_once()
