from django.urls import path

from .views import (
    IssueCommentDeleteView,
    IssueCreateView,
    IssueDeleteView,
    IssueDetailView,
    IssueListView,
    IssueUpdateView,
)

app_name = "issues"

urlpatterns = [
    path("", IssueListView.as_view(), name="list"),
    path("submit/", IssueCreateView.as_view(), name="submit"),
    path("<int:pk>/", IssueDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", IssueUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", IssueDeleteView.as_view(), name="delete"),
    path("comment/<int:pk>/delete/", IssueCommentDeleteView.as_view(), name="comment_delete"),
]
