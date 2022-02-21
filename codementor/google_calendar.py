from django.conf import settings

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials, _GOOGLE_OAUTH2_TOKEN_ENDPOINT
from allauth.socialaccount.models import SocialToken


class GoogleCalendarService:

    def __init__(self, user):
        social_token = SocialToken.objects.filter(account__user=user).first()
        creds = Credentials(social_token.token, refresh_token=social_token.token_secret,
                            token_uri=_GOOGLE_OAUTH2_TOKEN_ENDPOINT,
                            client_id=social_token.app.client_id,
                            client_secret=social_token.app.secret)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_calendar_list(self):
        calendar_list = self.service.calendarList().list().execute()
        return calendar_list['items']

    def add_calendar_event(self, start_time, end_time, summary, description, calendar_id='primary'):

        event_data = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
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

        event = self.service.events().insert(calendarId=calendar_id, body=event_data).execute()
        print('created event', event)
        return event

    def get_calendar_event(self, event_id, calendar_id='primary'):
        event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        print('created event', event)
        return event
