import click
from   packaging.version import parse
from   .                 import __version__
from   .api              import QyPI, first_upload
from   .util             import JSONLister, JSONMapper, clean_pypi_dict, \
                                    dumps, package_args, squish_versions

ENDPOINT = 'https://pypi.org/pypi'
TRUST_DOWNLOADS = False

SEARCH_SYNONYMS = {
    'homepage': 'home_page',
    'url': 'home_page',
    'long_description': 'description',
    'readme': 'description',
    'keyword': 'keywords',
}

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-i', '--index-url', default=ENDPOINT, metavar='URL',
              help='Use a different URL for PyPI', show_default=True)
@click.version_option(__version__, '-V', '--version',
                      message='%(prog)s %(version)s')
@click.pass_context
def qypi(ctx, index_url):
    """ Query PyPI from the command line """
    ctx.obj = QyPI(index_url)

@qypi.result_callback()
@click.pass_context
def cleanup(ctx, *_args, **_kwargs):
    ctx.obj.cleanup(ctx)

@qypi.command()
@click.option('--description/--no-description', default=False,
              help='Include (long) descriptions', show_default=True)
@click.option('--trust-downloads/--no-trust-downloads', default=TRUST_DOWNLOADS,
              help='Show download stats', show_default=True)
@package_args()
def info(packages, trust_downloads, description):
    """
    Show package details.

    Packages can be specified as either ``packagename`` to show the latest
    version or as ``packagename==version`` to show the details for ``version``.
    """
    with JSONLister() as jlist:
        for pkg in packages:
            info = clean_pypi_dict(pkg["info"])
            if not description:
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
@package_args()
def readme(packages):
    """
    View packages' long descriptions.

    If stdout is a terminal, the descriptions are passed to a pager program
    (e.g., `less(1)`).

    Packages can be specified as either ``packagename`` to show the latest
    version or as ``packagename==version`` to show the long description for
    ``version``.
    """
    for pkg in packages:
        click.echo_via_pager(pkg["info"]["description"])

@qypi.command()
@package_args(versioned=False)
def releases(packages):
    """ List released package versions """
    with JSONMapper() as jmap:
        for pkg in packages:
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
@click.option('--trust-downloads/--no-trust-downloads', default=TRUST_DOWNLOADS,
              help='Show download stats', show_default=True)
@package_args()
def files(packages, trust_downloads):
    """
    List files available for download.

    Packages can be specified as either ``packagename`` to show the latest
    version or as ``packagename==version`` to show the files available for
    ``version``.
    """
    with JSONLister() as jlist:
        for pkg in packages:
            pkgfiles = pkg["urls"]
            for pf in pkgfiles:
                if not trust_downloads:
                    pf.pop("downloads", None)
                pf.pop("path", None)
                ### TODO: Change empty comment_text fields to None?
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
              help='AND conditions together [default]')
@click.option('--or', 'oper', flag_value='or', help='OR conditions together')
@click.option('-p/-r', '--packages/--releases', default=False,
              help='Show one result per package/per release'
                   ' [default: per release]')
@click.argument('terms', nargs=-1, required=True)
@click.pass_obj
def search(obj, terms, oper, packages):
    """
    Search PyPI for packages or releases thereof.

    Search terms may be specified as either ``field:value`` (e.g.,
    ``summary:Django``) or just ``value`` to search long descriptions.
    """
    spec = {}
    for t in terms:
        key, colon, value = t.partition(':')
        if colon == '':
            key, value = 'description', t
        else:
            key = SEARCH_SYNONYMS.get(key, key)
        # ServerProxy can't handle defaultdicts, so we can't use those instead.
        spec.setdefault(key, []).append(value)
    results = map(clean_pypi_dict, obj.xmlrpc('search', spec, oper))
    if packages:
        results = squish_versions(results)
    click.echo(dumps(results))

@qypi.command()
@click.option('-f', '--file', type=click.File('r'))
@click.option('-p/-r', '--packages/--releases', default=False,
              help='Show one result per package/per release'
                   ' [default: per release]')
@click.argument('classifiers', nargs=-1)
@click.pass_obj
def browse(obj, classifiers, file, packages):
    """
    List packages with given trove classifiers.

    The list of classifiers may optionally be read from a file, one classifier
    per line.  Any further classifiers listed on the command line will be added
    to the file's list.
    """
    if file is not None:
        classifiers += tuple(map(str.strip, file))
    results = [
        {"name": name, "version": version or None}
        for name, version in obj.xmlrpc('browse', classifiers)
    ]
    if packages:
        results = squish_versions(results)
    click.echo(dumps(results))

@qypi.command()
@click.argument('packages', nargs=-1)
@click.pass_obj
def owner(obj, packages):
    """ List package owners & maintainers """
    with JSONMapper() as jmap:
        for pkg in packages:
            jmap.append(pkg, [
                {"role": role, "user": user}
                for role, user in obj.xmlrpc('package_roles', pkg)
            ])

@qypi.command()
@click.argument('users', nargs=-1)
@click.pass_obj
def owned(obj, users):
    """ List packages owned/maintained by a user """
    with JSONMapper() as jmap:
        for u in users:
            jmap.append(u, [
                {"role": role, "package": pkg}
                for role, pkg in obj.xmlrpc('user_packages', u)
            ])

if __name__ == '__main__':
    qypi()
