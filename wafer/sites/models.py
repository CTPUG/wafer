from django.db.models import *
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site

BaseModel = Model

class Model(BaseModel):
    site = ForeignKey(Site, on_delete=CASCADE, default=1, related_name='+', editable=False)
    objects = CurrentSiteManager()

    def save(self, *args, **kwargs):
        self.site = Site.objects.get_current()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
