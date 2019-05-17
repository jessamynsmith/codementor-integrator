import datetime
import pytz

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials, _GOOGLE_OAUTH2_TOKEN_ENDPOINT
from allauth.socialaccount.models import SocialToken


class CodementorWebhook(models.Model):
    event_name = models.CharField(max_length=40)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO How to know what user the data is for? Maybe require everyone to add a url parameter of their email?

    def __str__(self):
        return '{} ({})'.format(self.event_name, self.created_at)


def add_calendar_event(sender, instance=None, created=False, **kwargs):
    data = instance.data

    user = get_user_model().objects.get(email=settings.ADMIN_EMAIL)
    social_token = SocialToken.objects.filter(account__user=user).first()
    creds = Credentials(social_token.token, refresh_token=social_token.token_secret,
                        token_uri=_GOOGLE_OAUTH2_TOKEN_ENDPOINT,
                        client_id=social_token.app.client_id,
                        client_secret=social_token.app.secret)

    service = build('calendar', 'v3', credentials=creds)

    if instance.event_name == "scheduled_session.confirmed":
        appt_timestamp = data['appointment_timestamp']
        timezone = pytz.timezone(settings.CALENDAR_TIME_ZONE)
        appt_time = datetime.datetime.fromtimestamp(int(appt_timestamp))
        appt_time = timezone.localize(appt_time)
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


models.signals.post_save.connect(add_calendar_event, CodementorWebhook)
