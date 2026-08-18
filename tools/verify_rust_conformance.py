#!/usr/bin/env python3
"""Compile and verify the stdlib-only Rust LATTICE reference implementation."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "implementations" / "rust" / "lattice.rs"
FIXTURE = ROOT / "conformance" / "profile-v1.json"
MANIFEST = ROOT / "manifest.json"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def verify() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    toolchain = manifest.get("rust_toolchain")
    if not isinstance(toolchain, str) or not toolchain:
        raise ValueError("manifest rust_toolchain missing or invalid")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        test_binary = temp / "lattice-rust-tests"
        binary = temp / "lattice-rust"

        run(
            [
                "rustc",
                f"+{toolchain}",
                "--edition=2021",
                "--test",
                str(SOURCE),
                "-o",
                str(test_binary),
            ]
        )
        test_result = run([str(test_binary)])

        run(
            [
                "rustc",
                f"+{toolchain}",
                "--edition=2021",
                "-O",
                str(SOURCE),
                "-o",
                str(binary),
            ]
        )
        result = run([str(binary)])

    actual = json.loads(result.stdout)
    expected = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if actual != expected:
        raise ValueError("Rust conformance record does not match frozen profile-v1 fixture")
    if "test result: ok" not in test_result.stdout:
        raise ValueError("Rust unit-test runner did not report success")

    return {
        "status": "valid",
        "toolchain": toolchain,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "fixture": FIXTURE.relative_to(ROOT).as_posix(),
        "rust_tests": "passed",
        "profile_fingerprint": actual["fingerprint"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
