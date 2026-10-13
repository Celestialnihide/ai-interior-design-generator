"""Host ABI version. Plugins declaring a mismatched major are rejected."""
from __future__ import annotations

HOST_ABI = "1.4"
HOST_ABI_MAJOR = 1


def abi_compatible(declared: str) -> bool:
    """Return True if `declared` shares our major version.

    >>> abi_compatible("1.0")
    True
    >>> abi_compatible("2.0")
    False
    """
    try:
        major = int(declared.split(".", 1)[0])
    except (ValueError, AttributeError):
        return False
    return major == HOST_ABI_MAJOR