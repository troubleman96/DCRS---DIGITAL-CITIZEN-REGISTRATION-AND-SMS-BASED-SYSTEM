from django.urls import path

from .views import IssueCreateView, IssueDetailView, IssueListView, IssueUpdateView

app_name = "issues"

urlpatterns = [
    path("", IssueListView.as_view(), name="list"),
    path("submit/", IssueCreateView.as_view(), name="submit"),
    path("<int:pk>/", IssueDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", IssueUpdateView.as_view(), name="update"),
]
