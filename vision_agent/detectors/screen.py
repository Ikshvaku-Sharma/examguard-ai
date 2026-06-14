"""
Screen Activity Monitor
────────────────────────
Detects when the student switches away from the exam window.
Uses pygetwindow (cross-platform) to get the active window title.
"""

import os
from dataclasses import dataclass


@dataclass
class ScreenResult:
    tab_switched:  bool
    window_title:  str


class ScreenDetector:
    """
    Tracks the currently active window title.
    Flags a tab_switch event if the focus moves away from
    the expected exam window.
    """

    def __init__(self):
        self._exam_keywords   = ["exam", "test", "quiz", "examguard", "browser"]
        self._last_title      = ""
        self._pygetwindow_ok  = True
        self._import_lib()

    def _import_lib(self):
        try:
            import pygetwindow as gw
            self._gw = gw
        except ImportError:
            self._pygetwindow_ok = False
            import logging
            logging.getLogger(__name__).warning(
                "pygetwindow not installed — tab detection disabled. "
                "Run: pip install pygetwindow"
            )

    def check(self) -> ScreenResult:
        if not self._pygetwindow_ok:
            return ScreenResult(tab_switched=False, window_title="")

        try:
            active = self._gw.getActiveWindow()
            title  = active.title if active else ""
        except Exception:
            return ScreenResult(tab_switched=False, window_title="")

        # Detect switch: title changed AND new title doesn't look like an exam window
        switched = (
            title != self._last_title
            and title != ""
            and not any(kw in title.lower() for kw in self._exam_keywords)
        )
        self._last_title = title
        return ScreenResult(tab_switched=switched, window_title=title)
