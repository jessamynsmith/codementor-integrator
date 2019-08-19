from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework import routers

from codementor import views as cm_views

router = routers.DefaultRouter()
router.register('scheduled_sessions', cm_views.CodementorWebhookViewset)


urlpatterns = [
    path('', RedirectView.as_view(url='accounts/login/', permanent=False)),
    path('api/v1/codementor/', include(router.urls)),
    path('privacy/', cm_views.PrivacyPolicyView.as_view(), name='privacy'),
    path('user/profile/<int:pk>/', cm_views.UserProfileUpdateView.as_view(), name='user_profile'),
    path('calendar/add/', cm_views.AddCalendarEventsView.as_view(), name='add_events_to_calendar'),
    path('sessions/', cm_views.CodementorSessions.as_view(), name='sessions'),
    path('sessions/completed/', cm_views.CodementorCompletedSessions.as_view(), name='completed_sessions'),
]
