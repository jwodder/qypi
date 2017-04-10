- For arguments of the form `package==version`, use `packaging`'s version
  classes for the version comparison (This would involve an extra API call,
  though)
- When using a package name as a dictionary key in output, use the same casing
  as on the command line?
    - Normalize package names in output?
- Add examples to the README for every subcommand
- Write tests?
- Give `readme` an option for setting the pager
- Give `--all-versions` an `-a` (or `-A`?) short form?
    - Give `--latest-version` a short form?
- Set the user agent when using `requests`?
