from collections import defaultdict
from itertools import groupby
from operator import attrgetter
from typing import Dict, List, Optional, TextIO, Tuple
import click
from packaging.version import parse
from . import __version__
from .api import DEFAULT_ENDPOINT, QyPI, QyPIError
from .util import dumps, show_datetime

SEARCH_SYNONYMS = {
    "homepage": "home_page",
    "url": "home_page",
    "long_description": "description",
    "readme": "description",
    "keyword": "keywords",
}

pre_opt = click.option(
    "--pre/--no-pre",
    default=None,
    help="Show prerelease versions",
    show_default=True,
)

all_opt = click.option(
    "-A",
    "--all-versions/--latest-version",
    default=False,
    help="Show all versions/only the latest version when no version is"
    " specified [default: latest]",
)

sort_opt = click.option(
    "--newest/--highest",
    default=False,
    help='Does "latest" mean "newest" or "highest"? [default: highest]',
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-i",
    "--index-url",
    default=DEFAULT_ENDPOINT,
    metavar="URL",
    help="Set PyPI API endpoint URL",
    show_default=True,
)
@click.version_option(__version__, "-V", "--version", message="%(prog)s %(version)s")
@click.pass_context
def main(ctx: click.Context, index_url: str) -> None:
    """Query PyPI from the command line"""
    ctx.obj = ctx.with_resource(QyPI(index_url))


@main.command()
@click.option(
    "--description/--no-description",
    default=False,
    help="Include (long) descriptions",
    show_default=True,
)
@click.option(
    "--trust-downloads/--no-trust-downloads",
    default=False,
    help="Show download stats",
    show_default=True,
)
@all_opt
@sort_opt
@pre_opt
@click.argument("project")
@click.pass_obj
def info(
    qypi: QyPI,
    project: str,
    trust_downloads: bool,
    description: bool,
    all_versions: bool,
    newest: bool,
    pre: Optional[bool],
) -> None:
    """
    Show project details.

    Projects can be specified as either ``projectname`` to show the latest
    version or as ``projectname==version`` to show the details for ``version``.
    """
    if all_versions:
        try:
            vs = qypi.get_all_requirements(project, yanked=False, prereleases=pre)
        except QyPIError as e:
            raise click.UsageError(str(e))
        click.echo(
            dumps(
                [
                    v.qypi_json_dict(
                        description=description, trust_downloads=trust_downloads
                    )
                    for v in vs
                ]
            )
        )
    else:
        try:
            v = qypi.get_requirement(
                project, most_recent=newest, yanked=False, prereleases=pre
            )
        except QyPIError as e:
            raise click.UsageError(str(e))
        click.echo(
            dumps(
                v.qypi_json_dict(
                    description=description, trust_downloads=trust_downloads
                )
            )
        )


@main.command()
@sort_opt
@pre_opt
@click.argument("project")
@click.pass_obj
def readme(qypi: QyPI, project: str, newest: bool, pre: Optional[bool]) -> None:
    """
    View projects' long descriptions.

    If stdout is a terminal, the descriptions are passed to a pager program
    (e.g., `less(1)`).

    Projects can be specified as either ``projectname`` to show the latest
    version or as ``projectname==version`` to show the long description for
    ``version``.
    """
    v = qypi.get_requirement(project, most_recent=newest, yanked=False, prereleases=pre)
    if v.info.description is not None:
        click.echo_via_pager(v.info.description)
    else:
        click.echo_via_pager("--- no description ---")


@main.command()
@click.argument("project")
@click.pass_obj
def releases(qypi: QyPI, project: str) -> None:
    """List released project versions"""
    pkg = qypi.get_project(project)
    data: List[dict] = []
    for v in sorted(pkg.versions, key=parse):
        pv = pkg.get_version(v)
        data.append(
            {
                "version": v,
                "is_prerelease": parse(v).is_prerelease,
                "is_yanked": pv.is_yanked,
                "release_date": show_datetime(pv.upload_time),
                "release_url": pv.info.release_url,
            }
        )
    click.echo(dumps(data))


@main.command()
@click.option(
    "--trust-downloads/--no-trust-downloads",
    default=False,
    help="Show download stats",
    show_default=True,
)
@all_opt
@sort_opt
@pre_opt
@click.argument("project")
@click.pass_obj
def files(
    qypi: QyPI,
    project: str,
    trust_downloads: bool,
    all_versions: bool,
    newest: bool,
    pre: Optional[bool],
) -> None:
    """
    List files available for download.

    Projects can be specified as either ``projectname`` to show the latest
    version or as ``projectname==version`` to show the files available for
    ``version``.
    """
    if all_versions:
        vs = qypi.get_all_requirements(project, yanked=False, prereleases=pre)
        click.echo(
            dumps(
                {
                    v.info.version: [
                        f.json_dict(trust_downloads=trust_downloads, exclude_unset=True)
                        for f in v.files
                    ]
                    for v in vs
                }
            )
        )
    else:
        v = qypi.get_requirement(
            project, most_recent=newest, yanked=False, prereleases=pre
        )
        click.echo(
            dumps(
                [
                    f.json_dict(trust_downloads=trust_downloads, exclude_unset=True)
                    for f in v.files
                ]
            )
        )


@main.command("list")
@click.pass_obj
def listcmd(qypi: QyPI) -> None:
    """List all projects on PyPI"""
    for pkg in qypi.list_all_projects():
        click.echo(pkg)


@main.command()
@click.option(
    "--and",
    "oper",
    flag_value="and",
    default=True,
    help="AND conditions together [default]",
)
@click.option("--or", "oper", flag_value="or", help="OR conditions together")
@click.option(
    "-p/-r",
    "--projects/--releases",
    default=False,
    help="Show one result per project/per release [default: per release]",
)
@click.argument("terms", nargs=-1, required=True)
@click.pass_obj
def search(qypi: QyPI, terms: Tuple[str], oper: str, projects: bool) -> None:
    """
    Search PyPI for projects or releases thereof.

    Search terms may be specified as either ``field:value`` (e.g.,
    ``summary:Django``) or just ``value`` to search long descriptions.
    """
    spec: Dict[str, List[str]] = defaultdict(list)
    for t in terms:
        key, colon, value = t.partition(":")
        if colon == "":
            key, value = "description", t
        else:
            key = SEARCH_SYNONYMS.get(key, key)
        spec[key].append(value)
    results = qypi.search(dict(spec), oper)
    if projects:
        results = [
            max(versions, key=lambda v: parse(v.version))
            for _, versions in groupby(results, attrgetter("name"))
        ]
    click.echo(dumps(results))


@main.command()
@click.option("-f", "--file", type=click.File("r"))
@click.option(
    "-p/-r",
    "--projects/--releases",
    default=False,
    help="Show one result per project/per release [default: per release]",
)
@click.argument("classifiers", nargs=-1)
@click.pass_obj
def browse(
    qypi: QyPI, classifiers: Tuple[str, ...], file: Optional[TextIO], projects: bool
) -> None:
    """
    List projects with given trove classifiers.

    The list of classifiers may optionally be read from a file, one classifier
    per line.  Any further classifiers listed on the command line will be added
    to the file's list.
    """
    if file is not None:
        classifiers += tuple(map(str.strip, file))
    results = qypi.browse(list(classifiers))
    if projects:
        results = [
            max(versions, key=lambda v: parse(v.version))
            for _, versions in groupby(results, attrgetter("name"))
        ]
    click.echo(dumps(results))


@main.command()
@click.argument("project")
@click.pass_obj
def owner(qypi: QyPI, project: str) -> None:
    """List project owners & maintainers"""
    click.echo(dumps([pr.json_dict() for pr in qypi.get_project_roles(project)]))


@main.command()
@click.argument("user")
@click.pass_obj
def owned(qypi: QyPI, user: str) -> None:
    """List projects owned/maintained by a user"""
    click.echo(dumps([ur.json_dict() for ur in qypi.get_user_roles(user)]))


if __name__ == "__main__":
    main()
