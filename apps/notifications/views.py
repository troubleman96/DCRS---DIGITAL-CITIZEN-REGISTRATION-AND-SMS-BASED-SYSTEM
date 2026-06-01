from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from apps.citizens.models import Citizen

from .forms import BroadcastSMSForm, ComposeSMSForm
from .models import SMSLog
from .services import broadcast_sms, send_sms


class ComposeSMSView(LoginRequiredMixin, FormView):
    template_name = "notifications/sms_compose.html"
    form_class = ComposeSMSForm
    success_url = reverse_lazy("notifications:log")

    def form_valid(self, form):
        send_sms(form.cleaned_data["recipient"], form.cleaned_data["message_body"])
        return super().form_valid(form)


class BroadcastSMSView(LoginRequiredMixin, FormView):
    template_name = "notifications/sms_broadcast.html"
    form_class = BroadcastSMSForm
    success_url = reverse_lazy("notifications:log")

    def form_valid(self, form):
        ward_name = form.cleaned_data.get("ward")
        citizens = Citizen.objects.all()
        if ward_name:
            citizens = citizens.filter(ward__name__iexact=ward_name)
        recipients = citizens.values_list("phone_number", flat=True)
        broadcast_sms(recipients, form.cleaned_data["message_body"])
        return super().form_valid(form)


class SMSLogListView(LoginRequiredMixin, ListView):
    model = SMSLog
    template_name = "notifications/sms_log.html"
    paginate_by = 12
    context_object_name = "sms_logs"
