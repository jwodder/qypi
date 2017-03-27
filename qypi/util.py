import json
import click
from   .api import QyPIError

def parse_packages(ctx, packages, pre):
    ### TODO: Figure out a better way to integrate this with Click
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

def clean_pypi_dict(d):
    return {
        k: (None if v in ('', 'UNKNOWN') else v)
        for k,v in d.items() if not k.startswith(('cheesecake', '_pypi'))
    }
