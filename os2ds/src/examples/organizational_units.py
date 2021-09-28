#!/usr/bin/env python3
#
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from os2datascanner.projects.admin.adminapp.models.authentication_model import (
    Authentication,
)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.exchangescanner_model import (
    ExchangeScanner,
)
from os2datascanner.projects.admin.adminapp.views.exchangescanner_views import (
    ExchangeScannerCreate,
)
from os2datascanner.projects.admin.core.models import Administrator
from os2datascanner.projects.admin.core.models.client import Client
from os2datascanner.projects.admin.organizations.models import (
    OrganizationalUnit,
    Account,
    Alias,
)
from os2datascanner.projects.admin.organizations.models.aliases import AliasType
from os2datascanner.projects.admin.organizations.models.organization import Organization

client1 = Client.objects.create(
    name="client1",
)
magenta_org = Organization.objects.create(
    name="Magenta ApS",
    uuid="5d02dfd3-b31c-4076-b2d5-4e41d3442952",
    slug=slugify("Magenta ApS"),
    client=client1,
)

# create OUs, Accounts, Aliases
hirachys = [
    {
        "ou": "ou0",
        "ouid": "",
        "ou_parent": None,
        "aou": "aou0",
        "aid": "",
        "org": magenta_org,
        "email": True,
        "alias_id": "",
    },
]

ous = {}
accounts = {}
aliases = {}
def run():
    for h in hirachys:
        # create OUs
        ou = OrganizationalUnit.objects.create(
            name=f"Test {h['ou']}",
            uuid=h["ouid"],
            parent=ous.get(h["ou_parent"]),
            organization=h["org"],
        )

        # create accounts/konti
        account = Account.objects.create(
            uuid=h["aid"],
            username=h["aou"],
            first_name=f"f {h['aou']}",
            last_name=f"l {h['aou']}",
        )

        # create email-alias for account
        if h.get("email", False):
            alias = Alias.objects.create(
                uuid=h["alias_id"],
                account=account,
                alias_type=AliasType.EMAIL,
                value=f"{h['aou']}@{str(h['org'])}.dk",
            )
            aliases[h["aou"]] = alias

        # connect Account to OU, through implicit model.Position which is created
        # when we do account.units.add(OU)
        account.units.add(ou)

        # save stuff in dict
        ous[h["ou"]] = ou
        accounts[h["aou"]] = account


    scanner_auth_obj = Authentication.objects.create(
        username="ImExchangeAdmin",
        domain="ThisIsMyExchangeDomain",
    )

    exchange_scan = ExchangeScanner.objects.create(
        pk=3,
        name="This is an Exchange Scanner",
        organization=magenta_org,
        validation_status=ExchangeScanner.VALID,
        userlist='path/to/nothing.csv',
        service_endpoint="exchangeendpoint",
        authentication=scanner_auth_obj,
    )
    exchange_scan.org_unit.set(
        list(ous.values())
    )


# class ExchangeScannerViewsTest(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         client1 = Client.objects.create(name="client1")
#         test_org = Organization.objects.create(
#             name="Test",
#             uuid="bddb5188-1240-4733-8700-b57ba6228850",
#             slug=slugify("Test"),
#             client=client1,
#         )

#         """naming of OUs:
#         ou010: child of ou01, which is child of ou0, sister of ou00
#         """
#         test_ou0 = OrganizationalUnit.objects.create(
#             name="Test OU0",
#             uuid="466c3f4e-3f64-4c9b-b6ae-26726721a28f",
#             organization=test_org,
#         )

#         test_ou00 = OrganizationalUnit.objects.create(
#             name="Test OU00",
#             uuid="d063b582-fcd5-4a36-a99a-7785321de083",
#             parent=test_ou0,
#             organization=test_org,
#         )

#         test_ou01 = OrganizationalUnit.objects.create(
#             name="Test OU01",
#             uuid="d049756e-69ca-4056-90e1-3c91f4039754",
#             parent=test_ou0,
#             organization=test_org,
#         )

#         test_ou000 = OrganizationalUnit.objects.create(
#             name="Test OU000",
#             uuid="6e9f741f-5a78-49fe-ad93-501ec0749d5a",
#             parent=test_ou00,
#             organization=test_org,
#         )

#         test_ou1 = OrganizationalUnit.objects.create(
#             name="Test OU1",
#             uuid="3fceb4de-7c6a-4f0c-a5a8-1ad38a9bdc67",
#             organization=test_org,
#         )

#         test_ou10 = OrganizationalUnit.objects.create(
#             name="Test OU10",
#             uuid="5c75f0cb-deed-4c3e-8a3d-b1ea96f2f0a4",
#             parent=test_ou1,
#             organization=test_org,
#         )

#         """
#         Accounts (da: konti). These are the actual users that get scanned if they
#         have a associated email Alias.
#         They are connected to OUs through a model.Position, which is implicit
#         created when we do account.units.add(OU)
#         """
#         aou0 = Account.objects.create(
#             uuid="c638f530-184d-4846-af5e-9175c8ffd7dd",
#             username="aou0",
#             first_name="aou0",
#             last_name="aou0",
#             organization=test_org,
#         )

#         aou001 = Account.objects.create(
#             uuid="3b5b82ee-1b3d-4cbe-bfad-947a424ce40d",
#             username="aou001",
#             first_name="aou001",
#             last_name="aou001",
#             organization=test_org,
#         )

#         aou002 = Account.objects.create(
#             uuid="d0f93080-e0a7-4f84-bdd3-8449dbb9f0d3",
#             username="aou002",
#             first_name="aou002",
#             last_name="aou002",
#             organization=test_org,
#         )

#         aou10 = Account.objects.create(
#             uuid="e3f083f5-81d8-4bab-b21c-abc68eef25a5",
#             username="aou10",
#             first_name="aou10",
#             last_name="aou10",
#             organization=test_org,
#         )

#         Alias.objects.create(
#             uuid="",
#             account=aou0,
#             alias_type=AliasType.EMAIL,
#             value='aou0@testorg.dk',
#         )

#         scanner_auth_obj = Authentication.objects.create(
#             username="ImExchangeAdmin",
#             domain="ThisIsMyExchangeDomain",
#         )

#         exchange_scan = ExchangeScanner.objects.create(
#             pk=2,
#             name="This is an Exchange Scanner",
#             organization=test_org,
#             validation_status=ExchangeScanner.VALID,
#             userlist='path/to/nothing.csv',
#             service_endpoint="exchangeendpoint",
#             authentication=scanner_auth_obj,
#         )
#         exchange_scan.org_unit.set([test_ou0, test_ou00, test_ou000, test_ou1 ])

#         aou0.units.add(test_ou0)

#     def test_ou_accounts(self):
#         """ Test that amount of sources yielded correspond to amount
#         of users with email aliases"""
#         exchange_scanner_obj = ExchangeScanner.objects.get(pk=2)
#         exchange_scanner_obj.authentication.set_password("password")


#         exchange_scanner_source = exchange_scanner_obj.generate_sources()
#         sources_yielded = 0
#         for _ in exchange_scanner_source:
#             sources_yielded += 1

#         self.assertEqual(sources_yielded, 2)
