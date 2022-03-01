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

class Client(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.username})"


class Session(models.Model):
    """ Session data retrieved from Codementor """
    session_id = models.CharField(max_length=10, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    scheduled_start = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    amount_before_platform_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    session_length = models.IntegerField(null=True, blank=True)
    CREATED = 'created'
    CONFIRMED = 'confirmed'
    STATUS_CHOICES = (
        (CREATED, 'created'),
        (CONFIRMED, 'confirmed'),
        ('cancelled', 'cancelled'),
        ('declined', 'declined'),
        ('rescheduled', 'rescheduled')
    )
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default=CREATED)
    google_event_id = models.CharField(max_length=26, null=True, blank=True)

    def __str__(self):
        return f"{self.client} - {self.session_id} - {self.scheduled_start} - {self.status}"


def save_session_and_client(record):
    client_info = record.data['mentee']
    client, created = Client.objects.get_or_create(**client_info)
    appointment_timestamp = record.data['appointment_timestamp']
    scheduled_start = datetime.datetime.fromtimestamp(appointment_timestamp, tz=pytz.UTC)
    status = record.event_name.replace('scheduled_session.')
    session, created = Session.objects.get_or_create(session_id=record.data['id'], defaults={
        'client': client, 'status': status, 'google_event_id': record.google_event_id,
        'scheduled_start': scheduled_start})
    return session


class CodementorWebhook(models.Model):
    event_name = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, blank=True)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    # TODO remove this
    google_event_id = models.CharField(max_length=26, null=True, blank=True, default=None)

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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Event Name	Description
        scheduled_session.created	When a scheduled session is created
        scheduled_session.confirmed	When a scheduled session is confirmed
        scheduled_session.cancelled	When a scheduled session is cancelled
        scheduled_session.declined	When a scheduled session is declined
        scheduled_session.rescheduled	When a scheduled session is rescheduled
        """
        print('add_webhook_calendar_event', self.event_name)
        print(self.data)

        self.session = save_session_and_client(self)

        if not self.session.google_event_id and self.event_name == "scheduled_session.confirmed":
            start_time = self.get_appointment_time()
            end_time = start_time + datetime.timedelta(hours=1)
            mentee = self.data.get('mentee', {})
            summary = f"{mentee.get('name', 'unknown name')} scheduled session"
            description = self.data.get('schedule_url', 'missing schedule url')

            if self.user:
                try:
                    service = GoogleCalendarService(self.user)
                    event = service.add_calendar_event(start_time, end_time, summary, description)
                    self.session.google_event_id = event['id']
                    self.session.save()
                except Exception as e:
                    print(e)

        super().save(force_insert, force_update, using, update_fields)


def add_user_profile(sender, instance=None, created=False, **kwargs):
    if instance and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)


models.signals.post_save.connect(add_user_profile, get_user_model())
