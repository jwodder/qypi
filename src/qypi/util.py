from collections.abc import Iterator
from datetime import datetime
from itertools import groupby
import json
from operator import attrgetter
from typing import Optional
from packaging.version import parse


def json_default(x):
    from .api import JSONableBase

    if isinstance(x, JSONableBase):
        return x.json_dict()
    else:
        return x


def dumps(obj):
    if isinstance(obj, Iterator):
        obj = list(obj)
    return json.dumps(
        obj, sort_keys=True, indent=4, ensure_ascii=False, default=json_default
    )


def squish_versions(releases):
    """
    Given a list of `SearchResult`\\s or `BrowseResult`\\s, return for each
    name the result with the highest version.

    It is assumed that `dict`s with the same name are always adjacent.
    """
    for _, versions in groupby(releases, attrgetter("name")):
        yield max(versions, key=lambda v: parse(v.version))


def show_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    else:
        return dt.isoformat()
