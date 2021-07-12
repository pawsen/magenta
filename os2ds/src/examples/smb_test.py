#!/usr/bin/env python3

import logging
from pprint import pformat
from os2datascanner.engine2.model.smbc import SMBCSource
from os2datascanner.engine2.model.core import SourceManager
import smbc

# do initial setup for root logger, before setting the level
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
sm = SourceManager()

def print_handles(s):
    print(f"connecting to url {s.to_url()}")
    print(f"{pformat(s.to_json_object())}")
    for h in s.handles(sm):
        print(h.presentation)

path = "//172.16.20.230/Users/deathstar/documents/os2ds"
s1 = SMBCSource(path, user="deathstar", password="tordenskjold",
                skip_super_hidden=True)
s2 = SMBCSource(path, user="deathstar", password="tordenskjold",
                skip_super_hidden=False)
print_handles(s1)
# print_handles(s2)

def auth_handler(server, share, workgroup, username, password):
    """Returns the (workgroup, username, password) tuple expected of pysmbc
    authentication functions.
    """
    return ("", "deathstar", "tordenskjold")

url = "172.16.20.230/Users/deathstar/documents/os2ds/setmode_doc.txt"
ctx = smbc.Context (auth_fn=auth_handler)
attr = ctx.getxattr(f"smb://deathstar:tordenskjold@{url}", "system.*")
print(attr)

print(f"\nusing pysmbc client")
entries = ctx.opendir ("smb://172.16.20.230/Users/deathstar/documents/os2ds").getdents ()
for entry in entries:
    print(entry)
