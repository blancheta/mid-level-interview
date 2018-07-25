import datetime
from unittest import TestCase
import pytz
from monitoring.models import User, Contact, Server, Login


class TestsUserModel(TestCase):

    """
    Tests User Model
    """

    def test_can_create_a_user(self):

        """
        Can create a user with a username and a fullname
        """

        user = User.objects.create(
            username="terry",
            fullname="Terry"
        )

        self.assertIsInstance(user, User)


class TestsContactModel(TestCase):

    """
    Tests Contact Model
    """

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username="terrot",
            fullname="Terro T"
        )

    def test_can_create_a_contact(self):

        """
        Can create a contact with an identifier, a user, and a contact type
        """

        contact = Contact.objects.create(
            identifier="alalal@ooo.fr",
            type="email",
            user=self.user
        )

        self.assertIsInstance(contact, Contact)

    def test_can_get_contacts_for_a_user(self):

        """
        Test can get contact for a user
        """

        self.assertEqual(self.user.contact_set.count(), 1)



class TestsServerModel(TestCase):

    """
    Tests Server Model
    """

    def test_can_create_a_server(self):

        """
        Can create a server with a name and an ip
        """

        Server.objects.create(
            name="bravo",
            ip="192.168.1.1",
        )


class TestsLoginModel(TestCase):

    """
    Tests Login Model
    """

    def test_can_create_a_login(self):

        """
        Can create a login with a login time, a user and a server
        """

        user = User.objects.create(
            username="terra",
            fullname="Terra"
        )

        server = Server.objects.create(
            name="bravo",
            ip="192.168.1.1",
        )

        time = datetime.datetime.today().replace(tzinfo=pytz.utc)
        Login.objects.create(
            user=user,
            server=server,
            time=time
        )
