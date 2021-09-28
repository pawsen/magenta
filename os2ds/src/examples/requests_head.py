#!/usr/bin/env python3

import requests

"""
Example:
> curl -I https://web.firstagenda.com
HTTP/2 302

The final redirect result in
url="https://auth.firstagenda.com/oauth2/authorize?client_id=91687455-af96-434f-bf0a-878b9a270175&response_type=code&redirect_uri=https%3A%2F%2Fweb.firstagenda.com%2FAuthentication%2FTokenCallback%3FreturnUrl%3D%252F&requestedOrganisationId=0"

if we query this using a head requests, we get 404 - Not Found. We a get, we get
200 - OK. Idealy the server should respond with a 405 - Not allowed - for head,
if the server doesn't want us to do that.

curl -H ${url}
> 404

curl -i -o /dev/null -s -w "%{http_code}\n" ${url}
> 200

"""

url = "https://web.firstagenda.com"
r = requests.head(url)
print(f"no redirects: {r}")

r = requests.head(url, allow_redirects=True)
print(f"with redirects: {r}")

# a 302 - redirect - have a location field; where to go
print([r.headers["location"] for r in r.history])

# use the last redirect
url = r.history[-1].headers["location"]
requests.head(url)
# 404
requests.get(url)
# 202


# ok, so we need to either disallow redirects OR use get and only query for the
# first byte
headers = {"Range": "bytes=0-1"}
url = "http://download.thinkbroadband.com/5MB.zip"
r = requests.get(url, headers=headers)
print(r.text)
# > 'y™'

# But what about magenta...
r = requests.get("https://www.magenta.dk/", headers=headers)
len(r.text)
# 827756

## Magenta doesn't care...
