#!/usr/bin/python3
import click
from   packaging.version import parse
from   .                 import __version__
from   .api              import PyPIClient, first_upload
from   .util             import JSONLister, JSONMapper, clean_pypi_dict, \
                                    dumps, parse_packages

#ENDPOINT = 'https://pypi.python.org/pypi'
ENDPOINT = 'https://pypi.org/pypi'
TRUST_DOWNLOADS = False

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-i', '--index-url', default=ENDPOINT, metavar='URL',
              help='Use a different URL for PyPI', show_default=True)
@click.version_option(__version__, '-V', '--version',
                      message='%(prog)s %(version)s')
@click.pass_context
def qypi(ctx, index_url):
    """ Query PyPI from the command line """
    ctx.obj = PyPIClient(index_url)

@qypi.command()
@click.option('--pre', is_flag=True, help='Show prerelease versions')
@click.option('--newest/--highest', default=False,
              help='Does "latest" mean "newest" or "highest"? (default: highest)')
@click.option('--trust-downloads/--no-trust-downloads', default=TRUST_DOWNLOADS,
              help='Show download stats', show_default=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def info(ctx, packages, pre, newest, trust_downloads):
    """
    Show package details.

    Packages can be specified as either ``packagename`` to show the latest
    version (ignoring prerelease versions unless --pre is given) or as
    ``packagename==version`` to show the details for ``version``.
    """
    with JSONLister() as jlist:
        for pkg in parse_packages(ctx, packages, pre=pre, newest=newest):
            info = clean_pypi_dict(pkg["info"])
            info.pop('description', None)
            if not trust_downloads:
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
            if "package_url" in info and "project_url" not in info:
                # Field was renamed between PyPI Legacy and Warehouse
                info["project_url"] = info.pop("package_url")
            jlist.append(info)

@qypi.command()
@click.option('--pre', is_flag=True, help='Show prerelease versions')
@click.option('--newest/--highest', default=False,
              help='Does "latest" mean "newest" or "highest"? (default: highest)')
@click.argument('packages', nargs=-1)
@click.pass_context
def readme(ctx, packages, pre, newest):
    """
    View packages' long descriptions.

    If stdout is a terminal, the descriptions are passed to a pager program
    (e.g., `less(1)`).

    Packages can be specified as either ``packagename`` to show the latest
    version (ignoring prerelease versions unless --pre is given) or as
    ``packagename==version`` to show the long description for ``version``.
    """
    for pkg in parse_packages(ctx, packages, pre=pre, newest=newest):
        click.echo_via_pager(pkg["info"]["description"])

@qypi.command()
@click.argument('packages', nargs=-1)
@click.pass_context
def releases(ctx, packages):
    """ List released package versions """
    with JSONMapper() as jmap:
        for pkg in parse_packages(ctx, packages, versioned=False):
            try:
                project_url = pkg["info"]["project_url"]
            except KeyError:
                project_url = pkg["info"]["package_url"]
            if not project_url.endswith('/'):
                project_url += '/'
            jmap.append(
                pkg["info"]["name"],
                [{
                    "version": version,
                    "is_prerelease": parse(version).is_prerelease,
                    "release_date": first_upload(pkg["releases"][version]),
                    "release_url": project_url + version,
                } for version in sorted(pkg["releases"], key=parse)],
            )

@qypi.command()
@click.option('--pre', is_flag=True, help='Show prerelease versions')
@click.option('--newest/--highest', default=False,
              help='Does "latest" mean "newest" or "highest"? (default: highest)')
@click.option('--trust-downloads/--no-trust-downloads', default=TRUST_DOWNLOADS,
              help='Show download stats', show_default=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def files(ctx, packages, pre, newest, trust_downloads):
    """
    List files available for download.

    Packages can be specified as either ``packagename`` to show the latest
    version (ignoring prerelease versions unless --pre is given) or as
    ``packagename==version`` to show the files available for ``version``.
    """
    with JSONLister() as jlist:
        for pkg in parse_packages(ctx, packages, pre=pre, newest=newest):
            pkgfiles = pkg["urls"]
            for pf in pkgfiles:
                if not trust_downloads:
                    pf.pop("downloads", None)
                pf.pop("path", None)
                ### Change empty comment_text fields to None?
            jlist.append({
                "name": pkg["info"]["name"],
                "version": pkg["info"]["version"],
                "files": pkgfiles,
            })

@qypi.command('list')
@click.pass_obj
def listcmd(obj):
    """ List all packages on PyPI """
    for pkg in obj.xmlrpc('list_packages'):
        click.echo(pkg)

@qypi.command()
@click.option('--and', 'oper', flag_value='and', default=True,
              help='AND conditions together (default)')
@click.option('--or', 'oper', flag_value='or', help='OR conditions together')
@click.argument('terms', nargs=-1, required=True)
@click.pass_obj
def search(obj, terms, oper):
    """
    Search PyPI for packages.

    Search terms may be specified as either ``field:value`` (e.g.,
    ``summary:Django``) or just ``value`` to search long descriptions.
    """
    spec = {}
    for t in terms:
        key, colon, value = t.partition(':')
        if colon == '':
            key, value = 'description', t
        elif key == 'url':
            key = 'home_page'
        elif key in ('long_description', 'readme'):
            key = 'description'
        # ServerProxy can't handle defaultdicts, so we can't use those instead.
        spec.setdefault(key, []).append(value)
    click.echo(dumps(list(map(clean_pypi_dict,obj.xmlrpc('search',spec,oper)))))

@qypi.command()
@click.option('-f', '--file', type=click.File('r'))
@click.argument('classifiers', nargs=-1)
@click.pass_obj
def browse(obj, classifiers, file):
    """
    List packages with given trove classifiers.

    The list of classifiers may optionally be read from a file, one classifier
    per line.  Any further classifiers listed on the command line will be added
    to the file's list.
    """
    if file is not None:
        classifiers += tuple(map(str.strip, file))
    click.echo(dumps([
        {"name": name, "version": version or None}
        for name, version in obj.xmlrpc('browse', classifiers)
    ]))

@qypi.command()
@click.argument('packages', nargs=-1)
@click.pass_context
def owner(ctx, packages):
    """ List package owners & maintainers """
    with JSONMapper() as jmap:
        for pkg in parse_packages(ctx, packages, versioned=False):
            # Map through the JSON API so we can get the correct casing to
            # query the XML-RPC API with
            name = pkg["info"]["name"]
            jmap.append(name, [
                {"role": role, "user": user}
                for role, user in ctx.obj.xmlrpc('package_roles', name)
            ])

@qypi.command()
@click.argument('users', nargs=-1)
@click.pass_context
def owned(ctx, users):
    """ List packages owned/maintained by a user """
    with JSONMapper() as jmap:
        for u in users:
            jmap.append(u, [
                {"role": role, "package": pkg}
                for role, pkg in ctx.obj.xmlrpc('user_packages', u)
            ])

if __name__ == '__main__':
    qypi()
