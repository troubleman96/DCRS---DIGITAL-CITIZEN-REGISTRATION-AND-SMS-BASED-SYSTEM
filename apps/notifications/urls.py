from django.urls import path

from .views import BroadcastSMSView, ComposeSMSView, SMSLogListView

app_name = "notifications"

urlpatterns = [
    path("compose/", ComposeSMSView.as_view(), name="compose"),
    path("broadcast/", BroadcastSMSView.as_view(), name="broadcast"),
    path("log/", SMSLogListView.as_view(), name="log"),
]
