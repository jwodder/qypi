- For arguments of the form `package==version`, use `packaging`'s version
  classes for the version comparison (falling back to string comparison in the
  pathological case of two different releases with equivalent versions)
    - Support full PEP 440 version specifiers?
- When using a package name as a dictionary key in output, use the same casing
  as on the command line?
    - Normalize package names in output?
- Add examples to the README for every subcommand
- Write tests
- Give `--latest-version` a short form?
- Give `releases` an option for sorting by release date?
- Try to make the use of "release" vs. "version" consistent
    - Give `releases` a `versions` synonym?
    - Rename `releases` to `versions`?
- Change the output formats of `releases`, `owner`, and `owned` to be lists of
  objects, each of which has a `package`/`name`/`user` field giving what was
  formerly the entry's key and another field for what was formerly the value?
- Add a `-q`/`--quiet` option for suppressing errors about missing
  packages/versions
- Honor package yanking (PEP 592)
