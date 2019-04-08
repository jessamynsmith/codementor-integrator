from rest_framework.serializers import ModelSerializer

from codementor import models as cm_models


class CodementorWebhookSerializer(ModelSerializer):
    class Meta:
        model = cm_models.CodementorWebhook
        fields = ['event_name', 'data']
