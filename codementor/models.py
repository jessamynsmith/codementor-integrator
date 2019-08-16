import datetime
import pytz

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials, _GOOGLE_OAUTH2_TOKEN_ENDPOINT
from allauth.socialaccount.models import SocialToken


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codementor_api_key = models.CharField(max_length=20)
    
    def __str__(self):
        return 'Profile for {}'.format(self.user)


# TODO Create a model with session data that keeps track of what state the session is in
# Add a field for the google calendar event id


class CodementorWebhook(models.Model):
    event_name = models.CharField(max_length=40)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO How to know what user the data is for? Maybe require everyone to add a url
    # parameter of their email? # Or will verifying take care of that?

    def get_appointment_time(self):
        appt_time = ''
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


def add_calendar_event(sender, instance=None, created=False, **kwargs):
    data = instance.data

    user = get_user_model().objects.get(email=settings.ADMIN_EMAIL)
    social_token = SocialToken.objects.filter(account__user=user).first()
    creds = Credentials(social_token.token, refresh_token=social_token.token_secret,
                        token_uri=_GOOGLE_OAUTH2_TOKEN_ENDPOINT,
                        client_id=social_token.app.client_id,
                        client_secret=social_token.app.secret)

    service = build('calendar', 'v3', credentials=creds)
    
    """
    Event Name	Description
    scheduled_session.created	When a scheduled session is created
    scheduled_session.confirmed	When a scheduled session is confirmed
    scheduled_session.cancelled	When a scheduled session is cancelled
    scheduled_session.declined	When a scheduled session is declined
    scheduled_session.rescheduled	When a scheduled session is rescheduled
    """

    if instance.event_name == "scheduled_session.confirmed":
        appt_time = instance.get_appointment_time()
        end_time = appt_time + datetime.timedelta(hours=1)
        event_data = {
            'summary': '{} scheduled session'.format(data['mentee']['name']),
            'description': data['schedule_url'],
            'start': {
                'dateTime': appt_time.isoformat(),
                'timeZone': settings.CALENDAR_TIME_ZONE,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': settings.CALENDAR_TIME_ZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = service.events().insert(calendarId='primary', body=event_data).execute()
        print('created event', event)


def add_user_profile(sender, instance=None, created=False, **kwargs):
    if instance and not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)


models.signals.post_save.connect(add_calendar_event, CodementorWebhook)
models.signals.post_save.connect(add_user_profile, get_user_model())
