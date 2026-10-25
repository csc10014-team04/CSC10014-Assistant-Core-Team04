"""Command line interface for assistant core."""

import sys

from assistant.__main__ import build_service, main

if __name__ == "__main__":
    sys.exit(main())
