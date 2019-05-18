from rest_framework.viewsets import ModelViewSet

from codementor import models as cm_models
from codementor import serializers as cm_serializers


class CodementorWebhookViewset(ModelViewSet):
    queryset = cm_models.CodementorWebhook.objects.all()
    serializer_class = cm_serializers.CodementorWebhookSerializer
    http_method_names = ['POST']

    def perform_create(self, serializer):
        print('creating', self.request.data)
        return super().perform_create(serializer)


    """
    TODO: verify signature
    TODO: can this somehow be used to verify whose account is associated with this webhook call?
    
    For security reasons, you shouldn't trust incoming events your webhook URL receives. 
    You should verify signatures to ensure the event was sent from Codementor.

    Each webhook event will include a header called X-Cm-Signature. It's a HMAC hex 
    digest of the response body generated using the sha256 hash function and the
    CODEMENTOR_WEB_SECRET as the HMAC key. You can generate the signature from the 
    payload and compare it with X-Cm-Signature to make sure the request is sent from Codementor.
    """

    """
    {
      "event_name": "scheduled_session.confirmed",
      "data": {
        "id": "52nbekb9ca",
        "confirmed_at": 1538019834,
        "appointment_timestamp": 1538150400,
        "mentee": {
          "username": "mentee-username",
          "name": "mentee-name"
        },
        "schedule_url": "https://www.codementor.io/m/dashboard/my-schedules/52nbekb9ca"
      }
    }
    """
