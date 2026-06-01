from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import IssueForm, IssueStatusForm
from .models import Issue


class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = "issues/issue_list.html"
    paginate_by = 10
    context_object_name = "issues"

    def get_queryset(self):
        return Issue.objects.select_related("citizen", "ward", "assigned_officer").all()


class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = "issues/issue_submit.html"
    success_url = reverse_lazy("issues:list")


class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = "issues/issue_detail.html"
    context_object_name = "issue"


class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueStatusForm
    template_name = "issues/issue_update.html"

    def get_success_url(self):
        return reverse_lazy("issues:detail", kwargs={"pk": self.object.pk})
