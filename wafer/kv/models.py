from django.contrib.auth.models import Group
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from jsonfield import JSONField


@python_2_unicode_compatible
class KeyValue(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, db_index=True)
    value = JSONField()

    def __str__(self):
        return 'KV(%s, %s, %r)' % (self.group.name, self.key, self.value)
