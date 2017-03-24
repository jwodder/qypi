- It is possible for the "latest" version on PyPI to be a prerelease version.
  Handle this.
- Options to add:
    - `--pre` — include prereleases
    - `--index`
    - `--classifiers` / `--no-classifiers`
    - showing a list of all releases (sorted in version order) with their
      release dates
    - showing downloadable files (including URLs?)
    - showing download counts
    - getting the PyPI users associated with a package (via the XML-RPC API) ?
    - listing all of a user's packages (via the XML-RPC API)
    - output an array of JSON objects instead of a stream
    - controlling whether to add `people`/remove `author*` and `maintainer*` ?
- Support getting details for a specific version (at `/$pkg/$version/json`)
  rather than the latest one
- Parse `requires_dist` entries?
- Can `keywords` ever be a list?
