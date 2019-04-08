from django.urls import include, path
from rest_framework import routers

from codementor import views as cm_views

router = routers.DefaultRouter()
router.register('scheduled_sessions', cm_views.CodementorWebhookViewset)


urlpatterns = [
    path('api/v1/codementor/', include(router.urls)),
]
