- Options to add:
    - `--repository`/`-r` — support for `~/.pypirc` files
        - See <https://docs.python.org/3/distutils/packageindex.html#pypirc>
    - showing a list of all releases (sorted in version order) with their
      release dates
        - Output format for each package:

                {
                    "name": "package_name",
                    "releases": [
                        {
                            "is_prerelease": False,
                            "release_date": <TIMESTAMP>|null,
                            "release_url": ... ,  # ?
                            "version": "0.1.0"
                        }
                        ...
                    ]
                }

    - showing downloadable files (including URLs?)
    - showing download counts
    - getting the PyPI users associated with a package (via the XML-RPC API) ?
    - listing all of a user's packages (via the XML-RPC API)
- Support getting details for a specific version (at `/$pkg/$version/json`)
  rather than the latest one
- Parse `requires_dist` entries?
- Add docstrings and `--help` output
- Support searching PyPI via the XML-RPC API
    - support listing packages matching given classifiers
    - support listing all packages
- Write a `setup.py`?
- Make `--array` the default behavior?

- idea: Break into subcommands:
    - `info [--pre] <package>[=version] ...` — Show info for latest/given
      versions of packages as JSON
        - Add an `--all-versions` option?
        - Add an option for including the long description?
        - Rename to "`show`"?
    - `releases <package> ...` — list all releases of the given packages as
      JSON
        - Rethink name; "`versions`"? "`history`"?
    - `files [--pre] <package>[=version] ...` — list files available for
      download for the given versions of the given packages as JSON
        - Add an `--all-versions` option?
    - `readme [--pre] <package>[=version]` — show package long descriptions in
      pager

    - `search [--and|--or] <field>:<value> ...`
        - If the field is omitted from an argument, implicitly set it to
          `description` (or `summary`?)
        - Allow the field `url` as a synonym of `home_page`?
    - `browse <classifier> ...`
        - Add an option for reading the list of classifiers from a file/stdin
    - `listall` — outputs the name of each & every package, one per line
        - Rethink name; "`all`"? "`everything`"?
    - `users <package> ...` — list users & roles for packages
    - `??? [--owner|--maintainer] <user> ...` - list packages & roles for users
