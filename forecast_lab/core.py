"""Canonical identities and explicit UTC clocks shared by every artifact."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Invalid(ValueError):
    """An input cannot satisfy the frozen research contract."""


def canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def utc(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError) as exc:
        raise Invalid("Expected ISO timestamp with explicit timezone") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise Invalid("Naive timestamps are forbidden")
    return result.astimezone(timezone.utc)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def probability(value: Any, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise Invalid("Probability must be numeric")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise Invalid("Probability must be finite and in [0,1]")


def load(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def dump(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    )


def require(value: dict, keys: set[str]) -> None:
    missing = keys - value.keys()
    if missing:
        raise Invalid(f"Missing fields: {sorted(missing)}")
