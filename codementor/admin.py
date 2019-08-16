from django.contrib import admin

from codementor import models as codementor_models


class CodementorWebhookAdmin(admin.ModelAdmin):
    pass


admin.site.register(codementor_models.CodementorWebhook, CodementorWebhookAdmin)
admin.site.register(codementor_models.UserProfile)
