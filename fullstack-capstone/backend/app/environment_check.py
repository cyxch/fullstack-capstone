"""Report the local runtime needed by the capstone project."""

from __future__ import annotations

import platform
import sys


def collect_environment() -> dict[str, str]:
    """Return stable, human-readable environment information."""

    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "system": platform.system(),
        "architecture": platform.machine(),
        "executable": sys.executable,
    }


def main() -> None:
    """Print environment information for the first-week setup check."""

    for key, value in collect_environment().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
