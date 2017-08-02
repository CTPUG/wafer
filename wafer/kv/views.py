from rest_framework import viewsets

from wafer.kv.models import KeyValue
from wafer.kv.serializers import KeyValueSerializer
from wafer.kv.permissions import KeyValueGroupPermission
from wafer.utils import order_results_by


class KeyValueViewSet(viewsets.ModelViewSet):
    """API endpoint that allows key-value pairs to be viewed or edited."""
    queryset = KeyValue.objects.none()  # Needed for the REST Permissions
    serializer_class = KeyValueSerializer
    permission_classes = (KeyValueGroupPermission, )

    @order_results_by('key', 'id')
    def get_queryset(self):
        # Restrict the list to only those that match the user's
        # groups
        if self.request.user.id is not None:
            grp_ids = [x.id for x in self.request.user.groups.all()]
            return KeyValue.objects.filter(group_id__in=grp_ids)
        return KeyValue.objects.none()
