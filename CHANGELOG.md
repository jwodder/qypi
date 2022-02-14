v1.0.0 (in development)
-----------------------
- Package data returned from the JSON API is now internally represented by
  [pydantic](https://github.com/samuelcolvin/pydantic)-based classes.  As a
  result, unknown fields returned by the JSON API are no longer output, and
  there may be some errors interacting with non-Warehouse project indices that
  do not define all of the same fields as Warehouse.  [Please report any
  instances of the latter.](https://github.com/jwodder/qypi/issues)
- The `info`, `readme`, `releases`, `files`, `owner`, and `owned` commands now
  take exactly one positional argument, and the output formats of many of these
  commands have been simplified for this case
- The `readme` command no longer takes an `--all-versions`/`-A` option
- The output from the `releases` command now includes an `is_yanked` field
- The `--packages` option to the `search` and `browse` commands is now named
  `--projects`
- The output from the `owned` command has changed to use the more accurate
  "project" instead of "package".
- Output timestamps now use `+00:00` as the timezone offset instead of `Z`
- Honor yanking (PEP 592)
    - Yanked versions are no longer shown by default
    - The `info`, `readme`, and `files` commands now have
      `--yanked`/`--no-yanked` options for controlling whether to display
      yanked versions
- Support Python 3.10, 3.11, and 3.12
- Drop support for Python 3.6

v0.6.0 (2021-05-31)
-------------------
- Support Python 3.8 and 3.9
- `"release_date"` fields are now derived from `"upload_time_iso_8601"` fields
  instead of `"upload_time"`.  They thus now include microseconds and the
  timezone.
- Drop support for Python 3.4 and 3.5
- Support PyPy3
- Update Click to 8.0

v0.5.0 (2019-05-18)
-------------------
- `search` now accepts `homepage` and `keyword` as synonyms of `home_page` and
  `keywords`, respectively
- When getting the latest version of a package that only has prereleases, now
  show information on the latest prerelease instead of erroring when `--pre`
  isn't given

v0.4.1 (2017-05-15)
-------------------
- **Bugfix**: Better handling of package versions that aren't in PEP 440
  normalized form

v0.4.0 (2017-05-07)
-------------------
- Gave `browse` and `search` `--packages` and `--releases` options for
  controlling whether to show one result per matching package or per matching
  package release
- **Bugfix**: An error message will now be displayed for each nonexistent
  package/version given on the command line, not just the first one

v0.3.0 (2017-04-14)
-------------------
- Gave `info`, `readme`, and `files` an `-A`/`--all-versions` option
- Gave `info` a `--description` option for including (long) descriptions

v0.2.0 (2017-04-03)
-------------------
- Gave `info`, `readme`, and `files` `--newest` and `--highest` options for
  controlling how the latest version of a package is determined; `--highest` is
  now always the default
- Added a `--no-pre` option for negating `--pre`

v0.1.0 (2017-04-01)
-------------------
Initial release
