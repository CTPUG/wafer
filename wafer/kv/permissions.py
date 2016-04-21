from rest_framework.permissions import BasePermission

class KeyValueGroupPermission(BasePermission):
    """Restrict access to a given key / value pair to members of the
       corresponding group."""

    # We perhaps unwisely assume that the view set checks ensure we
    # aren't exposing other groups key-value combinations, so
    # we only need to provide the object permission check

    def has_object_permission(self, request, view, obj):
        # Only allow any sort of access if the user is a member of
        # the appropriate group
        group = obj.group
        user = request.user
        if user.groups.filter(name=group.name).exists():
            if request.method in ['PUT', 'PATCH']:
                # XXX: Better ideas here?
                if 'group' in request.data and obj.group.pk != int(request.data['group']):
                    self.message = "Cannot change the group owning this KeyValue pair"
                    return False
            return True
        return False
