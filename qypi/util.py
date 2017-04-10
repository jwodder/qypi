import json
import re
import click

def obj_option(*args, **kwargs):
    """
    Like `click.option`, but sets an attribute on ``ctx.obj`` instead of
    creating a parameter
    """
    def callback(ctx, param, value):
        setattr(ctx.obj, param.name, value)
    return click.option(*args, callback=callback, expose_value=False, **kwargs)

pre_opt = obj_option(
    '--pre/--no-pre',
    default=False,
    help='Show prerelease versions',
    show_default=True,
)

all_opt = obj_option(
    '--all-versions/--latest-version',
    default=False,
    help='Show all versions/only the latest version when no version is specified [default: latest]',
)

sort_opt = obj_option(
    '--newest/--highest',
    default=False,
    help='Does "latest" mean "newest" or "highest"? [default: highest]',
)

def package_args(versioned=True):
    if versioned:
        def wrapper(f):
            return all_opt(pre_opt(sort_opt(click.argument(
                'packages',
                nargs=-1,
                callback=lambda ctx, param, value:
                            ctx.obj.lookup_package_version(value),
            )(f))))
        return wrapper
    else:
        return click.argument(
            'packages',
            nargs=-1,
            callback=lambda ctx, param, value: ctx.obj.lookup_package(value),
        )

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
