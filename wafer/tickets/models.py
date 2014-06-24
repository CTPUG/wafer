from django.contrib.auth.models import User
from django.db import models


class TicketType(models.Model):
    name = models.CharField(max_length=32)


class Ticket(models.Model):
    barcode = models.IntegerField(primary_key=True)
    type = models.ForeignKey(TicketType)
    user = models.ForeignKey(User, related_name='ticket',
                             blank=True, null=True, on_delete=models.SET_NULL)
