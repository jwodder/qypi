.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP - Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://img.shields.io/github/license/jwodder/qypi.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/qypi>`_
| `Issues <https://github.com/jwodder/qypi/issues>`_

``qypi`` is a command-line client for querying & searching `PyPI
<https://pypi.python.org>`_ for Python package information and outputting JSON
(with some minor opinionated changes to the output data structures; see the
examples below).


Installation
============
``qypi`` requires Python 3.4 or newer.  Just use `pip <https://pip.pypa.io/>`_
for Python 3 (You have pip, right?) to install ``qypi`` and its dependencies::

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

    $ qypi releases in_place
    {
        "in-place": [
            {
                "is_prerelease": false,
                "release_date": "2017-01-27T23:41:06",
                "release_url": "https://pypi.org/project/in-place/0.1.1",
                "version": "0.1.1"
            },
            {
                "is_prerelease": false,
                "release_date": "2017-02-23T16:49:00",
                "release_url": "https://pypi.org/project/in-place/0.2.0",
                "version": "0.2.0"
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
These subcommands show information for specific package releases/versions.  By
default, they use the most recent release of each package (excluding prerelease
versions unless the ``--pre`` option is given); specific releases can be
queried with arguments of the form ``package==version`` (e.g., ``qypi info
qypi==0.1.0``).

``info``
^^^^^^^^

::

    qypi info [--pre] [--trust-downloads] <package[==version]> ...

Show basic information about the given package releases.  Download counts are
omitted because `the feature is currently broken & unreliable
<https://github.com/pypa/pypi-legacy/issues/396>`_; use the
``--trust-downloads`` option if you want to see the values anyway.

Example::

    $ qypi info requests
    [
        {
            "bugtrack_url": null,
            "classifiers": [
                "Development Status :: 5 - Production/Stable",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: Apache Software License",
                "Natural Language :: English",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2.6",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.3",
                "Programming Language :: Python :: 3.4",
                "Programming Language :: Python :: 3.5",
                "Programming Language :: Python :: 3.6",
                "Programming Language :: Python :: Implementation :: CPython",
                "Programming Language :: Python :: Implementation :: PyPy"
            ],
            "docs_url": null,
            "download_url": null,
            "keywords": null,
            "license": "Apache 2.0",
            "name": "requests",
            "people": [
                {
                    "email": "me@kennethreitz.com",
                    "name": "Kenneth Reitz",
                    "role": "author"
                }
            ],
            "platform": null,
            "project_url": "https://pypi.org/project/requests/",
            "release_date": "2017-01-24T12:53:25",
            "release_url": "https://pypi.org/project/requests/2.13.0/",
            "requires_python": null,
            "summary": "Python HTTP for Humans.",
            "url": "http://python-requests.org",
            "version": "2.13.0"
        }
    ]


``readme``
^^^^^^^^^^

::

    qypi readme [--pre] <package[==version]> ...

Display the given package releases' long descriptions in a pager one at a time.
``list`` and ``readme`` are the only subcommands that do not output JSON.

``files``
^^^^^^^^^

::

    qypi files [--pre] [--trust-downloads] <package[==version]> ...

List files available for download for the given package releases.  Download
counts are omitted because `the feature is currently broken & unreliable
<https://github.com/pypa/pypi-legacy/issues/396>`_; use the
``--trust-downloads`` option if you want to see the values anyway.

Example::

    $ qypi files requests
    [
        {
            "files": [
                {
                    "comment_text": "",
                    "digests": {
                        "md5": "5e432dcf5bd1e3402ea1656700d99365",
                        "sha256": "1a720e8862a41aa22e339373b526f508ef0c8988baf48b84d3fc891a8e237efb"
                    },
                    "filename": "requests-2.13.0-py2.py3-none-any.whl",
                    "has_sig": false,
                    "md5_digest": "5e432dcf5bd1e3402ea1656700d99365",
                    "packagetype": "bdist_wheel",
                    "python_version": "py2.py3",
                    "size": 584556,
                    "upload_time": "2017-01-24T12:53:25",
                    "url": "https://files.pythonhosted.org/packages/7e/ac/a80ed043485a3764053f59ca92f809cc8a18344692817152b0e8bd3ca891/requests-2.13.0-py2.py3-none-any.whl"
                },
                {
                    "comment_text": "",
                    "digests": {
                        "md5": "921ec6b48f2ddafc8bb6160957baf444",
                        "sha256": "5722cd09762faa01276230270ff16af7acf7c5c45d623868d9ba116f15791ce8"
                    },
                    "filename": "requests-2.13.0.tar.gz",
                    "has_sig": false,
                    "md5_digest": "921ec6b48f2ddafc8bb6160957baf444",
                    "packagetype": "sdist",
                    "python_version": "source",
                    "size": 557508,
                    "upload_time": "2017-01-24T12:53:28",
                    "url": "https://files.pythonhosted.org/packages/16/09/37b69de7c924d318e51ece1c4ceb679bf93be9d05973bb30c35babd596e2/requests-2.13.0.tar.gz"
                }
            ],
            "name": "requests",
            "version": "2.13.0"
        }
    ]
