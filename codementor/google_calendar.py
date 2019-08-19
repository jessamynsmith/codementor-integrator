from django.conf import settings
from django.contrib.auth import get_user_model

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials, _GOOGLE_OAUTH2_TOKEN_ENDPOINT
from allauth.socialaccount.models import SocialToken


def add_calendar_event(user, start_time, end_time, summary, description):
    social_token = SocialToken.objects.filter(account__user=user).first()
    creds = Credentials(social_token.token, refresh_token=social_token.token_secret,
                        token_uri=_GOOGLE_OAUTH2_TOKEN_ENDPOINT,
                        client_id=social_token.app.client_id,
                        client_secret=social_token.app.secret)

    service = build('calendar', 'v3', credentials=creds)

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

    event = service.events().insert(calendarId='primary', body=event_data).execute()
    print('created event', event)
