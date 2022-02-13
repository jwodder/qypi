from contextlib import ExitStack
import platform
import sys
from xmlrpc.client import ServerProxy
import click
from packaging.version import parse
import requests
from . import __url__, __version__

USER_AGENT = "qypi/{} ({}) requests/{} {}/{}".format(
    __version__,
    __url__,
    requests.__version__,
    platform.python_implementation(),
    platform.python_version(),
)


class QyPI:
    def __init__(self, index_url):
        self.index_url = index_url
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        if sys.version_info >= (3, 8):
            xsp_kwargs = {"headers": [("User-Agent", USER_AGENT)]}
        else:
            xsp_kwargs = {}
        self.xsp = ServerProxy(self.index_url, **xsp_kwargs)
        self.pre = False
        self.newest = False
        self.all_versions = False
        self.errmsgs = []
        self.ctx_stack = ExitStack()

    def __enter__(self) -> "QyPI":
        self.ctx_stack.enter_context(self.s)
        self.ctx_stack.enter_context(self.xsp)
        return self

    def __exit__(self, *_exc) -> None:
        self.ctx_stack.close()

    def get(self, *path):
        return self.s.get(self.index_url.rstrip("/") + "/" + "/".join(path))

    def get_package(self, package):
        r = self.get(package, "json")
        # Unlike the XML-RPC API, the JSON API accepts package names regardless
        # of normalization
        if r.status_code == 404:
            raise QyPIError(package + ": package not found")
        r.raise_for_status()
        return r.json()

    def get_latest_version(self, package):
        # TODO: Eliminate
        pkg = self.get_package(package)
        releases = {
            (parse(rel), rel): first_upload(files)
            # The unparsed version string needs to be kept around because the
            # alternative approach (stringifying the Version object once
            # comparisons are done) can result in a different string (e.g.,
            # "2001.01.01" becomes "2001.1.1"), leading to a 404.
            for rel, files in pkg["releases"].items()
        }
        candidates = releases.keys()
        if not self.pre and any(not v[0].is_prerelease for v in candidates):
            candidates = filter(lambda v: not v[0].is_prerelease, candidates)
        if self.newest:
            latest = max(
                filter(releases.__getitem__, candidates),
                key=releases.__getitem__,
                default=None,
            )
        else:
            latest = max(candidates, default=None)
        if latest is None:
            raise QyPIError(package + ": no suitable versions available")
        latest = latest[1]
        if pkg["info"]["version"] == latest:
            return pkg
        else:
            return self.get_package_version(package, latest)

    def get_package_version(self, package, version):
        r = self.get(package, version, "json")
        if r.status_code == 404:
            raise QyPIError(f"{package}: version {version} not found")
        r.raise_for_status()
        return r.json()

    def xmlrpc(self, method, *args, **kwargs):
        return getattr(self.xsp, method)(*args, **kwargs)

    def lookup_package(self, args):
        # TODO: Eliminate
        for name in args:
            try:
                yield self.get_package(name)
            except QyPIError as e:
                self.errmsgs.append(str(e))

    def lookup_package_version(self, args):
        for spec in args:
            name, eq, version = spec.partition("=")
            try:
                if eq != "":
                    yield self.get_package_version(name, version.lstrip("="))
                elif self.all_versions:
                    p = self.get_package(name)
                    for v in sorted(p["releases"], key=parse):
                        if self.pre or not parse(v).is_prerelease:
                            if v == p["info"]["version"]:
                                yield p
                            else:
                                ### TODO: Can this call ever fail?
                                yield self.get_package_version(name, v)
                else:
                    yield self.get_latest_version(name)
            except QyPIError as e:
                self.errmsgs.append(str(e))

    def cleanup(self, ctx):
        # TODO: Eliminate
        if self.errmsgs:
            for msg in self.errmsgs:
                click.echo(ctx.command_path + ": " + msg, err=True)
            ctx.exit(1)


class QyPIError(Exception):
    pass


def first_upload(files):
    return min((f["upload_time_iso_8601"] for f in files), default=None)
