from django.contrib import admin

from codementor import models as codementor_models

admin.site.register(codementor_models.CodementorWebhook)
