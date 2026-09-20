from __future__ import annotations

import sys
import unittest


def main() -> int:
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print("benchmark unit tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
