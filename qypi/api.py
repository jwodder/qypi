from   xmlrpc.client     import ServerProxy
import click
from   packaging.version import parse
import requests

class QyPI:
    def __init__(self, index_url):
        self.index_url = index_url
        self.s = None
        self.xsp = None
        self.pre = False
        self.newest = False
        self.all_versions = False
        self.errmsgs = []

    def get(self, *path):
        if self.s is None:
            self.s = requests.Session()
        return self.s.get(self.index_url.rstrip('/') + '/' + '/'.join(path))

    def get_package(self, package):
        r = self.get(package, 'json')
        # Unlike the XML-RPC API, the JSON API accepts package names regardless
        # of normalization
        if r.status_code == 404:
            raise QyPIError(package + ': package not found')
        r.raise_for_status()
        return r.json()

    def get_latest_version(self, package):
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
            raise QyPIError(package + ': no suitable versions available')
        latest = latest[1]
        if pkg["info"]["version"] == latest:
            return pkg
        else:
            return self.get_version(package, latest)

    def get_version(self, package, version):
        r = self.get(package, version, 'json')
        if r.status_code == 404:
            raise QyPIError('{}: version {} not found'.format(package, version))
        r.raise_for_status()
        return r.json()

    def xmlrpc(self, method, *args, **kwargs):
        if self.xsp is None:
            self.xsp = ServerProxy(self.index_url)
        return getattr(self.xsp, method)(*args, **kwargs)

    def lookup_package(self, args):
        for name in args:
            try:
                yield self.get_package(name)
            except QyPIError as e:
                self.errmsgs.append(str(e))

    def lookup_package_version(self, args):
        for spec in args:
            name, eq, version = spec.partition('=')
            try:
                if eq != '':
                    yield self.get_version(name, version.lstrip('='))
                elif self.all_versions:
                    p = self.get_package(name)
                    for v in sorted(p["releases"], key=parse):
                        if self.pre or not parse(v).is_prerelease:
                            if v == p["info"]["version"]:
                                yield p
                            else:
                                ### TODO: Can this call ever fail?
                                yield self.get_version(name, v)
                else:
                    yield self.get_latest_version(name)
            except QyPIError as e:
                self.errmsgs.append(str(e))

    def cleanup(self, ctx):
        if self.errmsgs:
            for msg in self.errmsgs:
                click.echo(ctx.command_path + ': ' + msg, err=True)
            ctx.exit(1)


class QyPIError(Exception):
    pass


def first_upload(files):
    return min((f["upload_time"] for f in files), default=None)
