# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Add some useful default groups"

    option_list = BaseCommand.option_list + tuple([
    ])

    GROUPS = {
        # Permissions are specified as (app, code_name) pairs
        'Page Editors': (
            ('pages', 'add_page'), ('pages', 'delete_page'),
            ('pages', 'change_page'), ('pages', 'add_file'),
            ('pages', 'delete_file'), ('pages', 'change_file'),
        ),
        'Talk Mentors': (
            ('talks', 'change_talk'), ('talks', 'view_all_talks'),
        ),
    }

    def add_wafer_groups(self):
        # This creates the groups we need for page editor and talk mentor
        # roles.
        for wafer_group, permission_list in self.GROUPS.items():
            group, created = Group.objects.all().get_or_create(
                name=wafer_group)
            if not created:
                print('Using existing %s group' % wafer_group)
            for app, perm_code in permission_list:
                try:
                    perm = Permission.objects.filter(
                        codename=perm_code, content_type__app_label=app).get()
                except Permission.DoesNotExist:
                    print('Unable to find permission %s' % perm_code)
                    continue
                except Permission.MultipleObjectsReturned:
                    print('Non-unique permission %s' % perm_code)
                if perm not in group.permissions.all():
                    print('Adding %s to %s' % (perm_code, wafer_group))
                    group.permissions.add(perm)
            group.save()

    def handle(self, *args, **options):
        self.add_wafer_groups()
