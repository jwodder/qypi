- Options to add:
    - `--repository`/`-r` — support for `~/.pypirc` files
        - See <https://docs.python.org/3/distutils/packageindex.html#pypirc>
    - `--[no-]trust-downloads` — showing download counts
- Add docstrings and `--help` output
- Write a `setup.py`?

- `info`:
    - Add an `--all-versions` option?
    - Add an option for including the long description?
    - Make `--array` the default/only behavior?
    - Parse/explode `requires_dist` entries?
- `releases`:
    - Add a `--map` option for merging the output into a single JSON object
        - Make it the default/only behavior?
    - Rethink name; "`versions`"? "`history`"?

- Subcommands to add:
    - `files [--pre] <package>[=version] ...` — list files available for
      download for the given versions of the given packages as JSON
        - Add an `--all-versions` option?
    - `search [--and|--or] <field>:<value> ...`
        - If the field is omitted from an argument, implicitly set it to
          `description` (or `summary`?)
        - Allow the field `url` as a synonym of `home_page`?
    - `browse <classifier> ...`
        - Add an option for reading the list of classifiers from a file/stdin
    - `listall` — outputs the name of each & every package, one per line
        - Rethink name; "`all`"? "`everything`"?
    - `users <package> ...` — list users & roles for packages
        - Rename to "`roles`"?
    - `??? [--owner|--maintainer] <user> ...` - list packages & roles for users
