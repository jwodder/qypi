v0.6.1 (in development)
-----------------------
- Support Python 3.10, 3.11, 3.12, and 3.13
- Migrated from setuptools to hatch
- Drop support for Python 3.6, 3.7, 3.8, and 3.9
- Exclude click v8.2.2 from dependencies due to breakage caused by
  https://github.com/pallets/click/issues/3024

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
