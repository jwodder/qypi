#!/usr/bin/python3
# Unlike the XML-RPC API, the JSON API accepts package names regardless of
# normalization

import json
#from   packaging.version import parse
import click
import requests

ENDPOINT = 'https://pypi.python.org/pypi'
#ENDPOINT = 'https://pypi.org/pypi'

#def is_prerelease(v):
#    return parse(v).is_prerelease

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-a', '--array', is_flag=True)
@click.option('-D', '--description', '--long-description', is_flag=True)
@click.argument('packages', nargs=-1)
@click.pass_context
def qypi(ctx, packages, array, long_description):
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
            if pkg.get('author') or pkg.get('author_email'):
                pkg["people"].append({
                    "name": pkg.get('author'),
                    "email": pkg.get('author_email'),
                    "role": "author",
                })
            if pkg.get('maintainer') or pkg.get('maintainer_email'):
                pkg["people"].append({
                    "name": pkg.get('maintainer'),
                    "email": pkg.get('maintainer_email'),
                    "role": "maintainer",
                })
            if array:
                pkgdata.append(pkg)
            else:
                print(json.dumps(pkg, sort_keys=True, indent=4))
    if array:
        print(json.dumps(pkgdata, sort_keys=True, indent=4))
    ctx.exit(0 if ok else 1)

if __name__ == '__main__':
    qypi()
