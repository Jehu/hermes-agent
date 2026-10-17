"""Onboarding handlers must import before server globals are bound, including on Python 3.11."""

import os
from pathlib import Path
import subprocess
import sys


def test_onboarding_import_without_server_globals(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path\n"
            "from typing import get_type_hints\n"
            "from tui_gateway import methods_onboarding\n"
            "assert get_type_hints(methods_onboarding._shared_nous_store)['return'] == tuple[Path, ...]\n"
            "assert 'onboarding.state' in methods_onboarding._registry.names()\n"
            "assert 'tui_gateway.server' not in __import__('sys').modules\n",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env={
            "PATH": os.defpath,
            "HOME": str(tmp_path),
            "USERPROFILE": str(tmp_path),
            "TMPDIR": str(tmp_path),
            "HERMES_HOME": str(tmp_path / "hermes"),
            "HERMES_RUNTIME_DIR": str(tmp_path / "runtime"),
            "HERMES_TEST_ISOLATION": str(tmp_path / "hermes"),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
