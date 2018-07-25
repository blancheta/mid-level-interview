from django.test import TestCase
from django.shortcuts import reverse
from monitoring.models import Server


class MonitoringViewTests(TestCase):

    """
    Tests the monitoring view
    """

    def setUp(self):

        Server.objects.create(
            name='alpha',
            ip='213.4.0.1'
        )

    def test_can_return_a_list_of_servers(self):
        """
        Test can return a list of servers
        """

        server_count = Server.objects.count()

        response = self.client.get(reverse('monitor'))
        self.assertEqual(server_count, len(response.context['servers']))
