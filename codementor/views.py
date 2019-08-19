from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView, TemplateView, UpdateView
from django.urls import reverse_lazy
from rest_framework.viewsets import ModelViewSet

from codementor import forms as cm_forms
from codementor import models as cm_models
from codementor import serializers as cm_serializers
from codementor.codementor_api import CodementorApi
from codementor.google_calendar import GoogleCalendarService


class PrivacyPolicyView(TemplateView):

    template_name = 'codementor/privacy_policy.html'


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):

    template_name = 'codementor/user_profile.html'
    model = cm_models.UserProfile
    fields = ['codementor_api_key']


class AddCalendarEventsView(LoginRequiredMixin, FormView):

    template_name = 'codementor/add_calendar_events.html'
    form_class = cm_forms.ScheduleDataForm
    success_url = reverse_lazy('sessions')

    def dispatch(self, request, *args, **kwargs):
        self.service = GoogleCalendarService(self.request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['calendars'] = self.service.get_calendar_list()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        schedule_data = form.cleaned_data['schedule_data']
        for item in schedule_data:
            start_time = item[0]
            end_time = item[1]
            summary = form.cleaned_data['summary']
            description = form.cleaned_data['description']
            calendar_id = form.cleaned_data['calendar']
            self.service.add_calendar_event(start_time, end_time, summary,
                                            description, calendar_id=calendar_id)
        return response


class CodementorCompletedSessions(LoginRequiredMixin, TemplateView):

    template_name = 'codementor/scheduled_sessions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        codementor_api = CodementorApi()
        completed_session_data = codementor_api.get_completed_sessions(self.request.user)
        context['object_list'] = completed_session_data['data']
        return context


class CodementorSessions(LoginRequiredMixin, ListView):

    template_name = 'codementor/sessions.html'
    model = cm_models.CodementorWebhook

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(event_name="scheduled_session.created")
        queryset = queryset.order_by('-created_at')
        return queryset


class CodementorWebhookViewset(ModelViewSet):
    queryset = cm_models.CodementorWebhook.objects.all()
    serializer_class = cm_serializers.CodementorWebhookSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        print('creating', self.request.data)
        return super().perform_create(serializer)


    """
    TODO: verify signature
    TODO: can this somehow be used to verify whose account is associated with this webhook call?
    
    For security reasons, you shouldn't trust incoming events your webhook URL receives. 
    You should verify signatures to ensure the event was sent from Codementor.

    Each webhook event will include a header called X-Cm-Signature. It's a HMAC hex 
    digest of the response body generated using the sha256 hash function and the
    CODEMENTOR_WEB_SECRET as the HMAC key. You can generate the signature from the 
    payload and compare it with X-Cm-Signature to make sure the request is sent from Codementor.
    """

    """
    {
      "event_name": "scheduled_session.confirmed",
      "data": {
        "id": "52nbekb9ca",
        "confirmed_at": 1538019834,
        "appointment_timestamp": 1538150400,
        "mentee": {
          "username": "mentee-username",
          "name": "mentee-name"
        },
        "schedule_url": "https://www.codementor.io/m/dashboard/my-schedules/52nbekb9ca"
      }
    }
    """
