from rest_framework import viewsets

from wafer.kv.models import KeyValue
from wafer.kv.serializers import KeyValueSerializer
from wafer.kv.permissions import KeyValueGroupPermission

class KeyValueViewSet(viewsets.ModelViewSet):
    """API endpoint that allows key-value pairs to be viewed or edited."""
    queryset = KeyValue.objects.all()  # Needed for the REST Permissions
    serializer_class = KeyValueSerializer
    permission_classes = (KeyValueGroupPermission, )

    def get_queryset(self):
        # Space for future expansion
        return super(KeyValueViewSet, self).get_queryset()
