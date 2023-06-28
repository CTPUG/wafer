from django.db import models
from django.conf import settings


class TicketType(models.Model):

    MAX_NAME_LENGTH = 255

    name = models.CharField(max_length=MAX_NAME_LENGTH)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    barcode = models.IntegerField(primary_key=True)
    email = models.EmailField(blank=True)
    type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='ticket',
        blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s (%s)' % (self.barcode, self.email)


def user_is_registered(user):
    """This function assumes that all ticket types are equally valid for
       determining the registration status"""
    return Ticket.objects.filter(user=user).exists()


def get_user_ticket_types(user):
    """This returns the distinct ticket types associaated with a user"""
    return set([x.type for x in Ticket.objects.filter(user=user)])
