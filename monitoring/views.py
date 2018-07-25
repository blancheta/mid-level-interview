from .models import Server
from django.views.generic.list import ListView


class MonitorListView(ListView):

    """
    Return a list of servers
    """

    model = Server
    queryset = Server.objects.all()
    context_object_name = 'servers'
    template_name = 'monitoring/monitor.html'
