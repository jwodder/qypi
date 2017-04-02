import json
import re
import click
from   .api import QyPIError

def parse_packages(ctx, packages, pre=False, newest=False, versioned=True):
    ### TODO: Figure out a better way to integrate this with Click
    ok = True
    for pkgname in packages:
        try:
            if versioned:
                name, eq, version = pkgname.partition('=')
                if eq == '':
                    pkg = ctx.obj.get_latest_version(name, pre, newest)
                else:
                    pkg = ctx.obj.get_version(name, version.lstrip('='))
            else:
                pkg = ctx.obj.get_package(pkgname)
        except QyPIError as e:
            click.echo(ctx.command_path + ': ' + str(e), err=True)
            ok = False
        else:
            yield pkg
    if not ok:
        ctx.exit(1)

def dumps(obj):
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)

def clean_pypi_dict(d):
    return {
        k: (None if v in ('', 'UNKNOWN') else v)
        for k,v in d.items() if not k.startswith(('cheesecake', '_pypi'))
    }


class JSONLister:
    def __init__(self):
        self.first = True

    def __enter__(self):
        click.echo('[', nl=False)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.first:
            click.echo()
        click.echo(']')
        return False

    def append(self, obj):
        if self.first:
            click.echo()
            self.first = False
        else:
            click.echo(',')
        click.echo(re.sub(r'^', '    ', dumps(obj), flags=re.M), nl=False)


class JSONMapper:
    def __init__(self):
        self.first = True

    def __enter__(self):
        click.echo('{', nl=False)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.first:
            click.echo()
        click.echo('}')
        return False

    def append(self, key, value):
        if self.first:
            click.echo()
            self.first = False
        else:
            click.echo(',')
        click.echo(
            re.sub(r'^', '    ', json.dumps(key)+': '+dumps(value), flags=re.M),
            nl=False,
        )
