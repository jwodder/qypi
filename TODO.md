- Options to add:
    - `--index-url`
        - Support setting via a `PIP_INDEX_URL`(?) environment variable
    - showing a list of all releases (sorted in version order) with their
      release dates
    - showing downloadable files (including URLs?)
    - showing download counts
    - getting the PyPI users associated with a package (via the XML-RPC API) ?
    - listing all of a user's packages (via the XML-RPC API)
    - controlling whether to add `people`/remove `author*` and `maintainer*` ?
- Support getting details for a specific version (at `/$pkg/$version/json`)
  rather than the latest one
- Parse `requires_dist` entries?
- Add docstrings and `--help` output
- Support searching PyPI via the XML-RPC API?
    - support listing packages matching given classifiers
    - support listing all packages
- Write a `setup.py`?
