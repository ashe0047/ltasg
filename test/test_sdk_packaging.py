"""Test SDK packaging, wheel/sdist integrity, and installability."""

from __future__ import annotations

import email
import email.policy
import subprocess
import sys
import tarfile
import tempfile
import textwrap
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = PROJECT_ROOT / "dist"


def _reset_build_dir() -> None:
    import shutil
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)


@pytest.fixture(scope="module")
def build_output() -> tuple[dict[str, str], list[str]]:
    """Build the project and return metadata plus artifact filenames."""
    _reset_build_dir()
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(BUILD_DIR), str(PROJECT_ROOT)],
        check=True, capture_output=True, text=True,
    )
    artifacts = sorted(BUILD_DIR.glob("ltasg-*"))
    info: dict[str, str] = {}
    paths: list[str] = []
    for artifact in artifacts:
        name = artifact.name
        paths.append(name)
        if name.endswith(".whl"):
            info["wheel"] = str(artifact)
            with zipfile.ZipFile(artifact) as zf:
                for entry in zf.namelist():
                    if entry.endswith("METADATA"):
                        info["metadata"] = zf.read(entry).decode("utf-8")
                        break
        elif name.endswith(".tar.gz"):
            info["sdist"] = str(artifact)
    assert "wheel" in info, "wheel artifact not produced"
    assert "sdist" in info, "sdist artifact not produced"
    return info, paths


def test_wheel_created(build_output) -> None:
    info, paths = build_output
    wheels = [p for p in paths if p.endswith(".whl")]
    assert len(wheels) == 1, f"expected 1 wheel, got {len(wheels)}: {wheels}"


def test_sdist_created(build_output) -> None:
    info, paths = build_output
    sdists = [p for p in paths if p.endswith(".tar.gz")]
    assert len(sdists) == 1, f"expected 1 sdist, got {len(sdists)}: {sdists}"


def test_wheel_contains_modules_and_py_typed(build_output) -> None:
    info, _ = build_output
    with zipfile.ZipFile(Path(info["wheel"])) as zf:
        names = set(zf.namelist())
    assert "ltasg/py.typed" in names, "PEP 561 marker missing"
    assert "ltasg/api.py" in names
    assert "ltasg/constants.py" in names
    assert "ltasg/traffic.py" in names
    assert "ltasg/other.py" in names
    assert "ltasg/transport/bus.py" in names
    assert "ltasg/transport/train.py" in names
    assert "ltasg/transport/taxi.py" in names


def test_wheel_excludes_tests(build_output) -> None:
    info, _ = build_output
    with zipfile.ZipFile(Path(info["wheel"])) as zf:
        names = zf.namelist()
    test_entries = [n for n in names if "test" in n.lower()]
    assert not test_entries, f"wheel contains test entries: {test_entries}"


def test_sdist_excludes_tests(build_output) -> None:
    info, _ = build_output
    with tarfile.open(Path(info["sdist"])) as tf:
        names = tf.getnames()
    test_entries = [n for n in names if "/test/" in n or n.endswith("test/")]
    assert not test_entries, f"sdist contains test entries: {test_entries}"


def test_metadata_name(build_output) -> None:
    info, _ = build_output
    msg = email.message_from_string(info["metadata"], policy=email.policy.compat32)
    assert msg["Name"] == "ltasg", f"got {msg['Name']!r}"


def test_metadata_version(build_output) -> None:
    info, _ = build_output
    msg = email.message_from_string(info["metadata"], policy=email.policy.compat32)
    ver = msg["Version"]
    assert ver, "Version field missing from METADATA"


def test_metadata_license(build_output) -> None:
    info, _ = build_output
    msg = email.message_from_string(info["metadata"], policy=email.policy.compat32)
    assert msg["License-Expression"] == "MIT", f"got {msg['License-Expression']!r}"


def test_metadata_requires_python(build_output) -> None:
    info, _ = build_output
    msg = email.message_from_string(info["metadata"], policy=email.policy.compat32)
    assert ">=" in (msg["Requires-Python"] or ""), (
        f"got {msg['Requires-Python']!r}"
    )


def test_metadata_requires_dist(build_output) -> None:
    info, _ = build_output
    msg = email.message_from_string(info["metadata"], policy=email.policy.compat32)
    requires_dist = msg.get_all("Requires-Dist", [])
    assert any("aiohttp" in r for r in requires_dist), (
        f"aiohttp not found in Requires-Dist: {requires_dist}"
    )


def _import_check_script() -> str:
    return textwrap.dedent("""\
        from ltasg import Bus, Train, Taxi, Traffic, Other
        from ltasg.api import LTADataMall
        import ltasg
        print(f"OK version={getattr(ltasg, '__version__', 'unknown')}")
    """)


def test_wheel_installs_and_imports(build_output) -> None:
    info, _ = build_output
    wheel_path = Path(info["wheel"])

    with tempfile.TemporaryDirectory(prefix="ltasg-test-") as tmp:
        target_dir = Path(tmp) / "lib"
        target_dir.mkdir(parents=True)

        subprocess.run(
            [sys.executable, "-m", "pip", "install",
             str(wheel_path), "--no-deps", "--quiet",
             "--target", str(target_dir)],
            check=True, capture_output=True, text=True,
        )

        target_repr = repr(str(target_dir))
        script = (
            f"import sys; sys.path.insert(0, {target_repr});\n"
            f"{_import_check_script()}"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, (
            f"import check failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
        assert "Imports OK" not in result.stderr.upper()
