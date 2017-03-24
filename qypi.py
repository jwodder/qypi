#!/usr/bin/python3
# Unlike the XML-RPC API, the JSON API accepts package names regardless of
# normalization

#__requires__ = ['packaging']
import json
import sys
#from   packaging.version import parse
import requests

ENDPOINT = 'https://pypi.python.org/pypi'
#ENDPOINT = 'https://pypi.org/pypi'

#def is_prerelease(v):
#    return parse(v).is_prerelease

s = requests.Session()
for pkgname in sys.argv[1:]:
    r = s.get(ENDPOINT + '/' + pkgname + '/json')
    if r.status_code == 404:
        print('{}: {}: package not found'.format(sys.argv[0], pkgname),
              file=sys.stderr)
    r.raise_for_status()
    about = r.json()
    pkg = about["info"]
    releases = about["releases"]

    for k,v in list(pkg.items()):
        if k.startswith(('cheesecake', '_pypi')):
            del pkg[k]
        elif v in ('', 'UNKNOWN'):
            pkg[k] = None

    pkg.pop('description', None)
    pkg.pop('downloads', None)
    pkg["url"] = pkg.pop('home_page', None)
    pkg["release_date"] = min((obj["upload_time"] for obj in about["urls"]),
                              default=None)

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

    print(json.dumps(pkg, sort_keys=True, indent=4))
