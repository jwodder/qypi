#!/usr/bin/python3
import json
import click
from   packaging.version import parse
import requests

ENDPOINT = 'https://pypi.python.org/pypi'
#ENDPOINT = 'https://pypi.org/pypi'

class QyPI:
    def __init__(self, index_url):
        self.index_url = index_url
        self.s = requests.Session()

    def get_latest_version(self, package, pre=False):
        r = self.s.get(self.index_url + '/' + package + '/json')
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
        r = self.s.get('{}/{}/{}/json'.format(self.index_url, package, version))
        if r.status_code == 404:
            raise VersionNotFoundError(package, version)
        r.raise_for_status()
        return r.json()


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


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-i', '--index-url', default=ENDPOINT, metavar='URL',
              envvar='PIP_INDEX_URL')
@click.pass_context
def qypi(ctx, index_url):
    """ Query & search PyPI from the command line """
    ctx.obj = QyPI(index_url)

@qypi.command()
@click.option('-a', '--array', is_flag=True)
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def info(ctx, packages, array, pre):
    pkgdata = []
    try:
        for pkg in parse_packages(ctx, packages, pre):
            info = pkg["info"]
            for k,v in list(info.items()):
                if k.startswith(('cheesecake', '_pypi')):
                    del info[k]
                elif v in ('', 'UNKNOWN'):
                    info[k] = None
            info.pop('description', None)
            info.pop('downloads', None)
            info["url"] = info.pop('home_page', None)
            info["release_date"] = first_upload(pkg["urls"])
            info["people"] = []
            for role in ('author', 'maintainer'):
                name = info.pop(role, None)
                email = info.pop(role + '_email', None)
                if name or email:
                    info["people"].append({
                        "name": name,
                        "email": email,
                        "role": role,
                    })
            if array:
                pkgdata.append(info)
            else:
                click.echo(dumps(info))
    finally:
        if array:
            click.echo(dumps(pkgdata))

@qypi.command()
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def readme(ctx, packages, pre):
    for pkg in parse_packages(ctx, packages, pre):
        click.echo_via_pager(pkg["info"]["description"])

@qypi.command()
@click.argument('packages', nargs=-1)
@click.pass_context
def releases(ctx, packages):
    ok = True
    for name in packages:
        try:
            pkg = ctx.obj.get_latest_version(name, pre=True)
        except QyPIError as e:
            click.echo(ctx.command_path + ': ' + str(e), err=True)
            ok = False
        else:
            about = {
                "name": pkg["info"]["name"],
                "releases": [{
                    "version": version,
                    "is_prerelease": parse(version).is_prerelease,
                    "release_date": first_upload(pkg["releases"][version]),
                    "release_url": pkg["info"]["package_url"] + '/' + version,
                } for version in sorted(pkg["releases"], key=parse)],
            }
            click.echo(dumps(about))
    if not ok:
        ctx.exit(1)

@qypi.command()
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def files(ctx, packages, pre):
    for pkg in parse_packages(ctx, packages, pre):
        pkgfiles = pkg["urls"]
        for pf in pkgfiles:
            pf.pop("downloads", None)
            pf.pop("path", None)
            ### Change empty comment_text fields to None?
        click.echo(dumps(pkgfiles))

def parse_packages(ctx, packages, pre):
    ### TODO: Look into a better way to integrate this with Click
    ok = True
    for pkgname in packages:
        try:
            name, eq, version = pkgname.partition('=')
            if eq == '':
                pkg = ctx.obj.get_latest_version(name, pre)
            else:
                pkg = ctx.obj.get_version(name, version.lstrip('='))
        except QyPIError as e:
            click.echo(ctx.command_path + ': ' + str(e), err=True)
            ok = False
        else:
            yield pkg
    if not ok:
        ctx.exit(1)

def dumps(obj):
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)

def first_upload(files):
    return min((f["upload_time"] for f in files), default=None)

if __name__ == '__main__':
    qypi()
