from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import IssueCommentForm, IssueForm, IssueStatusForm
from .models import Issue, IssueComment


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = IssueCommentForm()
        context["comments"] = self.object.comments.select_related("author").all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = IssueCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
        return redirect("issues:detail", pk=self.object.pk)


class IssueUpdateView(LoginRequiredMixin, UpdateView):
    model = Issue
    form_class = IssueStatusForm
    template_name = "issues/issue_update.html"

    def get_success_url(self):
        messages.success(self.request, f"Issue {self.object.reference_no} updated.")
        return reverse_lazy("issues:detail", kwargs={"pk": self.object.pk})


class IssueDeleteView(LoginRequiredMixin, DeleteView):
    model = Issue
    template_name = "issues/issue_confirm_delete.html"
    context_object_name = "issue"
    success_url = reverse_lazy("issues:list")

    def form_valid(self, form):
        messages.success(self.request, f"Issue {self.object.reference_no} has been deleted.")
        return super().form_valid(form)


class IssueCommentDeleteView(LoginRequiredMixin, DeleteView):
    model = IssueComment

    def get_success_url(self):
        return reverse_lazy("issues:detail", kwargs={"pk": self.object.issue.pk})

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
