#!/usr/bin/python3
import click
from   packaging.version import parse
from   .api              import PyPIClient, QyPIError
from   .util             import clean_pypi_dict, dumps, first_upload, \
                                    parse_packages

#ENDPOINT = 'https://pypi.python.org/pypi'
ENDPOINT = 'https://pypi.org/pypi'

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-i', '--index-url', default=ENDPOINT, metavar='URL',
              envvar='PIP_INDEX_URL')
@click.pass_context
def qypi(ctx, index_url):
    """ Query & search PyPI from the command line """
    ctx.obj = PyPIClient(index_url)

@qypi.command()
@click.option('-a', '--array', is_flag=True)
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def info(ctx, packages, array, pre):
    pkgdata = []
    try:
        for pkg in parse_packages(ctx, packages, pre):
            info = clean_pypi_dict(pkg["info"])
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
            if "package_url" in info and "project_url" not in info:
                # Field was renamed between PyPI Legacy and Warehouse
                info["project_url"] = info.pop("package_url")
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
    ### TODO: Use `parse_packages()` for this (without allowing `=version`
    ### suffixes)
    ok = True
    for name in packages:
        try:
            pkg = ctx.obj.get_latest_version(name, pre=True)
        except QyPIError as e:
            click.echo(ctx.command_path + ': ' + str(e), err=True)
            ok = False
        else:
            try:
                project_url = pkg["info"]["project_url"]
            except KeyError:
                project_url = pkg["info"]["package_url"]
            if not project_url.endswith('/'):
                project_url += '/'
            about = {
                "name": pkg["info"]["name"],
                "releases": [{
                    "version": version,
                    "is_prerelease": parse(version).is_prerelease,
                    "release_date": first_upload(pkg["releases"][version]),
                    "release_url": project_url + version,
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

@qypi.command('list')
@click.pass_obj
def listcmd(obj):
    for pkg in obj.xmlrpc('list_packages'):
        click.echo(pkg)

@qypi.command()
@click.argument('terms', nargs=-1, required=True)
@click.pass_obj
def search(obj, terms):
    spec = {}
    for t in terms:
        key, colon, value = t.partition(':')
        if colon == '':
            key, value = 'description', t
        elif key == 'url':
            key = 'home_page'
        # ServerProxy can't handle defaultdicts, so we can't use those instead.
        spec.setdefault(key, []).append(value)
    click.echo(dumps(list(map(clean_pypi_dict, obj.xmlrpc('search', spec)))))

@qypi.command()
@click.option('-f', '--file', type=click.File('r'))
@click.argument('classifiers', nargs=-1)
@click.pass_obj
def browse(obj, classifiers, file):
    if file is not None:
        classifiers += tuple(map(str.strip, file))
    click.echo(dumps([
        {"name": name, "version": version or None}
        for name, version in obj.xmlrpc('browse', classifiers)
    ]))

if __name__ == '__main__':
    qypi()