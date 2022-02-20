from django.contrib import admin

from codementor import models as codementor_models


class CodementorWebhookAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'created_at')
    list_filter = ('event_name', 'user')
    search_fields = ('event_name', 'user__email', 'user__first_name', 'user__last_name',
                     'data', 'created_at')


admin.site.register(codementor_models.CodementorWebhook, CodementorWebhookAdmin)
admin.site.register(codementor_models.UserProfile)
