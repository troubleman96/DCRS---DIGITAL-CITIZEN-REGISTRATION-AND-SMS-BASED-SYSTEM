from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import CitizenEditForm, CitizenRegistrationForm
from .models import Citizen


class CitizenPortalView(LoginRequiredMixin, TemplateView):
    template_name = "citizens/portal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Issue = apps.get_model("issues", "Issue")
        try:
            profile = self.request.user.citizen_profile
        except Citizen.DoesNotExist:
            profile = None
        context["profile"] = profile
        if profile:
            context["my_issues"] = Issue.objects.filter(citizen=profile).order_by("-created_at")[:10]
        else:
            context["my_issues"] = []
        return context


class CitizenHomeView(TemplateView):
    template_name = "citizens/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Issue = apps.get_model("issues", "Issue")
        SMSLog = apps.get_model("notifications", "SMSLog")
        context.update(
            total_citizens=Citizen.objects.count(),
            pending_citizens=Citizen.objects.filter(status=Citizen.Status.PENDING).count(),
            open_issues=Issue.objects.filter(status__in=["OPEN", "IN_PROGRESS", "ESCALATED"]).count(),
            sms_logs=SMSLog.objects.count(),
            recent_citizens=Citizen.objects.select_related("ward", "district").all()[:4],
        )
        return context


class CitizenRegistrationView(CreateView):
    model = Citizen
    form_class = CitizenRegistrationForm
    template_name = "citizens/register.html"
    success_url = reverse_lazy("citizens:list")


class CitizenListView(LoginRequiredMixin, ListView):
    model = Citizen
    template_name = "citizens/citizen_list.html"
    paginate_by = 10
    context_object_name = "citizens"

    def get_queryset(self):
        return Citizen.objects.select_related("region", "district", "ward", "mtaa").all()


class CitizenDetailView(LoginRequiredMixin, DetailView):
    model = Citizen
    template_name = "citizens/citizen_detail.html"
    context_object_name = "citizen"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Issue = apps.get_model("issues", "Issue")
        context["citizen_issues"] = Issue.objects.filter(
            citizen=self.object
        ).select_related("ward", "assigned_officer").order_by("-created_at")[:10]
        return context


class CitizenUpdateView(LoginRequiredMixin, UpdateView):
    model = Citizen
    form_class = CitizenEditForm
    template_name = "citizens/citizen_edit.html"
    context_object_name = "citizen"

    def get_success_url(self):
        messages.success(self.request, f"{self.object.full_name}'s profile has been updated.")
        return reverse_lazy("citizens:detail", kwargs={"pk": self.object.pk})


class CitizenDeleteView(LoginRequiredMixin, DeleteView):
    model = Citizen
    template_name = "citizens/citizen_confirm_delete.html"
    context_object_name = "citizen"
    success_url = reverse_lazy("citizens:list")

    def form_valid(self, form):
        messages.success(self.request, f"Citizen record for {self.object.full_name} has been deleted.")
        return super().form_valid(form)


class CitizenStatusView(LoginRequiredMixin, DetailView):
    model = Citizen
    template_name = "citizens/citizen_status.html"
    context_object_name = "citizen"
