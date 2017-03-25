#!/usr/bin/python3
# Unlike the XML-RPC API, the JSON API accepts package names regardless of
# normalization

import json
import click
from   packaging.version import parse
import requests

ENDPOINT = 'https://pypi.python.org/pypi'
#ENDPOINT = 'https://pypi.org/pypi'

def dumps(obj):
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-a', '--array', is_flag=True)
@click.option('-D', '--description', '--long-description', is_flag=True)
@click.option('--pre', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def qypi(ctx, packages, array, long_description, pre):
    s = requests.Session()
    ok = True
    pkgdata = []
    for pkgname in packages:
        r = s.get(ENDPOINT + '/' + pkgname + '/json')
        if r.status_code == 404:
            click.echo('qypi: {}: package not found'.format(pkgname), err=True)
            ok = False
            continue
        r.raise_for_status()
        about = r.json()
        if not pre and parse(about["info"]["version"]).is_prerelease:
            latest = max((v for v in map(parse, about["releases"])
                            if not v.is_prerelease), default=None)
            if latest is None:
                click.echo('qypi: {}: no stable versions available'
                           .format(pkgname), err=True)
                ok = False
                continue
            r = s.get('{}/{}/{}/json'.format(ENDPOINT, pkgname, latest))
            ### Will stringifying the parsed version string instead of using
            ### the original key from `about["releases"]` ever change the
            ### version string in a meaningful way?
            r.raise_for_status()
            about = r.json()
        pkg = about["info"]
        #releases = about["releases"]
        if long_description:
            click.echo_via_pager(pkg["description"])
        else:
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

if __name__ == '__main__':
    qypi()
