from __future__ import annotations

from importlib.metadata import version
from typing import Dict, Set


SUPPORTED_SCHEMA_HASHES: Dict[str, Set[str]] = {
    # Populate this set as Cloud schema evolves.
    "0.1.0": set(),
    "0.2.0": set(),
    "0.2.7": set(),
}


def package_version() -> str:
    try:
        return version("sdf-plan")
    except Exception:
        return "0.2.7"


def assert_schema_compat(pkg_version: str, schema_hash: str) -> None:
    if pkg_version not in SUPPORTED_SCHEMA_HASHES:
        raise RuntimeError(
            f"No schema compatibility map for sdf-plan {pkg_version}. "
            "Upgrade package or add compatibility entries."
        )
    allowed = SUPPORTED_SCHEMA_HASHES.get(pkg_version, set())
    if allowed and schema_hash not in allowed:
        raise RuntimeError(
            f"Incompatible schema_hash={schema_hash}. "
            f"sdf-plan {pkg_version} supports: {sorted(allowed)}"
        )
