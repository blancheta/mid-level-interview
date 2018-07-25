from django.db import models


class User(models.Model):

    """
    User Model
    """

    username = models.CharField(max_length=40, unique=True)
    fullname = models.CharField(max_length=100)


class Contact(models.Model):

    """
    Contact Model
    """

    EMAIL = "email"
    PHONE = "phone"

    TYPE_CHOICES = (
        (EMAIL, "Email"),
        (PHONE, "Phone")
    )

    identifier = models.CharField(max_length=50)
    type = models.CharField(max_length=5, choices=TYPE_CHOICES, default=PHONE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Server(models.Model):

    """
    Server Model
    """

    name = models.CharField(max_length=30, unique=True)
    ip = models.CharField(max_length=15, unique=True)


class Login(models.Model):

    """
    Login Model
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    time = models.DateTimeField()



