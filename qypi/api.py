from   xmlrpc.client     import ServerProxy
from   packaging.version import parse
import requests

class PyPIClient:
    def __init__(self, index_url):
        self.index_url = index_url
        self.s = None
        self.xsp = None

    def get(self, *path):
        if self.s is None:
            self.s = requests.Session()
        return self.s.get(self.index_url.rstrip('/') + '/' + '/'.join(path))

    def get_latest_version(self, package, pre=False):
        r = self.get(package, 'json')
        # Unlike the XML-RPC API, the JSON API accepts package names regardless
        # of normalization
        if r.status_code == 404:
            raise PackageNotFoundError(package)
        r.raise_for_status()
        pkg = r.json()
        if not pre and parse(pkg["info"]["version"]).is_prerelease:
            latest = max((v for v in map(parse, pkg["releases"])
                            if not v.is_prerelease), default=None)
            if latest is None:
                raise NoStableVersionError(package)
            return self.get_version(package, str(latest))
            ### Will stringifying the parsed version string instead of using
            ### the original key from `pkg["releases"]` ever change the version
            ### string in a meaningful way?
        return pkg

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


class NoStableVersionError(QyPIError):
    def __init__(self, package):
        self.package = package

    def __str__(self):
        return self.package + ': no stable versions available'
