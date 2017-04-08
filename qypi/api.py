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
            raise PackageNotFoundError(package)
        r.raise_for_status()
        return r.json()

    def get_latest_version(self, package):
        pkg = self.get_package(package)
        releases = {
            parse(rel): first_upload(files)
            for rel, files in pkg["releases"].items()
        }
        candidates = releases.keys()
        if not self.pre:
            candidates = filter(lambda v: not v.is_prerelease, candidates)
        if self.newest:
            latest = max(
                filter(releases.__getitem__, candidates),
                key=releases.__getitem__,
                default=None,
            )
        else:
            latest = max(candidates, default=None)
        if latest is None:
            raise NoSuitableVersionError(package)
        latest = str(latest)
        ### TODO: Will stringifying the parsed version string instead of using
        ### the original key from `pkg["releases"]` ever change the version
        ### string in a meaningful way?
        if pkg["info"]["version"] == latest:
            return pkg
        else:
            return self.get_version(package, latest)

    def get_version(self, package, version):
        r = self.get(package, version, 'json')
        if r.status_code == 404:
            raise VersionNotFoundError(package, version)
        r.raise_for_status()
        return r.json()

    def xmlrpc(self, method, *args, **kwargs):
        if self.xsp is None:
            self.xsp = ServerProxy(self.index_url)
        return getattr(self.xsp, method)(*args, **kwargs)

    def lookup_package(self, args):
        pkgs = []
        for name in args:
            try:
                pkgs.append(self.get_package(name))
            except QyPIError as e:
                self.errmsgs.append(str(e))
        return pkgs

    def lookup_package_version(self, args):
        pkgs = []
        for spec in args:
            name, eq, version = spec.partition('=')
            try:
                if eq == '':
                    pkgs.append(self.get_latest_version(name))
                else:
                    pkgs.append(self.get_version(name, version.lstrip('=')))
            except QyPIError as e:
                self.errmsgs.append(str(e))
        return pkgs

    def cleanup(self, ctx):
        if self.errmsgs:
            for msg in self.errmsgs:
                click.echo(ctx.command_path + ': ' + msg, err=True)
                ctx.exit(1)


class QyPIError(Exception):
    pass


class PackageNotFoundError(QyPIError):
    def __init__(self, package):
        self.package = package

    def __str__(self):
        return self.package + ': package not found'


class VersionNotFoundError(QyPIError):
    def __init__(self, package, version):
        self.package = package
        self.version = version

    def __str__(self):
        return '{0.package}: version {0.version} not found'.format(self)


class NoSuitableVersionError(QyPIError):
    def __init__(self, package):
        self.package = package

    def __str__(self):
        return self.package + ': no suitable versions available'

def first_upload(files):
    return min((f["upload_time"] for f in files), default=None)
