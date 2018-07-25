from monitoring.models import Server
from .helper import FunctionalTest


class TestsMonitoring(FunctionalTest):

    """
    Tests Monitoring view
    """

    def setUp(self):
        super().setUp()

        Server.objects.create(
            ip="100.100.100.100",
            name='alpha'
        )

    def test_can_display_details_for_a_list_of_servers(self):

        init_server_count = Server.objects.count()

        self.browser.get(self.server_url)

        servers = self.browser.find_elements_by_class_name('server')

        self.assertEqual(init_server_count, len(servers))
