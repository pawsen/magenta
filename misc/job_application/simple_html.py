#!/usr/bin/env python3


from html.parser import HTMLParser


class SimpleHTMLParser(HTMLParser):
    """This parser is intended to give same parsed output as BS4"""

    # https://github.com/python/cpython/blob/3.9/Lib/html/parser.py
    def __init__(self):
        super().__init__()
        self._in_body = False
        self.previoustag = "???"
        self.body = ""
        self.body2 = []
        self.reset()

    def handle_starttag(self, tag, attrs):
        # self.lasttag is updated in library before calling this function
        if self.lasttag == "body":
            self._in_body = True

        for name, value in attrs:
            pass

    def handle_data(self, data):
        if self._in_body:
            # This body is not equal to raw output of BS4.body.get_text(), as
            # the number of newlines differs. But this output from BS4 is
            # split'ed and join'ed and then we get same result.
            self.body += data

            # all the following is not necessary; body2 is not used. Does not
            # give exactly the same result at BS4,
            if data.strip():
                if self.lasttag == "br":
                    # as per output of BS4, no newline here.
                    pass
                    # self.body2[-1] += "\n"

                self.body2.append(" ".join(data.split()))

                # bit of a hack. Are last- and previoustag equal for NON-EMPTY
                # lines, then append current data to previous line.
                if self.lasttag == self.previoustag:
                    self.body2[-2] += self.body2[-1]
                    self.body2.pop()

                self.previoustag = self.lasttag


def html_parser(html):
    """simpleHTMLParser"""

    # decode byte-string
    try:
        html = str(html, "utf-8")
    except TypeError:
        # already str... fingers crossed :)
        pass
    parser = SimpleHTMLParser()
    parser.feed(html)
    parser.close()
    return " ".join(parser.body.split()) #, (parser.body, parser.body2)
