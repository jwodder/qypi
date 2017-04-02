- Give `info` and `files` an `--all-versions` option
- Give `info` an option for including the long description

- When fetching details for a package without specifying the version, it
  appears that Legacy PyPI returns information for the release with the highest
  version number, while Warehouse returns the most recent release.  Try to make
  ``qypi``'s behavior consistent here.
    - Give the relevant subcommands ``--newest`` and ``--highest`` options?
      (Default to ``--highest`` because ``--newest`` would fail if there have
      never been any uploads)
- Add `--no-pre` options?

- Improve the way messages printed to stderr interact with stdout

- When using a package name as a dictionary key in output, use the same casing
  as on the command line?
    - Normalize package names in output?
- Add examples to the README for every subcommand
