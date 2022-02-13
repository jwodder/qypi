from collections.abc import Iterator
from datetime import datetime
import json
from typing import Any, Optional


def json_default(x: Any) -> Any:
    from .api import JSONableBase

    if isinstance(x, Iterator):
        return list(x)
    elif isinstance(x, JSONableBase):
        return x.json_dict()
    else:
        return x


def dumps(obj: Any) -> str:
    return json.dumps(
        obj, sort_keys=True, indent=4, ensure_ascii=False, default=json_default
    )


def show_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    else:
        return dt.isoformat()
