#!/usr/bin/env python3

from contextlib import contextmanager

from os2datascanner.engine2.model.core import FileResource, Handle, Source

# https://github.com/os2datascanner/os2datascanner/blob/master/doc/engine2.rst#adding-a-new-data-source

# toy data source
backing_store = {
    "alec:secretpassword": {
        "/home/alec/Documents/secrets.txt": {
            "type": "text/plain",
            "content": b"A big dog!",
        },
        "/home/alec/Downloads/smile.png": {
            "type": "image/png",
            "content": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00"
            b"\x08\x00\x00\x00\x08\x08\x02\x00\x00\x00Km)\xdc"
            b"\x00\x00\x00*IDAT\x08\xd7c\xfc\xff\xff?\x036\xc0"
            b"\x04\xa1\x18\x19\x19\xd1\x18L\x0c8\x00N\tF|v\xc0"
            b"\xcdE\xb6\x86\x05\xcdN\xc2F\x01\x00\xc6#\t\x16"
            b"\xd7\xf5M}\x00\x00\x00\x00IEND\xaeB`\x82",
        },
    }
}


# Many engine2 classes override the Python __eq__ and __hash__ methods. For
# example, objects that open an equivalent connection to an external resource
# compare equal to each other.
#
# Overriding equality in this way makes it possible to implement the following
# logic to share and reuse connections:
#
# (This won't actually work because Sources don't have an open method as part of
# their public API, but this is, in principle, what SourceManager does behind
# the scenes.)
opened_sources = {}


def open_source(source):
    if source not in opened_sources:
        opened_sources = source.open()
    return opened_sources[source]


# "Authentication" against this data source will be performed by joining the
# username and password together with a : in the middle and doing a dictionary
# key lookup; exploration will then be a simple matter of iterating over the
# keys in the resulting dictionary. Outside of engine2, here's what that might
# look like:
def explore(username, password):
    auth_string = "{0}:{1}".format(username, password)
    if not auth_string in backing_store:
        raise ValueError("Username or password incorrect")

    files = backing_store[auth_string]
    for path, descriptor in files.items():
        yield (path, descriptor["type"], descriptor["content"])


# Supporting a new data source is a matter of implementing three classes: a
# Source subclass, a Resource subclass, and a Handle subclass to join them
# together.

# lets translate that into engine2


### ToySource
# The data source and its exploration strategy will be modelled by a Source
# subclass, which will emit Handle references that can be followed to their
# content through a Resource:
class ToySource(Source):
    type_label = "toy"

    # The constructor of a Source should take all the information needed to open
    # a connection and log in to a data source. Here, that's just a simple
    # username and password; in the real world, it could be a username and
    # password, or an API key, or an OAuth token.
    def __init__(self, username, password):
        self._username = username
        self._password = password

    # Now we need to implement the exploration strategy, and the generator
    # function that creates the state object. In the real world, this function
    # would open a connection to a remote server, authenticate against it, yield
    # a cookie of some kind, and then clean up after it when the generator
    # stops. Our toy example can be much simpler:
    def _generate_state(self, source_manager):
        auth_string = "{0}:{1}".format(self._username, self._password)
        if not auth_string in backing_store:
            raise ValueError(self, "Username or password incorrect")
        else:
            yield backing_store[auth_string]

    # We never call this state function explicitly, though. Instead, ToySource
    # objects call the SourceManager.open method on themselves:
    def handles(self, source_manager):
        files = source_manager.open(self)
        for path, descriptor in files.items():
            yield ToyHandle(self, path)

    ### Sensoring objects
    # Sources, in general, carry sensitive information. (Even our ToySource has
    # a username and password.) This sensitive information is necessary for the
    # model to do its job, but when we want to send objects to a lower-privilege
    # system, we want to be able to remove this information.
    #
    # Both Source and Handle define an abstract method called censor. This
    # method should return a version of the original object but with the
    # sensitive information stripped off:
    #
    # The resulting Source will not necessarily carry enough information to
    # generate a meaningful state object, and so will not necessarily compare
    # equal to this one.
    #
    # That is, a censored Source is supposed to be presentationally equivalent
    # to the original one, but nothing more: it carries enough information to be
    # able to point a user at the right website or network drive, but not enough
    # to actually give access to any objects.)
    def censor(self):
        return ToySource(username=None, password=None)

    ### Serialization
    # To give us as much flexibility as possible, to help with debugging, and to
    # make the system's internal messages human-readable, engine2 requires that
    # every class explicitly define its serialised forms.
    #
    # Sources must implement a method called to_json_object and should implement
    # a static method called from_json_object. The first of these returns an
    # object suitable for JSON serialisation, and the second is given a decoded
    # JSON object and returns a new Source of an appropriate type.
    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            **{"username": self._username, "password": self._password}
        )

    # The super implementation of this function just returns the dict {"type":
    # class.type_label}. The type property is used elsewhere in the system to
    # determine what kind of object is being deserialised.

    # engine2 uses decorators a lot to manage internal registries of things. The
    # Source.json_handler decorator adds things to the registry behind the
    # Source.from_json_object function -- the pipeline uses this function to
    # load serialised Sources without having to know anything about them.
    #
    # It's not important that a method with the specific name from_json_object
    # exists: what's important is that an appropriate method is added to the
    # internal registry.
    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return ToySource(username=obj["username"], password=obj["password"])


### Operations: ToyResource
# We can now discover and point at objects in our toy filesystem. This is a good
# start, but now we need to be able to do things to those objects: we need a
# Resource.

# More specifically, since our objects look like files, we need the subclass
# FileResource, which takes care of some of the basics for us:
class ToyResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._entry = None

    # Resources are short-lived and not serialisable, so they're allowed to
    # track state. Here, for example, is a simple cache of the underlying
    # dictionary entry. (Resource._get_cookie is a utility method that calls
    # SourceManager.open(self.handle.source) on the Resource's bound
    # SourceManager.)
    def _get_entry(self):
        if not self._entry:
            self._entry = self._get_cookie()[self.handle.relative_path]
        return self._entry

    # Files in the engine2 world always have a last modification date associated
    # with them. There is a default, naïve implementation of this method in
    # FileResource, which returns the time the method was first called; There
    # are virtually always better approaches available, though, so it's declared
    # as an abstract method to force subclasses to explicitly decide whether or
    # not to use it.
    #
    # Our toy filesystem doesn't have enough information for us to do better, so
    # we'll just use the default implementation.
    def get_last_modified(self):
        return super().get_last_modified()

    #  Here are the two methods at the heart of FileResource: get_size, which
    #  retrieves a metadata property, and make_stream, which makes the file's
    #  content available to the rest of the OS2datascanner system.
    def get_size(self):
        return len(self._get_entry()["content"])

    @contextmanager
    def make_stream(self):
        from io import BytesIO

        yield BytesIO(self._get_entry()["content"])

    # FileResource comes with a few other useful methods, such as compute_type,
    # a counterpart to Handle.guess_type that's actually allowed to look at the
    # content of the file.

    def check(self) -> bool:
        return True

    @contextmanager
    def make_path(self):
        from os2datascanner.engine2.model.utilities import NamedTemporaryResource

        # write content to temporary file
        with NamedTemporaryResource(self.handle.name) as ntr:
            with ntr.open("wb") as res:
                with self.make_stream() as s:
                    res.write(s.read())
            yield ntr.get_path()


### References: ToyHandle
# The next thing to implement is ToyHandle. As this is a simple Handle (it just
# binds a Source to a named object), the Handle base class will implement almost
# everything for us:
#
# Since we don't store any properties other than a Source and a path, we can use
# the Handle.stock_json_handler decorator, which automatically registers a
# standard from_json_object-like function with the registry used by the
# Handle.from_json_object function.
@Handle.stock_json_handler("toy")
class ToyHandle(Handle):

    # The Handle class defines a method, follow, that binds a Handle to a
    # SourceManager and returns a new Resource. The implementation of this
    # function is always the same: return self.resource_type(self,
    # source_manager).
    type_label = "toy"
    resource_type = ToyResource

    # Because engine2 objects can get quite complicated, the Handle API is also
    # used by the user interface components of OS2datascanner to compute names
    # for things. This is the job of the Handle.presentation method: it should
    # return something that the user recognises as a name.
    #
    # There's also an optional Handle.presentation_url method that returns a
    # user-friendly link to an object. The definition of "link" is deliberately
    # a bit fuzzy: for example, an message in an email account scanned over IMAP
    # might have a presentation_url implementation that points at a webmail
    # system. We don't need to define that here, though, since there are no
    # meaningful links to Python dictionary members.
    @property
    def presentation(self):
        return "A ToyHandle"

    # Handles carry Source references, so they need to be censorable as well. (A
    # Source is supposed to be presentationally equivalent to its censored form,
    # which in turn means that handle.presentation is supposed to be equal to
    # handle.censor().presentation.)
    def censor(self):
        return ToyHandle(self.source.censor(), self.relative_path)

    # Handle automatically provides a few other useful functions, like
    # guess_type, which returns an educated guess for the object's MIME type.
    #
    # The default implementation of Handle.guess_type just looks at the name and
    # makes a decision based on the file extension, but this too can be
    # overridden. (Don't try to do anything too clever in this method, though --
    # remember that Handles are just references and can't look at content.)


# SourceManager.open is the real version of the hypothetical open_source
# function we saw earlier. It will either return a cached cookie or call
# _generate_state to make a fresh one (which will itself then be cached).

# SourceManager implements a lot of engine2's clever behaviour: for example,
# opening a Source might cause older Sources to be closed.

# _generate_state is an important internal API. Its return value (as returned by
# SourceManager.open) is also the entire interface between a Source and its
# Resource subclass, so that value must also expose everything needed to
# retrieve file data and metadata.

# Some classes make API guarantees for their _generate_state method. For
# example, the FilesystemSource method states that it yields a directory path.
# This allows us to mix and match classes in weird ways: if another Source also
# puts objects in the filesystem and implements a compatible _generate_state
# method, then it can reuse the FilesystemResource class to give access to them.
# (See os2datascanner.engine2.model.derived.pdf for an example of this.)


# The implementation of our Source is now substantially finished, but we can't
# instantiate this object just yet:
