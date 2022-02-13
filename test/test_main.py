import json
import sys
from traceback import format_exception
import click
from click.testing import CliRunner
import pytest
from qypi.__main__ import main
from qypi.api import USER_AGENT


def show_result(r):
    if r.exception is not None:
        return "".join(format_exception(*r.exc_info))
    else:
        return r.output


def test_list(mocker):
    spinstance = mocker.MagicMock(
        **{
            "list_packages.return_value": [
                "foobar",
                "BarFoo",
                "quux",
                "Gnusto-Cleesh",
                "XYZZY_PLUGH",
            ],
        }
    )
    spclass = mocker.patch("qypi.api.ServerProxy", return_value=spinstance)
    r = CliRunner().invoke(main, ["list"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "foobar\nBarFoo\nquux\nGnusto-Cleesh\nXYZZY_PLUGH\n"
    if sys.version_info >= (3, 8):
        spclass.assert_called_once_with(
            "https://pypi.org/pypi", headers=[("User-Agent", USER_AGENT)]
        )
    else:
        spclass.assert_called_once_with("https://pypi.org/pypi")
    assert spinstance.method_calls == [mocker.call.list_packages()]


def test_owner(mocker):
    spinstance = mocker.MagicMock(
        **{
            "package_roles.return_value": [
                ["Owner", "luser"],
                ["Maintainer", "jsmith"],
            ],
        }
    )
    spclass = mocker.patch("qypi.api.ServerProxy", return_value=spinstance)
    r = CliRunner().invoke(main, ["owner", "foobar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "role": "Owner",\n'
        '        "user": "luser"\n'
        "    },\n"
        "    {\n"
        '        "role": "Maintainer",\n'
        '        "user": "jsmith"\n'
        "    }\n"
        "]\n"
    )
    if sys.version_info >= (3, 8):
        spclass.assert_called_once_with(
            "https://pypi.org/pypi", headers=[("User-Agent", USER_AGENT)]
        )
    else:
        spclass.assert_called_once_with("https://pypi.org/pypi")
    assert spinstance.method_calls == [mocker.call.package_roles("foobar")]


def test_owned(mocker):
    spinstance = mocker.MagicMock(
        **{
            "user_packages.return_value": [
                ["Owner", "foobar"],
                ["Maintainer", "quux"],
            ],
        }
    )
    spclass = mocker.patch("qypi.api.ServerProxy", return_value=spinstance)
    r = CliRunner().invoke(main, ["owned", "luser"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "project": "foobar",\n'
        '        "role": "Owner"\n'
        "    },\n"
        "    {\n"
        '        "project": "quux",\n'
        '        "role": "Maintainer"\n'
        "    }\n"
        "]\n"
    )
    if sys.version_info >= (3, 8):
        spclass.assert_called_once_with(
            "https://pypi.org/pypi", headers=[("User-Agent", USER_AGENT)]
        )
    else:
        spclass.assert_called_once_with("https://pypi.org/pypi")
    assert spinstance.method_calls == [mocker.call.user_packages("luser")]


def test_search(mocker):
    spinstance = mocker.MagicMock(
        **{
            "search.return_value": [
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
        }
    )
    spclass = mocker.patch("qypi.api.ServerProxy", return_value=spinstance)
    r = CliRunner().invoke(main, ["search", "term", "keyword:foo", "readme:bar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "name": "foobar",\n'
        '        "summary": "Foo all your bars",\n'
        '        "version": "1.2.3"\n'
        "    },\n"
        "    {\n"
        '        "name": "quux",\n'
        '        "summary": "Do that thing this does",\n'
        '        "version": "0.1.0"\n'
        "    },\n"
        "    {\n"
        '        "name": "gnusto",\n'
        '        "summary": null,\n'
        '        "version": "0.0.0"\n'
        "    }\n"
        "]\n"
    )
    if sys.version_info >= (3, 8):
        spclass.assert_called_once_with(
            "https://pypi.org/pypi", headers=[("User-Agent", USER_AGENT)]
        )
    else:
        spclass.assert_called_once_with("https://pypi.org/pypi")
    assert spinstance.method_calls == [
        mocker.call.search(
            {"description": ["term", "bar"], "keywords": ["foo"]},
            "and",
        )
    ]


def test_browse(mocker):
    spinstance = mocker.MagicMock(
        **{
            "browse.return_value": [
                ["foobar", "1.2.3"],
                ["foobar", "1.2.2"],
                ["foobar", "1.2.1"],
                ["foobar", "1.2.0"],
                ["quux", "0.1.0"],
                ["gnusto", "0.0.0"],
            ],
        }
    )
    spclass = mocker.patch("qypi.api.ServerProxy", return_value=spinstance)
    r = CliRunner().invoke(
        main,
        ["browse", "Typing :: Typed", "Topic :: Utilities"],
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "name": "foobar",\n'
        '        "version": "1.2.3"\n'
        "    },\n"
        "    {\n"
        '        "name": "foobar",\n'
        '        "version": "1.2.2"\n'
        "    },\n"
        "    {\n"
        '        "name": "foobar",\n'
        '        "version": "1.2.1"\n'
        "    },\n"
        "    {\n"
        '        "name": "foobar",\n'
        '        "version": "1.2.0"\n'
        "    },\n"
        "    {\n"
        '        "name": "quux",\n'
        '        "version": "0.1.0"\n'
        "    },\n"
        "    {\n"
        '        "name": "gnusto",\n'
        '        "version": "0.0.0"\n'
        "    }\n"
        "]\n"
    )
    if sys.version_info >= (3, 8):
        spclass.assert_called_once_with(
            "https://pypi.org/pypi", headers=[("User-Agent", USER_AGENT)]
        )
    else:
        spclass.assert_called_once_with("https://pypi.org/pypi")
    assert spinstance.method_calls == [
        mocker.call.browse(("Typing :: Typed", "Topic :: Utilities"))
    ]


def test_browse_packages(mocker):
    spinstance = mocker.MagicMock(
        **{
            "browse.return_value": [
                ["foobar", "1.2.3"],
                ["foobar", "1.2.2"],
                ["foobar", "1.2.1"],
                ["foobar", "1.2.0"],
                ["quux", "0.1.0"],
                ["gnusto", "0.0.0"],
            ],
        }
    )
    spclass = mocker.patch("qypi.api.ServerProxy", return_value=spinstance)
    r = CliRunner().invoke(
        main,
        ["browse", "--projects", "Typing :: Typed", "Topic :: Utilities"],
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "name": "foobar",\n'
        '        "version": "1.2.3"\n'
        "    },\n"
        "    {\n"
        '        "name": "quux",\n'
        '        "version": "0.1.0"\n'
        "    },\n"
        "    {\n"
        '        "name": "gnusto",\n'
        '        "version": "0.0.0"\n'
        "    }\n"
        "]\n"
    )
    if sys.version_info >= (3, 8):
        spclass.assert_called_once_with(
            "https://pypi.org/pypi", headers=[("User-Agent", USER_AGENT)]
        )
    else:
        spclass.assert_called_once_with("https://pypi.org/pypi")
    assert spinstance.method_calls == [
        mocker.call.browse(("Typing :: Typed", "Topic :: Utilities"))
    ]


@pytest.mark.usefixtures("mock_pypi_json")
def test_info():
    r = CliRunner().invoke(main, ["info", "foobar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "{\n"
        '    "classifiers": [\n'
        '        "Topic :: Software Development :: Testing",\n'
        '        "UNKNOWN"\n'
        "    ],\n"
        '    "name": "foobar",\n'
        '    "package_url": "https://dummy.nil/pypi/foobar",\n'
        '    "people": [\n'
        "        {\n"
        '            "email": "megan30@daniels.info",\n'
        '            "name": "Brandon Perkins",\n'
        '            "role": "author"\n'
        "        },\n"
        "        {\n"
        '            "email": "cspencer@paul-fisher.com",\n'
        '            "name": "Denise Adkins",\n'
        '            "role": "maintainer"\n'
        "        }\n"
        "    ],\n"
        '    "platform": "Amiga",\n'
        '    "project_url": "https://dummy.nil/pypi/foobar",\n'
        '    "release_date": "2019-02-01T09:17:59.172284+00:00",\n'
        '    "release_url": "https://dummy.nil/pypi/foobar/1.0.0",\n'
        '    "summary": "Including drive environment my it.",\n'
        '    "url": "https://www.johnson.com/homepage.php",\n'
        '    "version": "1.0.0",\n'
        '    "yanked": false,\n'
        '    "yanked_reason": null\n'
        "}\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_explicit_latest_version():
    r = CliRunner().invoke(main, ["info", "foobar==1.0.0"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "{\n"
        '    "classifiers": [\n'
        '        "Topic :: Software Development :: Testing",\n'
        '        "UNKNOWN"\n'
        "    ],\n"
        '    "name": "foobar",\n'
        '    "package_url": "https://dummy.nil/pypi/foobar",\n'
        '    "people": [\n'
        "        {\n"
        '            "email": "megan30@daniels.info",\n'
        '            "name": "Brandon Perkins",\n'
        '            "role": "author"\n'
        "        },\n"
        "        {\n"
        '            "email": "cspencer@paul-fisher.com",\n'
        '            "name": "Denise Adkins",\n'
        '            "role": "maintainer"\n'
        "        }\n"
        "    ],\n"
        '    "platform": "Amiga",\n'
        '    "project_url": "https://dummy.nil/pypi/foobar",\n'
        '    "release_date": "2019-02-01T09:17:59.172284+00:00",\n'
        '    "release_url": "https://dummy.nil/pypi/foobar/1.0.0",\n'
        '    "summary": "Including drive environment my it.",\n'
        '    "url": "https://www.johnson.com/homepage.php",\n'
        '    "version": "1.0.0",\n'
        '    "yanked": false,\n'
        '    "yanked_reason": null\n'
        "}\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_explicit_version():
    r = CliRunner().invoke(main, ["info", "foobar==0.2.0"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "{\n"
        '    "classifiers": [\n'
        '        "Topic :: Software Development :: Testing",\n'
        '        "UNKNOWN"\n'
        "    ],\n"
        '    "name": "foobar",\n'
        '    "package_url": "https://dummy.nil/pypi/foobar",\n'
        '    "people": [\n'
        "        {\n"
        '            "email": "danielstewart@frye.com",\n'
        '            "name": "Sonya Johnson",\n'
        '            "role": "author"\n'
        "        },\n"
        "        {\n"
        '            "email": "maynardtim@hotmail.com",\n'
        '            "name": "Stephen Romero",\n'
        '            "role": "maintainer"\n'
        "        }\n"
        "    ],\n"
        '    "platform": "Wood",\n'
        '    "project_url": "https://dummy.nil/pypi/foobar",\n'
        '    "release_date": "2017-02-04T12:34:05.766270+00:00",\n'
        '    "release_url": "https://dummy.nil/pypi/foobar/0.2.0",\n'
        '    "summary": "Water audience cut call.",\n'
        '    "url": "http://www.sanchez.net/index.htm",\n'
        '    "version": "0.2.0",\n'
        '    "yanked": false,\n'
        '    "yanked_reason": null\n'
        "}\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_description():
    r = CliRunner().invoke(main, ["info", "--description", "foobar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "{\n"
        '    "classifiers": [\n'
        '        "Topic :: Software Development :: Testing",\n'
        '        "UNKNOWN"\n'
        "    ],\n"
        '    "description": "foobar v1.0.0\\n\\nDream political close attorney sit cost inside. Seek hard can bad investment authority walk we. Sing range late use speech citizen.\\n\\nCan money issue claim onto really case. Fact garden along all book sister trip step.\\n\\nView table woman her production result. Fine allow prepare should traditional. Send cultural two care eye.\\n\\nGenerated with Faker",\n'
        '    "name": "foobar",\n'
        '    "package_url": "https://dummy.nil/pypi/foobar",\n'
        '    "people": [\n'
        "        {\n"
        '            "email": "megan30@daniels.info",\n'
        '            "name": "Brandon Perkins",\n'
        '            "role": "author"\n'
        "        },\n"
        "        {\n"
        '            "email": "cspencer@paul-fisher.com",\n'
        '            "name": "Denise Adkins",\n'
        '            "role": "maintainer"\n'
        "        }\n"
        "    ],\n"
        '    "platform": "Amiga",\n'
        '    "project_url": "https://dummy.nil/pypi/foobar",\n'
        '    "release_date": "2019-02-01T09:17:59.172284+00:00",\n'
        '    "release_url": "https://dummy.nil/pypi/foobar/1.0.0",\n'
        '    "summary": "Including drive environment my it.",\n'
        '    "url": "https://www.johnson.com/homepage.php",\n'
        '    "version": "1.0.0",\n'
        '    "yanked": false,\n'
        '    "yanked_reason": null\n'
        "}\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
@pytest.mark.parametrize("arg", ["does-not-exist", "does-not-exist==2.23.42"])
def test_info_nonexistent(arg):
    r = CliRunner().invoke(main, ["info", arg], standalone_mode=False)
    assert r.exit_code != 0, show_result(r)
    assert r.output == ""
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == "does-not-exist: project not found"


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_nonexistent_version():
    r = CliRunner().invoke(main, ["info", "foobar==2.23.42"], standalone_mode=False)
    assert r.exit_code != 0, show_result(r)
    assert r.output == ""
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == "foobar: no matching versions found"


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_latest_is_prerelease():
    r = CliRunner().invoke(main, ["info", "has-prerel"])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data["version"] == "1.0.0"


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_latest_is_prerelease_pre():
    r = CliRunner().invoke(main, ["info", "--pre", "has-prerel"])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data["version"] == "1.0.1a1"


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_explicit_prerelease():
    r = CliRunner().invoke(main, ["info", "has-prerel==1.0.1a1"])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data["version"] == "1.0.1a1"


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_all_are_prerelease():
    r = CliRunner().invoke(main, ["info", "prerelease-only"])
    assert r.exit_code == 0, show_result(r)
    data = json.loads(r.output)
    assert data["version"] == "0.2a1"


@pytest.mark.usefixtures("mock_pypi_json")
def test_info_nullfields():
    r = CliRunner().invoke(main, ["info", "nullfields"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "{\n"
        '    "classifiers": [\n'
        '        "Topic :: Software Development :: Testing",\n'
        '        "UNKNOWN"\n'
        "    ],\n"
        '    "name": "nullfields",\n'
        '    "package_url": "https://dummy.nil/pypi/nullfields",\n'
        '    "people": [\n'
        "        {\n"
        '            "email": "barbara10@yahoo.com",\n'
        '            "name": "Philip Gonzalez",\n'
        '            "role": "author"\n'
        "        }\n"
        "    ],\n"
        '    "platform": null,\n'
        '    "project_url": "https://dummy.nil/pypi/nullfields",\n'
        '    "release_date": "2007-10-08T07:21:06.191703+00:00",\n'
        '    "release_url": "https://dummy.nil/pypi/nullfields/1.0.0",\n'
        '    "summary": "Film station choose short.",\n'
        '    "url": "https://bryant.com/wp-content/search/author/",\n'
        '    "version": "1.0.0",\n'
        '    "yanked": false,\n'
        '    "yanked_reason": null\n'
        "}\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_readme():
    r = CliRunner().invoke(main, ["readme", "foobar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "foobar v1.0.0\n"
        "\n"
        "Dream political close attorney sit cost inside. Seek hard can bad investment authority walk we. Sing range late use speech citizen.\n"
        "\n"
        "Can money issue claim onto really case. Fact garden along all book sister trip step.\n"
        "\n"
        "View table woman her production result. Fine allow prepare should traditional. Send cultural two care eye.\n"
        "\n"
        "Generated with Faker\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_readme_explicit_version():
    r = CliRunner().invoke(main, ["readme", "foobar==0.2.0"])
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


@pytest.mark.usefixtures("mock_pypi_json")
def test_files():
    r = CliRunner().invoke(main, ["files", "foobar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "comment_text": "",\n'
        '        "digests": {\n'
        '            "md5": "f92e8964922878760a07f783341a58ae",\n'
        '            "sha256": "84750bd98e3f61441e4b86ab443ebae41e65557e2b071b5a8e22a7d61a48a59d"\n'
        "        },\n"
        '        "filename": "foobar-1.0.0-py2.py3-none-any.whl",\n'
        '        "has_sig": true,\n'
        '        "md5_digest": "f92e8964922878760a07f783341a58ae",\n'
        '        "packagetype": "bdist_wheel",\n'
        '        "python_version": "py2.py3",\n'
        '        "size": 735,\n'
        '        "upload_time": "2019-02-01T09:17:59",\n'
        '        "upload_time_iso_8601": "2019-02-01T09:17:59.172284+00:00",\n'
        '        "url": "https://files.dummyhosted.nil/packages/7f/97/e5ec19aed5d108c2f6c2fc6646d8247b1fadb49f0bf48e87a0fca8827696/foobar-1.0.0-py2.py3-none-any.whl",\n'
        '        "yanked": false,\n'
        '        "yanked_reason": null\n'
        "    }\n"
        "]\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_files_explicit_version():
    r = CliRunner().invoke(main, ["files", "foobar==0.2.0"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "comment_text": "",\n'
        '        "digests": {\n'
        '            "md5": "5ced02e62434eb5649276e6f12003009",\n'
        '            "sha256": "f0862078b4f1af49f6b8c91153e9a7df88807900f9cf1b24287a901e515c824e"\n'
        "        },\n"
        '        "filename": "foobar-0.2.0-py2.py3-none-any.whl",\n'
        '        "has_sig": false,\n'
        '        "md5_digest": "5ced02e62434eb5649276e6f12003009",\n'
        '        "packagetype": "bdist_wheel",\n'
        '        "python_version": "py2.py3",\n'
        '        "size": 752,\n'
        '        "upload_time": "2017-02-04T12:34:05",\n'
        '        "upload_time_iso_8601": "2017-02-04T12:34:05.766270+00:00",\n'
        '        "url": "https://files.dummyhosted.nil/packages/54/40/36eccb727704b5dabfda040e0eb23c29dbe26cf1a78cbeb24f33deb26b22/foobar-0.2.0-py2.py3-none-any.whl",\n'
        '        "yanked": false,\n'
        '        "yanked_reason": null\n'
        "    }\n"
        "]\n"
    )


@pytest.mark.usefixtures("mock_pypi_json")
def test_releases():
    r = CliRunner().invoke(main, ["releases", "foobar"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "[\n"
        "    {\n"
        '        "is_prerelease": false,\n'
        '        "is_yanked": false,\n'
        '        "release_date": "2013-01-18T18:53:56.265173+00:00",\n'
        '        "release_url": "https://dummy.nil/pypi/foobar/0.1.0",\n'
        '        "version": "0.1.0"\n'
        "    },\n"
        "    {\n"
        '        "is_prerelease": false,\n'
        '        "is_yanked": false,\n'
        '        "release_date": "2017-02-04T12:34:05.766270+00:00",\n'
        '        "release_url": "https://dummy.nil/pypi/foobar/0.2.0",\n'
        '        "version": "0.2.0"\n'
        "    },\n"
        "    {\n"
        '        "is_prerelease": false,\n'
        '        "is_yanked": false,\n'
        '        "release_date": "2019-02-01T09:17:59.172284+00:00",\n'
        '        "release_url": "https://dummy.nil/pypi/foobar/1.0.0",\n'
        '        "version": "1.0.0"\n'
        "    }\n"
        "]\n"
    )


# `qypi --index-url`
