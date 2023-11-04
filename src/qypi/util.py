from datetime import datetime
import json
from typing import Any, Optional


def dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)


def show_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    else:
        return dt.isoformat()
