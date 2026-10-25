"""
Components package initialization for FamilyCare AI.
"""
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _PKG_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

__path__ = [str(_PKG_DIR)]

from . import ui_helpers
from . import three_scene
