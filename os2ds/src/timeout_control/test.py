from os2datascanner.engine2.model.core import *
from os2datascanner.engine2.model.file import *
lrfs = Source.from_handle(FilesystemHandle.make_handle("/home/paw/Downloads/pain.xls"))
sm = SourceManager()
list(lrfs.handles(sm))
