from django.urls import path

from .views import CitizenDetailView, CitizenHomeView, CitizenListView, CitizenPortalView, CitizenRegistrationView, CitizenStatusView

app_name = "citizens"

urlpatterns = [
    path("", CitizenHomeView.as_view(), name="home"),
    path("portal/", CitizenPortalView.as_view(), name="portal"),
    path("register/", CitizenRegistrationView.as_view(), name="register"),
    path("list/", CitizenListView.as_view(), name="list"),
    path("<int:pk>/", CitizenDetailView.as_view(), name="detail"),
    path("<int:pk>/status/", CitizenStatusView.as_view(), name="status"),
]
