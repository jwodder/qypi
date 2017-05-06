v0.4.0 (in development)
-----------------------
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
