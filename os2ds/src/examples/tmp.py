#!/usr/bin/env ipython


with SourceManager() as sm:
    try:
        a = testfile.follow(sm)
    except:
        pass

example_handles = [

    FilesystemHandle(
            FilesystemSource(datadir.absolute()),
            "test.txt"),
    DataHandle(
            DataSource(b"This is a test", "text/plain"),
            "file"),
    DataHandle(
            DataSource(b"This is a test", "text/plain", "test.txt"),
            "test.txt"),


]
