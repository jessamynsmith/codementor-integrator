import base64
import hashlib
import hmac

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView, TemplateView, UpdateView
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.response import Response
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
    fields = ['codementor_api_key', 'codementor_web_secret']
    success_url = reverse_lazy('sessions')


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

    def create(self, request, *args, **kwargs):
        email = self.request.query_params.get('email')
        user = get_user_model().objects.get(email=email)
        if user and hasattr(user, 'userprofile') and user.userprofile.codementor_web_secret:
            signature_header = request.META.get('HTTP_X_CM_SIGNATURE')
            print('signature_header', signature_header)
            digest = hmac.new(
                user.userprofile.codementor_web_secret.encode(),
                msg=request.stream.body,
                digestmod=hashlib.sha256).digest()
            calculated_signature = base64.b64encode(digest).decode()
            print('calculated_signature', calculated_signature)
            print('request.stream.body', request.stream.body)
            if signature_header == calculated_signature:
                print('equal!')
            return super().create(request, *args, **kwargs)

        # Return 200 to keep Codementor happy
        return Response({}, status=status.HTTP_200_OK)

        """
        Each webhook event will include a header called X-Cm-Signature. It's a HMAC hex 
        digest of the response body generated using the sha256 hash function and the
        CODEMENTOR_WEB_SECRET as the HMAC key. You can generate the signature from the 
        payload and compare it with X-Cm-Signature to make sure the request is sent from Codementor.
        
        import hmac
        import hashlib
        import base64
        
        digest = hmac.new(secret, msg=thing_to_hash, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        """

    def perform_create(self, serializer):
        email = self.request.query_params.get('email')
        serializer.save(email=email)
