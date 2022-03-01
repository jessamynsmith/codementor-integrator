from django.contrib import admin

from codementor import models as codementor_models


class CodementorWebhookAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'created_at')
    list_filter = ('event_name', 'user')
    search_fields = ('event_name', 'user__email', 'user__first_name', 'user__last_name',
                     'data', 'created_at')


class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'client', 'scheduled_start', 'finished_at',
                    'amount_before_platform_fee', 'session_length', 'google_event_id')
    list_filter = ('status', 'client')
    search_fields = ('session_id', 'client__name', 'client__username', 'google_event_id')


admin.site.register(codementor_models.Client)
admin.site.register(codementor_models.CodementorWebhook, CodementorWebhookAdmin)
admin.site.register(codementor_models.Session, SessionAdmin)
admin.site.register(codementor_models.UserProfile)
