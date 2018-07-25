from django.core.management import BaseCommand
from django.db.utils import IntegrityError
from dateutil.parser import parse
import pandas as pd
import pytz
from monitoring.models import Server, User, Contact, Login


class Command(BaseCommand):

    """
    Import servers, users and login attempts into the database
    """

    # known uncommon date format
    # if uncommon format not in this list, should raise a ValueError
    exception_date_patterns = [
        "[1-9]{1,2}\\\[0-9]{1,2}\\\[0-9]{1,2}",
        "[1-9]{1,2}\|[0-9]{1,2}\|[0-9]{1,2}",
        "[1-9]{1,2}\/[0-9]{1,2}\/[0-9]{1,2}"
    ]

    def add_arguments(self, parser):

        """
        Allow the command to have an argument
        """

        parser.add_argument('file_path')

    def validate(self, s, default_value):

        """
        Return date if date has a correct format
        else default_value
        """

        date = default_value

        try:
            # I can check the date without dateutil
            # can be better
            date = parse(s)
            date.replace(tzinfo=pytz.utc)
        except ValueError:
            print("Incorrect value : {}, default_value set : {}".format(s, default_value))

        return date

    def clean_login_times(self, df):

        """
        Clean login times,
        if login-time has an uncommon format,
        the most used value is used to replace the uncommon login-time
        """

        most_frequent_date = df['login-time'].value_counts().idxmax()

        df['login-time'] = df['login-time'].apply(lambda s: self.validate(s, most_frequent_date))
        df['login-time'] = df['login-time'].apply(lambda x: x.replace(tzinfo=pytz.utc))

        df.rename({'login-time': 'time'}, axis="columns", inplace=True)

        return df

    def clean_logins_file(self, df):

        """
        Clean logins data for the csv file
        """

        # drop nan, empty and duplicate values
        df = df.dropna().drop_duplicates()
        df = df[df['username'] != '']
        df.rename(columns={'server-name': "name", 'server-ip': "ip"}, inplace=True)

        return self.clean_login_times(df)

    def get_user_records(self):

        """
        Get user records
        """

        user_records = pd.DataFrame(list(User.objects.all().defer('fullname').values()))
        user_records.rename(columns={'id': 'user_id'}, inplace=True)

        return user_records[['username', 'user_id']]

    def get_server_records(self):

        """
        Get server records
        """

        server_records = pd.DataFrame(list(Server.objects.values()))
        server_records.rename(columns={'id': 'server_id'}, inplace=True)

        return server_records[['ip', 'server_id']]

    def extract_and_create_servers(self, df):

        """
        Extract servers from dataframe and create its to db
        """

        server_identifiers = df[['ip', 'name']].dropna().drop_duplicates()

        try:
            Server.objects.bulk_create(
                Server(**vals) for vals in server_identifiers.to_dict('records')
            )
        except IntegrityError:
            print("Servers already imported")

        return self.get_server_records()

    def extract_and_create_contacts(self, df):

        """
        Extract and create contacts
        """

        df = df.rename(columns={'contact': 'identifier'})
        df = df[['identifier', 'user_id']]

        # extract phone numbers
        phone_numbers = df[df.identifier.str.contains('^0|\+|\(')]
        phone_numbers = phone_numbers.assign(type='phone')

        # extract emails
        emails = df[df.identifier.str.contains('@')].drop_duplicates()
        emails = emails.assign(type='email')

        contacts = pd.concat([phone_numbers, emails])

        try:
            Contact.objects.bulk_create(
                Contact(**contact) for contact in contacts.to_dict('records')
            )
        except IntegrityError:
            print("Contact already imported")

    def extract_and_create_users(self, df):

        """
        Extract users and create users
        """

        df.rename(columns={'full-name': "fullname"}, inplace=True)

        users = df[['username', 'fullname']]

        df.drop('fullname', axis=1, inplace=True)

        users = users.set_index('username')
        # one row per user
        users = users[~users.index.duplicated(keep='first')].reset_index()

        try:
            User.objects.bulk_create(
                User(**vals) for vals in users.to_dict('records')
            )
        except IntegrityError:
            print("Users already imported")

        return self.get_user_records()

    def create_logins(self, df):

        """
        Create login attempts
        """

        try:
            Login.objects.bulk_create(
                Login(**vals) for vals in df.to_dict('records')
            )
        except:
            print("Logins already imported")

    def prepare_login_data(self, df):

        """
        Prepare data to create login attempts
        """

        df.drop(['username', 'contact', 'name', 'ip'], axis=1, inplace=True)

        return df

    def handle(self, *args, **options):

        """
        Action method of the command
        """

        file_path = options['file_path']

        logins = pd.read_csv(file_path)
        logins = self.clean_logins_file(logins)

        server_records = self.extract_and_create_servers(logins)

        # new column for logins : server_id
        logins = pd.merge(logins, server_records, how='inner', on=['ip'])

        user_records = self.extract_and_create_users(logins)

        # new column for logins : user_id
        logins = pd.merge(logins, user_records, how='inner', on=['username'])

        self.extract_and_create_contacts(logins)

        self.create_logins(self.prepare_login_data(logins))
