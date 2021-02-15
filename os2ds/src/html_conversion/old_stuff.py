#!/usr/bin/env python3


## read wiki page
url = "https://en.wikipedia.org/wiki/Spider"
sm = SourceManager()

source = SecureWebSource(url)
handle = source.handles(sm)
h = next(handle)
resource = h.follow(sm)
with resource.make_stream() as fp:
    content = fp.read()


##
def test_wiki_page():
    # url = "https://en.wikipedia.org/wiki/Spider"

    # create json to inject into the conversion queue
    obj = messages.ConversionMessage(
        scan_spec=messages.ScanSpecMessage(
            scan_tag="dummy",
            source=WebSource("https://en.wikipedia.org/"),
            rule=RegexRule("[Aa]rachnid"),
            configuration={},
            progress=None,
        ),
        handle=WebHandle(WebSource("https://en.wikipedia.org/"), "/wiki/Spider"),
        progress=messages.ProgressFragment(rule=RegexRule("[Aa]rachnid"), matches=[]),
    ).to_json_object()

    mylist = list(
        processor.message_received_raw(obj, "os2ds_conversions", SourceManager())
    )
    return mylist


curdir = os.path.dirname(__file__)
benchpath = os.path.join(curdir, "..", "data", "html_benchmark", "data")


def test_local_html():
    # create json to inject into the conversion queue
    obj = messages.ConversionMessage(
        scan_spec=messages.ScanSpecMessage(
            scan_tag="dummy",
            source=FilesystemSource(benchpath),
            rule=RegexRule("[Aa]rachnid"),
            configuration={},
            progress=None,
        ),
        handle=FilesystemHandle(FilesystemSource(benchpath), "html.html"),
        progress=messages.ProgressFragment(rule=RegexRule("[Aa]rachnid"), matches=[]),
    ).to_json_object()

    mylist = list(
        processor.message_received_raw(obj, "os2ds_conversions", SourceManager())
    )
    return mylist


# CONVERSION_LIB = 'bs4'
CONVERSION_LIB = "lxml"
if __name__ == "__main__":
    # obj = test_wiki_page()
    obj = test_local_html()
    msg = obj[0][1]
    text = msg["representations"]["text"]
    os.makedirs(os.path.join(curdir, "out"), exist_ok=True)

    fpath = os.path.join(curdir, "out", f"html_{CONVERSION_LIB}.txt")
    print(f"## dumping to file {os.path.basename(fpath)}")
    with open(fpath, "w") as fp:
        fp.write(text)

    print(f"## timing")
    t = timeit.Timer(lambda: test_local_html())
    print(f"{t.timeit(number=5):.5}")
