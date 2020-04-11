from traceback     import format_exception
from click.testing import CliRunner
from qypi.__main__ import qypi

def show_result(r):
    if r.exception is not None:
        return ''.join(format_exception(*r.exc_info))
    else:
        return r.output

def test_list(mocker):
    spinstance = mocker.Mock(**{
        'list_packages.return_value': [
            'foobar',
            'BarFoo',
            'quux',
            'Gnusto-Cleesh',
            'XYZZY_PLUGH',
        ],
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(qypi, ['list'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        'foobar\n'
        'BarFoo\n'
        'quux\n'
        'Gnusto-Cleesh\n'
        'XYZZY_PLUGH\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [mocker.call.list_packages()]

def test_owner(mocker):
    spinstance = mocker.Mock(**{
        'package_roles.return_value': [
            ['Owner', 'luser'],
            ['Maintainer', 'jsmith'],
        ],
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(qypi, ['owner', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '{\n'
        '    "foobar": [\n'
        '        {\n'
        '            "role": "Owner",\n'
        '            "user": "luser"\n'
        '        },\n'
        '        {\n'
        '            "role": "Maintainer",\n'
        '            "user": "jsmith"\n'
        '        }\n'
        '    ]\n'
        '}\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [mocker.call.package_roles('foobar')]

def test_owned(mocker):
    spinstance = mocker.Mock(**{
        'user_packages.return_value': [
            ['Owner', 'foobar'],
            ['Maintainer', 'quux'],
        ],
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(qypi, ['owned', 'luser'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '{\n'
        '    "luser": [\n'
        '        {\n'
        '            "package": "foobar",\n'
        '            "role": "Owner"\n'
        '        },\n'
        '        {\n'
        '            "package": "quux",\n'
        '            "role": "Maintainer"\n'
        '        }\n'
        '    ]\n'
        '}\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [mocker.call.user_packages('luser')]

def test_search(mocker):
    spinstance = mocker.Mock(**{
        'search.return_value': [
            {
                "name": "foobar",
                "version": "1.2.3",
                "summary": "Foo all your bars",
                "_pypi_ordering": False,
            },
            {
                "name": "quux",
                "version": "0.1.0",
                "summary": "Do that thing this does",
                "_pypi_ordering": True,
            },
            {
                "name": "gnusto",
                "version": "0.0.0",
                "summary": "",
                "_pypi_ordering": False,
            },
        ],
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(qypi, ['search', 'term', 'keyword:foo', 'readme:bar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "name": "foobar",\n'
        '        "summary": "Foo all your bars",\n'
        '        "version": "1.2.3"\n'
        '    },\n'
        '    {\n'
        '        "name": "quux",\n'
        '        "summary": "Do that thing this does",\n'
        '        "version": "0.1.0"\n'
        '    },\n'
        '    {\n'
        '        "name": "gnusto",\n'
        '        "summary": null,\n'
        '        "version": "0.0.0"\n'
        '    }\n'
        ']\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [
        mocker.call.search(
            {"description": ["term", "bar"], "keywords": ["foo"]},
            'and',
        )
    ]

def test_browse(mocker):
    spinstance = mocker.Mock(**{
        'browse.return_value': [
            ['foobar', '1.2.3'],
            ['foobar', '1.2.2'],
            ['foobar', '1.2.1'],
            ['foobar', '1.2.0'],
            ['quux', '0.1.0'],
            ['gnusto', '0.0.0'],
        ],
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(
        qypi,
        ['browse', 'Typing :: Typed', 'Topic :: Utilities'],
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "name": "foobar",\n'
        '        "version": "1.2.3"\n'
        '    },\n'
        '    {\n'
        '        "name": "foobar",\n'
        '        "version": "1.2.2"\n'
        '    },\n'
        '    {\n'
        '        "name": "foobar",\n'
        '        "version": "1.2.1"\n'
        '    },\n'
        '    {\n'
        '        "name": "foobar",\n'
        '        "version": "1.2.0"\n'
        '    },\n'
        '    {\n'
        '        "name": "quux",\n'
        '        "version": "0.1.0"\n'
        '    },\n'
        '    {\n'
        '        "name": "gnusto",\n'
        '        "version": "0.0.0"\n'
        '    }\n'
        ']\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [
        mocker.call.browse(('Typing :: Typed', 'Topic :: Utilities'))
    ]

def test_browse_packages(mocker):
    spinstance = mocker.Mock(**{
        'browse.return_value': [
            ['foobar', '1.2.3'],
            ['foobar', '1.2.2'],
            ['foobar', '1.2.1'],
            ['foobar', '1.2.0'],
            ['quux', '0.1.0'],
            ['gnusto', '0.0.0'],
        ],
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(
        qypi,
        ['browse', '--packages', 'Typing :: Typed', 'Topic :: Utilities'],
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "name": "foobar",\n'
        '        "version": "1.2.3"\n'
        '    },\n'
        '    {\n'
        '        "name": "quux",\n'
        '        "version": "0.1.0"\n'
        '    },\n'
        '    {\n'
        '        "name": "gnusto",\n'
        '        "version": "0.0.0"\n'
        '    }\n'
        ']\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [
        mocker.call.browse(('Typing :: Typed', 'Topic :: Utilities'))
    ]

def test_info(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "classifiers": [\n'
        '            "Topic :: Software Development :: Testing",\n'
        '            "UNKNOWN"\n'
        '        ],\n'
        '        "name": "foobar",\n'
        '        "people": [\n'
        '            {\n'
        '                "email": "megan30@daniels.info",\n'
        '                "name": "Brandon Perkins",\n'
        '                "role": "author"\n'
        '            },\n'
        '            {\n'
        '                "email": "cspencer@paul-fisher.com",\n'
        '                "name": "Denise Adkins",\n'
        '                "role": "maintainer"\n'
        '            }\n'
        '        ],\n'
        '        "platform": "Amiga",\n'
        '        "project_url": "https://dummy.nil/pypi/foobar",\n'
        '        "release_date": "2019-02-01T09:17:59.172284Z",\n'
        '        "release_url": "https://dummy.nil/pypi/foobar/1.0.0",\n'
        '        "summary": "Including drive environment my it.",\n'
        '        "unknown_field": "passed through",\n'
        '        "url": "https://www.johnson.com/homepage.php",\n'
        '        "version": "1.0.0"\n'
        '    }\n'
        ']\n'
    )

# Test `owner` with multiple arguments
# Test `owned` with multiple arguments
