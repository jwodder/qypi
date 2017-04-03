.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://img.shields.io/pypi/pyversions/qypi.svg
    :target: https://pypi.python.org/pypi/qypi

.. image:: https://img.shields.io/github/license/jwodder/qypi.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/qypi>`_
| `PyPI <https://pypi.python.org/pypi/qypi>`_
| `Issues <https://github.com/jwodder/qypi/issues>`_

``qypi`` is a command-line client for querying & searching `the Python Package
Index <https://pypi.python.org>`_ for Python package information and outputting
JSON (with some minor opinionated changes to the output data structures; see
the examples below).


Installation
============
``qypi`` requires Python 3.4 or newer.  Just use version 6.0 or higher of `pip
<https://pip.pypa.io/>`_ for Python 3 (You have pip, right?) to install
``qypi`` and its dependencies::

    pip3 install qypi


Usage
=====

::

    qypi [-i|--index-url <URL>] <command> [<options>] [<arguments>]

Global Option
-------------

- ``-i <URL>``, ``--index-url <URL>`` — Query the Python package server at the
  given URL, which must support both the `XML-RPC
  <http://wiki.python.org/moin/PyPIXmlRpc>`_ and `JSON
  <http://wiki.python.org/moin/PyPIJSON>`_ APIs.  By default, ``qypi`` queries
  `Warehouse <https://pypi.org>`_ at ``https://pypi.org/pypi``; to use the
  current/legacy PyPI instance instead, set the index URL to
  ``https://pypi.python.org/pypi``.


List Packages
-------------

``list``
^^^^^^^^

::

    qypi list

List all packages registered on PyPI, one per line, in the order that they are
returned by the API.  ``list`` and ``readme`` are the only subcommands that do
not output JSON.

``search``
^^^^^^^^^^

::

    qypi search [--and|--or] <term> ...

Search PyPI for package releases matching the given search terms.  Search terms
consist of a field name and a value separated by a colon; a term without a
colon searches the ``description`` field.  As documented `here
<https://wiki.python.org/moin/PyPIXmlRpc>`_, the supported searchable fields
are:

- ``name``
- ``version``
- ``author``
- ``author_email``
- ``maintainer``
- ``maintainer_email``
- ``home_page`` (alias: ``url``)
- ``license``
- ``summary``
- ``description`` (aliases: ``long_description`` and ``readme``)
- ``keywords``
- ``platform``
- ``download_url``

All other fields are ignored.

Multiple search terms referring to the same field are combined with logical OR.
Search terms on different fields are combined according to whether ``--and`` or
``--or`` is specified on the command line; the default behavior is ``--and``.

``browse``
^^^^^^^^^^

::

    qypi browse [-f|--file <file>] <classifier> ...

List package releases with the given `trove classifiers
<https://pypi.python.org/pypi?%3Aaction=list_classifiers>`_.  Because
classifiers are not the most command-line friendly thing in the world, they may
optionally be read from a file, one classifier per line.  Any further
classifiers listed on the command line will be added to the file's list.

``owned``
^^^^^^^^^

::

    qypi owned <user> ...

List packages owned or maintained by the given PyPI users


Package Information
-------------------

``releases``
^^^^^^^^^^^^

::

    qypi releases <package> ...

List the released versions for the given packages in PEP 440 order

Example::

    $ qypi releases qypi
    {
        "qypi": [
            {
                "is_prerelease": false,
                "release_date": "2017-04-02T03:07:42",
                "release_url": "https://pypi.org/project/qypi/0.1.0",
                "version": "0.1.0"
            },
            {
                "is_prerelease": false,
                "release_date": "2017-04-02T03:32:44",
                "release_url": "https://pypi.org/project/qypi/0.1.0.post1",
                "version": "0.1.0.post1"
            }
        ]
    }

A release's release date is the time at which its first file was uploaded.  If
there are no files associated with a release, its release date will be
``null``.

``owner``
^^^^^^^^^

::

    qypi owner <package> ...

List the PyPI users that own and/or maintain the given packages

Example::

    $ qypi owner requests
    {
        "requests": [
            {
                "role": "Owner",
                "user": "graffatcolmingov"
            },
            {
                "role": "Owner",
                "user": "kennethreitz"
            },
            {
                "role": "Owner",
                "user": "Lukasa"
            },
            {
                "role": "Maintainer",
                "user": "graffatcolmingov"
            },
            {
                "role": "Maintainer",
                "user": "Lukasa"
            },
            {
                "role": "Maintainer",
                "user": "nateprewitt"
            }
        ]
    }

Release Information
-------------------
These subcommands show information for specific package releases/versions.
Arguments can be in the form ``package==version`` (e.g., ``qypi info
qypi==0.1.0``) in order to query the given version of the given package; or
they can be just a package name in order to query (by default) the
highest-numbered non-prerelease version of the package.  Package-only arguments
can be made to refer to the most recently-released version (as determined by
file upload times) instead of the highest-numbered by specifying the
``--newest`` option on the command line, and prerelease versions can be added
to consideration with the ``--pre`` option.  These options can be negated back
to the default behavior with the ``--highest`` and ``--no-pre`` options,
respectively.

``info``
^^^^^^^^

::

    qypi info [--pre|--no-pre] [--newest|--highest] [--trust-downloads] <package[==version]> ...

Show basic information about the given package releases.  Download counts are
omitted because `the feature is currently broken & unreliable
<https://github.com/pypa/pypi-legacy/issues/396>`_; use the
``--trust-downloads`` option if you want to see the values anyway.

Example::

    $ qypi info qypi
    [
        {
            "bugtrack_url": null,
            "classifiers": [
                "Development Status :: 4 - Beta",
                "Environment :: Console",
                "Intended Audience :: Developers",
                "Intended Audience :: Information Technology",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.4",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: 3 :: Only",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "Topic :: System :: Software Distribution"
            ],
            "docs_url": null,
            "download_url": null,
            "keywords": "pypi warehouse search packages pip",
            "license": "MIT",
            "name": "qypi",
            "people": [
                {
                    "email": "qypi@varonathe.org",
                    "name": "John Thorvald Wodder II",
                    "role": "author"
                }
            ],
            "platform": null,
            "project_url": "https://pypi.org/project/qypi/",
            "release_date": "2017-04-02T03:32:44",
            "release_url": "https://pypi.org/project/qypi/0.1.0.post1/",
            "requires_python": "~=3.4",
            "summary": "Query PyPI from the command line",
            "url": "https://github.com/jwodder/qypi",
            "version": "0.1.0.post1"
        }
    ]

``readme``
^^^^^^^^^^

::

    qypi readme [--pre|--no-pre] [--newest|--highest] <package[==version]> ...

Display the given package releases' long descriptions in a pager one at a time.
``list`` and ``readme`` are the only subcommands that do not output JSON.

``files``
^^^^^^^^^

::

    qypi files [--pre|--no-pre] [--newest|--highest] [--trust-downloads] <package[==version]> ...

List files available for download for the given package releases.  Download
counts are omitted because `the feature is currently broken & unreliable
<https://github.com/pypa/pypi-legacy/issues/396>`_; use the
``--trust-downloads`` option if you want to see the values anyway.

Example::

    $ qypi files qypi
    [
        {
            "files": [
                {
                    "comment_text": "",
                    "digests": {
                        "md5": "58863d77e19bf4aa1ae85026cc1ff0f6",
                        "sha256": "5946a4557550479af90278e5418cd2c32a2626936075078a4c7096be52d43078"
                    },
                    "filename": "qypi-0.1.0.post1-py3-none-any.whl",
                    "has_sig": true,
                    "md5_digest": "58863d77e19bf4aa1ae85026cc1ff0f6",
                    "packagetype": "bdist_wheel",
                    "python_version": "py3",
                    "size": 13590,
                    "upload_time": "2017-04-02T03:32:44",
                    "url": "https://files.pythonhosted.org/packages/f9/3f/6b184713e79da15cd451f0dab91864633175242f4d321df0cacdd2dc8300/qypi-0.1.0.post1-py3-none-any.whl"
                },
                {
                    "comment_text": "",
                    "digests": {
                        "md5": "bfd357b3df2c2f1cbb6d23ff7c61fbb9",
                        "sha256": "c99eea315455cf9fde722599ab67eeefdff5c184bb3861a7fd82f8a9387c252d"
                    },
                    "filename": "qypi-0.1.0.post1.tar.gz",
                    "has_sig": true,
                    "md5_digest": "bfd357b3df2c2f1cbb6d23ff7c61fbb9",
                    "packagetype": "sdist",
                    "python_version": "source",
                    "size": 8975,
                    "upload_time": "2017-04-02T03:32:46",
                    "url": "https://files.pythonhosted.org/packages/0e/49/3056ee68b44c8eab4d4698b52ae4d18c0db92c80abc312894c02c4722621/qypi-0.1.0.post1.tar.gz"
                }
            ],
            "name": "qypi",
            "version": "0.1.0.post1"
        }
    ]
