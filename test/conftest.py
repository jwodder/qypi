from collections import OrderedDict
import json
from pathlib import Path
import re
from packaging.utils import canonicalize_name
import pytest
import responses

DATA_DIR = Path(__file__).with_name("data")

urlre = re.compile(r"^https://pypi\.org/pypi/([-.\w]+)(?:/([^/]+))?/json$")


@pytest.fixture
def mock_pypi_json():
    with responses.RequestsMock() as rsps:
        rsps.add_callback(
            responses.GET,
            urlre,
            callback=mkresponse,
            content_type="application/json",
        )
        yield rsps


def mkresponse(r):
    m = urlre.match(r.url)
    assert m
    package, version = m.groups()
    package = canonicalize_name(package)
    try:
        with open(str(DATA_DIR / (package + ".json"))) as fp:
            data = json.load(fp, object_pairs_hook=OrderedDict)
    except FileNotFoundError:
        return (404, {}, "Nope.")
    if version is None:
        version = next(reversed(data))
    try:
        about = data[version]
    except KeyError:
        return (404, {}, "Nope.")
    return (
        200,
        {},
        json.dumps(
            {
                "info": dict(about["info"], version=version),
                "urls": about["files"],
                "releases": {v: ab["files"] for v, ab in data.items()},
            }
        ),
    )
