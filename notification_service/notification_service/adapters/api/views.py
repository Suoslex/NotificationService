from dataclasses import asdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notification_service.adapters.api.auth import JWTAuthentication, HasScope
from notification_service.domain.entities import Notification
from notification_service.adapters.api import serializers
from notification_service.application.use_cases.send_notification import (
    SendNotificationUseCase
)
from notification_service.adapters.dependencies import get_unit_of_work


class SendNotificationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasScope]
    required_scope = "notifications:send"
    serializer_class = serializers.NotificationSerializer

    def post(self, request):
        notification_data = self.serializer_class(data=request.data)
        notification_data.is_valid(raise_exception=True)
        use_case = SendNotificationUseCase(get_unit_of_work())
        accept_status = use_case.execute(
            Notification(**notification_data.validated_data)
        )
        return Response(
            asdict(accept_status),
            201 if accept_status.was_created else 200
        )

