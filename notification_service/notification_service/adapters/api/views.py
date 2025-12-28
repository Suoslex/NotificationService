from dataclasses import asdict

from loguru import logger
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response

from notification_service.adapters.api.auth import JWTAuthentication, HasScope
from notification_service.domain.entities import Notification
from notification_service.adapters.api import serializers
from notification_service.application.use_cases.send_notification import (
    SendNotificationUseCase
)
from notification_service.adapters.dependencies import get_unit_of_work


class SendNotificationView(APIView):
    """
    View for sending notifications.

    Handles HTTP POST requests for creating and sending notifications.
    Requires JWT authentication and scope checking.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasScope]
    required_scope = "notifications:send"
    serializer_class = serializers.NotificationSerializer

    # TODO: RateLimit

    def post(self, request: Request) -> Response:
        logger.debug("Received POST request to send notification")
        logger.debug(f"Request data: {request.data}")
        
        notification_data = self.serializer_class(data=request.data)
        notification_data.is_valid(raise_exception=True)
        logger.debug(
            f"Validated notification data: "
            f"{notification_data.validated_data}"
        )
        
        use_case = SendNotificationUseCase(get_unit_of_work())        
        notification = Notification(**notification_data.validated_data)
        logger.debug(
            f"Created notification object with UUID: {notification.uuid}"
        )
        
        accept_status = use_case.execute(notification)
        logger.debug(f"Use case executed, status: {accept_status}")
        
        response_data = asdict(accept_status)
        logger.debug(f"Returning response data: {response_data}")
        
        status_code = 201 if accept_status.was_created else 200
        logger.debug(f"Response status code: {status_code}")
        
        return Response(
            response_data,
            status_code
        )

