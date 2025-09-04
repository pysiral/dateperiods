# -*- coding: utf-8 -*-

import sys
from pathlib import Path

PACKAGE_PATH = Path(__file__).parent.resolve() / ".." / "src"
sys.path.insert(0, str(PACKAGE_PATH))

import dateperiods

__all__ = ["dateperiods"]
