import datetime
import pytz

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.utils.timezone import now

from allauth.socialaccount.models import SocialToken

from codementor.google_calendar import GoogleCalendarService


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codementor_api_key = models.CharField(max_length=20, null=True, blank=True)
    codementor_web_secret = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return 'Profile for {}'.format(self.user)


# TODO Create a model with session data that keeps track of what state the session is in
# Add a field for the google calendar event id


class CodementorWebhook(models.Model):
    event_name = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, blank=True)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO add field to indicate session has been successfully saved to google calendar

    def get_appointment_time(self):
        appt_time = now()
        appt_timestamp = self.data.get('appointment_timestamp')
        if appt_timestamp:
            timezone = pytz.timezone(settings.CALENDAR_TIME_ZONE)
            appt_time = datetime.datetime.fromtimestamp(int(appt_timestamp), tz=timezone)
        return appt_time

    def get_mentee_name(self):
        return self.data.get('mentee', {}).get('name', '')

    def __str__(self):
        return '{} - {} - {}'.format(
            self.event_name, self.get_mentee_name(), self.get_appointment_time())


def add_webhook_calendar_event(sender, instance=None, created=False, **kwargs):
    data = instance.data

    """
    Event Name	Description
    scheduled_session.created	When a scheduled session is created
    scheduled_session.confirmed	When a scheduled session is confirmed
    scheduled_session.cancelled	When a scheduled session is cancelled
    scheduled_session.declined	When a scheduled session is declined
    scheduled_session.rescheduled	When a scheduled session is rescheduled
    """
    print('add_webhook_calendar_event', instance.event_name)
    print(instance.data)
    if instance.event_name == "scheduled_session.confirmed":
        start_time = instance.get_appointment_time()
        end_time = start_time + datetime.timedelta(hours=1)
        mentee = data.get('mentee', {})
        summary = f"{mentee.get('name', 'unknown name')} scheduled session"
        description = data.get('schedule_url', 'missing schedule url')

        if instance.user:
            service = GoogleCalendarService(instance.user)
            service.add_calendar_event(start_time, end_time, summary, description)


def add_user_profile(sender, instance=None, created=False, **kwargs):
    if instance and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)


models.signals.post_save.connect(add_webhook_calendar_event, CodementorWebhook)
models.signals.post_save.connect(add_user_profile, get_user_model())
