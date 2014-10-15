from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class TicketType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Ticket(models.Model):
    barcode = models.IntegerField(primary_key=True)
    email = models.EmailField(blank=True)
    type = models.ForeignKey(TicketType)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ticket',
                             blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return u'%s (%s)' % (self.barcode, self.email)
