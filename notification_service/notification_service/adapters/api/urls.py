from django.urls import path, include

from notification_service.adapters.api.views import SendNotificationView


urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', SendNotificationView.as_view())
]