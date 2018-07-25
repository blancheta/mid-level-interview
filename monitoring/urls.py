from django.conf.urls import url
from .views import MonitorListView

urlpatterns = [
    url('', MonitorListView.as_view(), name="monitor")
]