from unittest import TestCase
from django.core.management import call_command
from monitoring.models import Server, User, Contact, Login
from servers.settings import BASE_DIR

TEST_FILE_PATH = BASE_DIR + '/data/logins.csv'


class TestsMonitoring(TestCase):

    """
    Tests Monitoring view
    """

    def test_command_import_can_import_servers_from_a_csv(self):

        """
        Test can create servers when executes import command
        """

        initial_server_count = Server.objects.count()
        initial_user_count = User.objects.count()

        call_command('import', TEST_FILE_PATH)

        self.assertGreater(Server.objects.count(), initial_server_count)
        self.assertGreater(User.objects.count(), initial_user_count)
        self.assertGreater(Contact.objects.filter(type='email').count(), 0)
        self.assertGreater(Contact.objects.filter(type='phone').count(), 0)
        self.assertGreater(Login.objects.count(), 0)
