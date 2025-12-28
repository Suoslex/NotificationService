from django.urls import path, include

from notification_service.adapters.api.views import SendNotificationView


urlpatterns = [
    path('', SendNotificationView.as_view())
]