import base64

from os2datascanner.engine2.model.core import Source
from os2datascanner.engine2.rules.dummy import BuggyRule
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.utils.system_utilities import time_now
import os2datascanner.engine2.pipeline.messages as messages

from pprint import pprint

"""This sends a scan to explorer, by submitting a `scan_spec` message to
RabbitMQ

This will crash admin.pipeline_collector, if there's no matching pk in the Scanner
table. So clear the queues after running this which is easiest done by using the
RabbitMQ web interface

http://localhost:8030 (user/pass os2ds)

and then purge (or view) the queues.

"""


data = """Bare en lang streng af data

111111-1118
"""
data_url = "data:text/plain;base64,{0}".format(
    base64.encodebytes(data.encode("utf-8")).decode("ascii")
)


scan_tag = messages.ScanTagFragment(
    time=time_now(),
    user=None,
    scanner=messages.ScannerFragment(pk=3, name="paws scanner"),
    organisation=None,
)

configuration = {"skip_mime_types": ["image/*"]}
source = Source.from_url(data_url)
scan_spec = messages.ScanSpecMessage(
    scan_tag=scan_tag,
    rule=BuggyRule(),  # rule,
    configuration=configuration,
    source=source,
    progress=None,
)

## It would be easier just to generate the json scan_spec message directly
# obj = {
#     "scan_tag": {
#         "scanner": {
#             "name": "integration_test",
#             "pk": 0
#         },
#         "user": None,
#         "organisation": "Vejstrand Kommune",
#         "time": "2020-01-01T00:00:00+00:00"
#     },
#     "source": Source.from_url(data_url).to_json_object(),
#     "rule": {
#         "type": "buggy"
#     }
# }
#

msg = []
msg.append(
    (
        "os2ds_scan_specs",
        scan_spec.to_json_object(),
    )
)

pprint(msg)
# exit()

with PikaPipelineThread(write={queue for queue, _ in msg}) as sender:
    for queue, message in msg:
        sender.enqueue_message(queue, message)
    sender.enqueue_stop()
    sender.start()
    sender.join()
