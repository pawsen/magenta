#!/usr/bin/env python3

from django.utils.timezone import now

from os2datascanner.projects.admin.core.models import Client
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.import_services.models import Realm, LDAPConfig


"""Run with

dsa python ~/git/os2datascanner/src/os2datascanner/projects/admin/manage.py shell_plus
%run create_ldap_config.py
ldap = LDAPConfigTest()
"""

class LDAPConfigTest:
    def __init__(self):
        self.create_client()
        self.create_config()

    def create_client(self):
        # obj: model, created: bool = get_or_create()
        # Any keyword arguments passed to get_or_create() — except an optional
        # one called defaults — will be used in a get() call.
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#get-or-create

        # clients are Kunder in danish
        self.client, _ = Client.objects.get_or_create(
            name="TestClient", contact_email="test@magenta.dk", contact_phone="12345678"
        )
        # set choises, so client can perform all scans and all features
        # equvilent to features = 1 << 0 | 1 << 1 | 1 << 2
        features = 0
        for x in range(3): features |= 1 << x
        self.client.features = features

        scans = 0
        for x in range(9): scans |= 1 << x
        self.client.scans = scans
        self.client.save()

        self.organization, _ = Organization.objects.get_or_create(
            name="TestOrg",
            slug="test_org",
            client=self.client,
        )

        self.realm, _ = Realm.objects.get_or_create(
            realm_id=self.organization.slug,
            organization=self.organization,
            defaults={
                "last_modified": now(),
            },
        )

    def create_config(self):
        self.config, _ = LDAPConfig.objects.get_or_create(
            organization=self.organization,
            vendor="ad",  # or ad?
            username_attribute="cn",
            rdn_attribute="cn",
            uuid_attribute="uidNumber",
            user_obj_classes="inetOrgPerson",
            connection_protocol="ldap://",
            users_dn="ou=jumbo,dc=magenta,dc=test",
            search_scope=2,
            bind_dn="cn=admin,dc=magenta,dc=test",
            defaults={
                # dk network inspect os2datascanner_default | grep -A 4 os2datascanner_ldap_server
                "connection_url":"ldap_server:389",
                "last_modified": now(),
            },
        )
        # password is encrypted
        self.config.ldap_credential = "testMAG"
        self.config.save()
