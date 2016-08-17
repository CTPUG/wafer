from django.contrib.auth.models import Group
from django.db import models

from jsonfield import JSONField


class KeyValue(models.Model):
    group = models.ForeignKey(Group)
    key = models.CharField(max_length=64, db_index=True)
    value = JSONField()

    def __unicode__(self):
        return u'KV(%s, %s, %r)' % (self.group.name, self.key, self.value)
