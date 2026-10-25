"""Compatibility package forwarding to assistant."""

import sys
import assistant

sys.modules.setdefault("assistant_core", assistant)
