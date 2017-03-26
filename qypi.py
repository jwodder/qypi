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
        about = r.json()
        if not pre and parse(about["info"]["version"]).is_prerelease:
            latest = max((v for v in map(parse, about["releases"])
                            if not v.is_prerelease), default=None)
            if latest is None:
                raise NoStableVersionError(package)
            r = self.s.get('{}/{}/{}/json'.format(self.index_url, package, latest))
            ### Will stringifying the parsed version string instead of using
            ### the original key from `about["releases"]` ever change the
            ### version string in a meaningful way?
            r.raise_for_status()
            about = r.json()
        return about


class QyPIError(Exception):
    pass


class PackageNotFoundError(QyPIError):
    def __init__(self, package):
        self.package = package

    def __str__(self):
        return self.package + ': package not found'


class NoStableVersionError(QyPIError):
    def __init__(self, package):
        self.package = package

    def __str__(self):
        return self.package + ': no stable versions available'


def dumps(obj):
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-i', '--index-url', default=ENDPOINT, metavar='URL',
              envvar='PIP_INDEX_URL')
@click.pass_context
def qypi(ctx, index_url):
    """ Query PyPI """
    ctx.obj = QyPI(index_url)

@qypi.command()
@click.option('-a', '--array', is_flag=True)
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def info(ctx, packages, array, pre):
    ok = True
    pkgdata = []
    for pkgname in packages:
        try:
            about = ctx.obj.get_latest_version(pkgname, pre)
        except QyPIError as e:
            click.echo('qypi: ' + str(e), err=True)
            ok = False
            continue
        pkg = about["info"]
        for k,v in list(pkg.items()):
            if k.startswith(('cheesecake', '_pypi')):
                del pkg[k]
            elif v in ('', 'UNKNOWN'):
                pkg[k] = None
        pkg.pop('description', None)
        pkg.pop('downloads', None)
        pkg["url"] = pkg.pop('home_page', None)
        pkg["release_date"] = min(
            (obj["upload_time"] for obj in about["urls"]), default=None,
        )
        pkg["people"] = []
        for role in ('author', 'maintainer'):
            name = pkg.pop(role, None)
            email = pkg.pop(role + '_email', None)
            if name or email:
                pkg["people"].append({
                    "name": name,
                    "email": email,
                    "role": role,
                })
        if array:
            pkgdata.append(pkg)
        else:
            click.echo(dumps(pkg))
    if array:
        click.echo(dumps(pkgdata))
    ctx.exit(0 if ok else 1)

@qypi.command()
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def readme(ctx, packages, pre):
    ok = True
    for pkgname in packages:
        try:
            about = ctx.obj.get_latest_version(pkgname, pre)
        except QyPIError as e:
            click.echo('qypi: ' + str(e), err=True)
            ok = False
            continue
        click.echo_via_pager(about["info"]["description"])
    ctx.exit(0 if ok else 1)

if __name__ == '__main__':
    qypi()
