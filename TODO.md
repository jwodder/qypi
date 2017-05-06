- For arguments of the form `package==version`, use `packaging`'s version
  classes for the version comparison (This would involve an extra API call,
  though)
- When using a package name as a dictionary key in output, use the same casing
  as on the command line?
    - Normalize package names in output?
- Add examples to the README for every subcommand
- Write tests?
- Give `--latest-version` a short form?
- Give `releases` an option for sorting by release date?
- Try to make the use of "release" vs. "version" consistent
    - Give `releases` a `versions` synonym?
    - Rename `releases` to `versions`?
