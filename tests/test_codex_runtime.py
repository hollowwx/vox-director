from __future__ import annotations

import json
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import atlas_cloud  # noqa: E402
import codex_runtime  # noqa: E402
import doctor  # noqa: E402


class ResolveExecutableTests(unittest.TestCase):
    def test_resolves_command_from_path(self) -> None:
        with mock.patch("codex_runtime.shutil.which", return_value="C:/tools/curl.exe"):
            self.assertEqual(
                Path(codex_runtime.resolve_executable("curl")), Path("C:/tools/curl.exe").resolve()
            )

    def test_raises_clear_error_when_command_is_missing(self) -> None:
        with mock.patch("codex_runtime.shutil.which", return_value=None):
            with self.assertRaisesRegex(codex_runtime.RuntimeDependencyError, "curl"):
                codex_runtime.resolve_executable("curl")

    def test_explicit_override_must_be_absolute(self) -> None:
        with mock.patch.dict("codex_runtime.os.environ", {"VOX_CURL": "relative/curl.exe"}):
            with self.assertRaisesRegex(codex_runtime.RuntimeDependencyError, "absolute"):
                codex_runtime.resolve_executable("curl")


class EnvironmentInspectionTests(unittest.TestCase):
    def test_offline_environment_does_not_require_api_key(self) -> None:
        with mock.patch("codex_runtime.shutil.which", return_value="C:/tools/tool.exe"), mock.patch(
            "codex_runtime.importlib.util.find_spec", return_value=object()
        ):
            report = codex_runtime.inspect_environment(env={}, require_api_key=False)

        self.assertTrue(report["ok"])
        self.assertEqual(report["checks"]["atlas_api_key"]["status"], "optional")

    def test_production_environment_requires_api_key(self) -> None:
        with mock.patch("codex_runtime.shutil.which", return_value="C:/tools/tool.exe"), mock.patch(
            "codex_runtime.importlib.util.find_spec", return_value=object()
        ):
            report = codex_runtime.inspect_environment(env={}, require_api_key=True)

        self.assertFalse(report["ok"])
        self.assertTrue(report["offline_ready"])
        self.assertEqual(report["checks"]["atlas_api_key"]["status"], "missing")

    def test_codex_native_path_does_not_require_curl(self) -> None:
        def which(name: str) -> str | None:
            return None if name == "curl" else f"C:/tools/{name}.exe"

        with mock.patch("codex_runtime.shutil.which", side_effect=which), mock.patch(
            "codex_runtime.importlib.util.find_spec", return_value=object()
        ):
            report = codex_runtime.inspect_environment(env={}, require_api_key=False)

        self.assertTrue(report["ok"])
        self.assertEqual(report["checks"]["curl"]["status"], "optional")

    def test_atlas_path_requires_curl(self) -> None:
        def which(name: str) -> str | None:
            return None if name == "curl" else f"C:/tools/{name}.exe"

        with mock.patch("codex_runtime.shutil.which", side_effect=which), mock.patch(
            "codex_runtime.importlib.util.find_spec", return_value=object()
        ):
            report = codex_runtime.inspect_environment(
                env={"ATLASCLOUD_API_KEY": "secret"}, require_api_key=True
            )

        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"]["curl"]["status"], "missing")


class AtlasCurlTests(unittest.TestCase):
    def test_upload_uses_platform_resolved_curl(self) -> None:
        completed = subprocess.CompletedProcess([], 0, stdout='{"data":{"url":"https://example.com/file"}}')
        with mock.patch("atlas_cloud.resolve_executable", return_value="C:/tools/curl.exe"), mock.patch(
            "atlas_cloud._key", return_value="secret"
        ), mock.patch("atlas_cloud.subprocess.run", return_value=completed) as run:
            result = atlas_cloud.upload("poster.png")

        self.assertEqual(result, "https://example.com/file")
        self.assertEqual(run.call_args.args[0][0], "C:/tools/curl.exe")
        self.assertNotIn("secret", " ".join(run.call_args.args[0]))
        self.assertIn("Authorization: Bearer secret", run.call_args.kwargs["input"])

    def test_download_uses_platform_resolved_curl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.bin"

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                destination.write_bytes(b"ok")
                self.assertEqual(command[0], "C:/tools/curl.exe")
                self.assertIn("--proto", command)
                self.assertEqual(command[-2:], ["--", "https://example.com/asset"])
                return subprocess.CompletedProcess(command, 0)

            with mock.patch("atlas_cloud.resolve_executable", return_value="C:/tools/curl.exe"), mock.patch(
                "atlas_cloud.subprocess.run", side_effect=fake_run
            ):
                result = atlas_cloud.download("https://example.com/asset", str(destination))

        self.assertEqual(result, str(destination))

    def test_download_rejects_non_https_urls(self) -> None:
        with self.assertRaisesRegex(atlas_cloud.AtlasCloudError, "HTTPS"):
            atlas_cloud.download("file:///etc/passwd", "asset.bin")


class DoctorCliTests(unittest.TestCase):
    def test_json_output_is_machine_readable(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "doctor.py"), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        report = json.loads(completed.stdout)
        self.assertIn("checks", report)
        self.assertIn("ok", report)

    def test_human_output_reports_readiness(self) -> None:
        report = {
            "ok": True,
            "offline_ready": True,
            "production_ready": False,
            "checks": {"atlas_api_key": {"status": "optional", "detail": "not set"}},
        }
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["doctor.py"]), mock.patch(
            "doctor.inspect_environment", return_value=report
        ), mock.patch("sys.stdout", output):
            status = doctor.main()

        self.assertEqual(status, 0)
        self.assertIn("offline_ready: true", output.getvalue())
        self.assertIn("production_ready: false", output.getvalue())

    def test_json_mode_returns_failure_for_missing_required_dependency(self) -> None:
        report = {"ok": False, "offline_ready": True, "production_ready": False, "checks": {}}
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["doctor.py", "--json", "--require-api-key"]), mock.patch(
            "doctor.inspect_environment", return_value=report
        ) as inspect, mock.patch("sys.stdout", output):
            status = doctor.main()

        self.assertEqual(status, 1)
        inspect.assert_called_once_with(require_api_key=True)
        self.assertFalse(json.loads(output.getvalue())["ok"])


if __name__ == "__main__":
    unittest.main()
