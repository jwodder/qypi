import json
from   traceback     import format_exception
from   click.testing import CliRunner
from   qypi.__main__ import qypi

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

def test_multiple_owner(mocker):
    package_roles_iter = iter([
        [
            ['Owner', 'luser'],
            ['Maintainer', 'jsmith'],
        ],
        [
            ['Owner', 'jsmith'],
            ['Owner', 'froody'],
        ],
    ])
    spinstance = mocker.Mock(**{
        'package_roles.side_effect': lambda _: next(package_roles_iter),
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(qypi, ['owner', 'foobar', 'Glarch'])
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
        '    ],\n'
        '    "Glarch": [\n'
        '        {\n'
        '            "role": "Owner",\n'
        '            "user": "jsmith"\n'
        '        },\n'
        '        {\n'
        '            "role": "Owner",\n'
        '            "user": "froody"\n'
        '        }\n'
        '    ]\n'
        '}\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [
        mocker.call.package_roles('foobar'),
        mocker.call.package_roles('Glarch'),
    ]

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

def test_multiple_owned(mocker):
    user_packages_iter = iter([
        [
            ['Owner', 'foobar'],
            ['Maintainer', 'quux'],
        ],
        [
            ['Maintainer', 'foobar'],
            ['Owner', 'Glarch'],
        ],
    ])
    spinstance = mocker.Mock(**{
        'user_packages.side_effect': lambda _: next(user_packages_iter),
    })
    spclass = mocker.patch('qypi.api.ServerProxy', return_value=spinstance)
    r = CliRunner().invoke(qypi, ['owned', 'luser', 'jsmith'])
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
        '    ],\n'
        '    "jsmith": [\n'
        '        {\n'
        '            "package": "foobar",\n'
        '            "role": "Maintainer"\n'
        '        },\n'
        '        {\n'
        '            "package": "Glarch",\n'
        '            "role": "Owner"\n'
        '        }\n'
        '    ]\n'
        '}\n'
    )
    spclass.assert_called_once_with('https://pypi.org/pypi')
    assert spinstance.method_calls == [
        mocker.call.user_packages('luser'),
        mocker.call.user_packages('jsmith'),
    ]

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

def test_info_explicit_latest_version(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'foobar==1.0.0'])
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

def test_info_explicit_version(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'foobar==0.2.0'])
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
        '                "email": "danielstewart@frye.com",\n'
        '                "name": "Sonya Johnson",\n'
        '                "role": "author"\n'
        '            },\n'
        '            {\n'
        '                "email": "maynardtim@hotmail.com",\n'
        '                "name": "Stephen Romero",\n'
        '                "role": "maintainer"\n'
        '            }\n'
        '        ],\n'
        '        "platform": "Wood",\n'
        '        "project_url": "https://dummy.nil/pypi/foobar",\n'
        '        "release_date": "2017-02-04T12:34:05.766270Z",\n'
        '        "release_url": "https://dummy.nil/pypi/foobar/0.2.0",\n'
        '        "summary": "Water audience cut call.",\n'
        '        "unknown_field": "passed through",\n'
        '        "url": "http://www.sanchez.net/index.htm",\n'
        '        "version": "0.2.0"\n'
        '    }\n'
        ']\n'
    )

def test_info_description(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', '--description', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "classifiers": [\n'
        '            "Topic :: Software Development :: Testing",\n'
        '            "UNKNOWN"\n'
        '        ],\n'
        '        "description": "foobar v1.0.0\\n\\nDream political close attorney sit cost inside. Seek hard can bad investment authority walk we. Sing range late use speech citizen.\\n\\nCan money issue claim onto really case. Fact garden along all book sister trip step.\\n\\nView table woman her production result. Fine allow prepare should traditional. Send cultural two care eye.\\n\\nGenerated with Faker",\n'  # noqa: B950
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

def test_multiple_info(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'has-prerel', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "classifiers": [\n'
        '            "Topic :: Software Development :: Testing",\n'
        '            "UNKNOWN"\n'
        '        ],\n'
        '        "name": "has_prerel",\n'
        '        "people": [\n'
        '            {\n'
        '                "email": "freed@hotmail.com",\n'
        '                "name": "Samantha Gilbert",\n'
        '                "role": "author"\n'
        '            },\n'
        '            {\n'
        '                "email": "estradakelly@hotmail.com",\n'
        '                "name": "Bradley Livingston",\n'
        '                "role": "maintainer"\n'
        '            }\n'
        '        ],\n'
        '        "platform": "Coleco",\n'
        '        "project_url": "https://dummy.nil/pypi/has_prerel",\n'
        '        "release_date": "1970-04-21T22:33:29.915221Z",\n'
        '        "release_url": "https://dummy.nil/pypi/has_prerel/1.0.0",\n'
        '        "summary": "Boy kid chance indeed resource explain.",\n'
        '        "unknown_field": "passed through",\n'
        '        "url": "http://www.johnson.com/author.jsp",\n'
        '        "version": "1.0.0"\n'
        '    },\n'
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

def test_info_nonexistent(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'does-not-exist', 'foobar'])
    assert r.exit_code == 1, show_result(r)
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
        'qypi: does-not-exist: package not found\n'
    )

def test_info_nonexistent_split(mock_pypi_json):
    r = CliRunner(mix_stderr=False)\
            .invoke(qypi, ['info', 'does-not-exist', 'foobar'])
    assert r.exit_code == 1, show_result(r)
    assert r.stdout == (
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
    assert r.stderr == 'qypi: does-not-exist: package not found\n'

def test_info_nonexistent_version(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'foobar==2.23.42'])
    assert r.exit_code == 1, show_result(r)
    assert r.output == (
        '[]\n'
        'qypi: foobar: version 2.23.42 not found\n'
    )

def test_info_nonexistent_version_split(mock_pypi_json):
    r = CliRunner(mix_stderr=False).invoke(qypi, ['info', 'foobar==2.23.42'])
    assert r.exit_code == 1, show_result(r)
    assert r.stdout == '[]\n'
    assert r.stderr == 'qypi: foobar: version 2.23.42 not found\n'

def test_info_nonexistent_explicit_version(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'does-not-exist==2.23.42'])
    assert r.exit_code == 1, show_result(r)
    assert r.output == (
        '[]\n'
        'qypi: does-not-exist: version 2.23.42 not found\n'
    )

def test_info_nonexistent_explicit_version_split(mock_pypi_json):
    r = CliRunner(mix_stderr=False)\
            .invoke(qypi, ['info', 'does-not-exist==2.23.42'])
    assert r.exit_code == 1, show_result(r)
    assert r.stdout == '[]\n'
    assert r.stderr == 'qypi: does-not-exist: version 2.23.42 not found\n'

def test_info_latest_is_prerelease(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'has-prerel'])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data[0]["version"] == "1.0.0"

def test_info_latest_is_prerelease_pre(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', '--pre', 'has-prerel'])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data[0]["version"] == "1.0.1a1"

def test_info_explicit_prerelease(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'has-prerel==1.0.1a1'])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data[0]["version"] == "1.0.1a1"

def test_info_all_are_prerelease(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'prerelease-only'])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data[0]["version"] == "0.2a1"

def test_info_nullfields(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['info', 'nullfields'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "classifiers": [\n'
        '            "Topic :: Software Development :: Testing",\n'
        '            "UNKNOWN"\n'
        '        ],\n'
        '        "name": "nullfields",\n'
        '        "people": [\n'
        '            {\n'
        '                "email": "barbara10@yahoo.com",\n'
        '                "name": "Philip Gonzalez",\n'
        '                "role": "author"\n'
        '            }\n'
        '        ],\n'
        '        "platform": null,\n'
        '        "project_url": "https://dummy.nil/pypi/nullfields",\n'
        '        "release_date": "2007-10-08T07:21:06.191703Z",\n'
        '        "release_url": "https://dummy.nil/pypi/nullfields/1.0.0",\n'
        '        "summary": "Film station choose short.",\n'
        '        "unknown_field": null,\n'
        '        "url": "https://bryant.com/wp-content/search/author/",\n'
        '        "version": "1.0.0"\n'
        '    }\n'
        ']\n'
    )

def test_readme(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['readme', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "foobar v1.0.0\n"
        "\n"
        "Dream political close attorney sit cost inside. Seek hard can bad investment authority walk we. Sing range late use speech citizen.\n"  # noqa: B950
        "\n"
        "Can money issue claim onto really case. Fact garden along all book sister trip step.\n"  # noqa: B950
        "\n"
        "View table woman her production result. Fine allow prepare should traditional. Send cultural two care eye.\n"  # noqa: B950
        "\n"
        "Generated with Faker\n"
    )

def test_readme_explicit_version(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['readme', 'foobar==0.2.0'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "foobar v0.2.0\n"
        "\n"
        "Lead must laugh trouble expert else get million.\n"
        "\n"
        "Top shake walk. A cold national.\n"
        "\n"
        "Bring energy yourself suffer. Catch concern official relate voice base.\n"
        "\n"
        "Generated with Faker\n"
    )

def test_files(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['files', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "files": [\n'
        '            {\n'
        '                "comment_text": "",\n'
        '                "digests": {\n'
        '                    "md5": "f92e8964922878760a07f783341a58ae",\n'
        '                    "sha256": "84750bd98e3f61441e4b86ab443ebae41e65557e2b071b5a8e22a7d61a48a59d"\n'  # noqa: B950
        '                },\n'
        '                "filename": "foobar-1.0.0-py2.py3-none-any.whl",\n'
        '                "has_sig": true,\n'
        '                "md5_digest": "f92e8964922878760a07f783341a58ae",\n'
        '                "packagetype": "bdist_wheel",\n'
        '                "python_version": "py2.py3",\n'
        '                "size": 735,\n'
        '                "unknown_field": "passed through",\n'
        '                "upload_time": "2019-02-01T09:17:59",\n'
        '                "upload_time_iso_8601": "2019-02-01T09:17:59.172284Z",\n'
        '                "url": "https://files.dummyhosted.nil/packages/7f/97/e5ec19aed5d108c2f6c2fc6646d8247b1fadb49f0bf48e87a0fca8827696/foobar-1.0.0-py2.py3-none-any.whl"\n'  # noqa: B950
        '            }\n'
        '        ],\n'
        '        "name": "foobar",\n'
        '        "version": "1.0.0"\n'
        '    }\n'
        ']\n'
    )

def test_files_explicit_version(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['files', 'foobar==0.2.0'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '[\n'
        '    {\n'
        '        "files": [\n'
        '            {\n'
        '                "comment_text": "",\n'
        '                "digests": {\n'
        '                    "md5": "5ced02e62434eb5649276e6f12003009",\n'
        '                    "sha256": "f0862078b4f1af49f6b8c91153e9a7df88807900f9cf1b24287a901e515c824e"\n'  # noqa: B950
        '                },\n'
        '                "filename": "foobar-0.2.0-py2.py3-none-any.whl",\n'
        '                "has_sig": false,\n'
        '                "md5_digest": "5ced02e62434eb5649276e6f12003009",\n'
        '                "packagetype": "bdist_wheel",\n'
        '                "python_version": "py2.py3",\n'
        '                "size": 752,\n'
        '                "unknown_field": "passed through",\n'
        '                "upload_time": "2017-02-04T12:34:05",\n'
        '                "upload_time_iso_8601": "2017-02-04T12:34:05.766270Z",\n'
        '                "url": "https://files.dummyhosted.nil/packages/54/40/36eccb727704b5dabfda040e0eb23c29dbe26cf1a78cbeb24f33deb26b22/foobar-0.2.0-py2.py3-none-any.whl"\n'  # noqa: B950
        '            }\n'
        '        ],\n'
        '        "name": "foobar",\n'
        '        "version": "0.2.0"\n'
        '    }\n'
        ']\n'
    )

def test_releases(mock_pypi_json):
    r = CliRunner().invoke(qypi, ['releases', 'foobar'])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        '{\n'
        '    "foobar": [\n'
        '        {\n'
        '            "is_prerelease": false,\n'
        '            "release_date": "2013-01-18T18:53:56.265173Z",\n'
        '            "release_url": "https://dummy.nil/pypi/foobar/0.1.0",\n'
        '            "version": "0.1.0"\n'
        '        },\n'
        '        {\n'
        '            "is_prerelease": false,\n'
        '            "release_date": "2017-02-04T12:34:05.766270Z",\n'
        '            "release_url": "https://dummy.nil/pypi/foobar/0.2.0",\n'
        '            "version": "0.2.0"\n'
        '        },\n'
        '        {\n'
        '            "is_prerelease": false,\n'
        '            "release_date": "2019-02-01T09:17:59.172284Z",\n'
        '            "release_url": "https://dummy.nil/pypi/foobar/1.0.0",\n'
        '            "version": "1.0.0"\n'
        '        }\n'
        '    ]\n'
        '}\n'
    )

# `qypi --index-url`
