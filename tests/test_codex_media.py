from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import codex_media  # noqa: E402


class CodexMediaManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.beats_path = self.project / "beats.json"
        self.beats_path.write_text(
            json.dumps(
                {
                    "project": "demo",
                    "aspect": "9:16",
                    "style": "collage",
                    "theme": "swiss-modern",
                    "beats": [
                        {
                            "id": 1,
                            "title_cn": "钩子",
                            "title_en": "THE HOOK",
                            "bg": "warm ivory",
                            "feel": "editorial",
                            "shots": [
                                {
                                    "id": "a",
                                    "dur": 6,
                                    "title": True,
                                    "scene": "a paper city crossed by a red route",
                                    "camera_move": "push_in",
                                    "element_motion": "the route draws forward",
                                }
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_prepare_keyframes_builds_codex_imagegen_task(self) -> None:
        manifest = codex_media.prepare_manifest(self.project, stage="keyframes")
        task = manifest["tasks"][0]

        self.assertEqual(task["key"], "1a")
        self.assertEqual(task["provider"], "codex-imagegen")
        self.assertEqual(task["aspect"], "9:16")
        self.assertEqual(Path(task["output_path"]).parts[-2:], ("keyframes", "kf_1a.png"))
        self.assertIn("paper city", task["prompt"])
        self.assertEqual(task["status"], "pending")

    def test_prepare_bakeoff_builds_one_imagegen_task_per_theme(self) -> None:
        manifest = codex_media.prepare_manifest(
            self.project,
            stage="bakeoff",
            styles=["swiss-modern", "punk-zine"],
        )

        self.assertEqual([task["key"] for task in manifest["tasks"]], ["swiss-modern", "punk-zine"])
        self.assertTrue(all(task["provider"] == "codex-imagegen" for task in manifest["tasks"]))
        self.assertTrue(all("style-bakeoff" in task["output_path"] for task in manifest["tasks"]))
        self.assertNotEqual(manifest["tasks"][0]["prompt"], manifest["tasks"][1]["prompt"])

    def test_rejects_unsafe_style_and_shot_identifiers(self) -> None:
        with self.assertRaisesRegex(ValueError, "identifier"):
            codex_media.prepare_manifest(self.project, stage="bakeoff", styles=["../../outside"])

        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        document["beats"][0]["id"] = "../../outside"
        self.beats_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "identifier"):
            codex_media.prepare_manifest(self.project, stage="keyframes")

    def test_select_style_updates_project_theme(self) -> None:
        codex_media.select_style(self.project, "punk-zine")
        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        self.assertEqual(document["theme"], "punk-zine")

    def test_prepare_supergrok_uses_local_keyframe_and_motion_prompt(self) -> None:
        keyframe = self.project / "keyframes" / "kf_1a.png"
        keyframe.parent.mkdir()
        keyframe.write_bytes(b"png")
        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        document["beats"][0]["shots"][0]["keyframe_path"] = str(keyframe)
        self.beats_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")

        manifest = codex_media.prepare_manifest(self.project, stage="supergrok")
        task = manifest["tasks"][0]

        self.assertEqual(task["provider"], "supergrok")
        self.assertEqual(task["input_path"], str(keyframe.resolve()))
        self.assertEqual(Path(task["output_path"]).parts[-2:], ("clips", "clip_1a.mp4"))
        self.assertIn("push-in", task["prompt"])
        self.assertEqual(task["duration"], 6)

    def test_supergrok_enforces_six_second_minimum_and_keeps_trim_target(self) -> None:
        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        document["beats"][0]["shots"][0]["dur"] = 2
        keyframe = self.project / "keyframes" / "kf_1a.png"
        keyframe.parent.mkdir()
        keyframe.write_bytes(b"png")
        document["beats"][0]["shots"][0]["keyframe_path"] = str(keyframe)
        self.beats_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")

        task = codex_media.prepare_manifest(self.project, stage="supergrok")["tasks"][0]

        self.assertEqual(task["duration"], 6)
        self.assertEqual(task["trim_to"], 2)
        self.assertIn("last 2 seconds", task["prompt"])

    def test_record_output_updates_beats_and_manifest(self) -> None:
        manifest = codex_media.prepare_manifest(self.project, stage="keyframes")
        output = self.project / "keyframes" / "kf_1a.png"
        output.parent.mkdir(exist_ok=True)
        output.write_bytes(b"png")

        codex_media.record_output(self.project, stage="keyframes", key="1a", output_path=output)

        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        shot = document["beats"][0]["shots"][0]
        updated_manifest = json.loads((self.project / "codex-media.json").read_text(encoding="utf-8"))
        self.assertEqual(shot["keyframe_path"], str(output.resolve()))
        self.assertEqual(updated_manifest["tasks"][0]["status"], "complete")

    def test_record_copies_external_output_into_project(self) -> None:
        codex_media.prepare_manifest(self.project, stage="keyframes")
        with tempfile.TemporaryDirectory() as external_dir:
            external = Path(external_dir) / "generated.png"
            external.write_bytes(b"png")
            codex_media.record_output(
                self.project, stage="keyframes", key="1a", output_path=external
            )

        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        recorded = Path(document["beats"][0]["shots"][0]["keyframe_path"])
        self.assertEqual(recorded, (self.project / "keyframes" / "kf_1a.png").resolve())
        self.assertEqual(recorded.read_bytes(), b"png")

    def test_missing_inputs_and_invalid_stage_raise(self) -> None:
        with self.assertRaisesRegex(ValueError, "stage"):
            codex_media.prepare_manifest(self.project, stage="unknown")
        with self.assertRaises(FileNotFoundError):
            codex_media.prepare_manifest(self.project / "missing", stage="keyframes")
        with self.assertRaises(FileNotFoundError):
            codex_media.record_output(
                self.project, stage="keyframes", key="1a", output_path=self.project / "missing.png"
            )

    def test_painterly_and_blocked_supergrok_paths(self) -> None:
        document = json.loads(self.beats_path.read_text(encoding="utf-8"))
        document["style"] = "painterly"
        document["era"] = "tang"
        document["beats"][0]["shots"][0]["motion"] = "clouds drift"
        self.beats_path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")

        keyframes = codex_media.prepare_manifest(self.project, stage="keyframes")
        supergrok = codex_media.prepare_manifest(self.project, stage="supergrok")

        self.assertIn("classical", keyframes["tasks"][0]["prompt"].lower())
        self.assertIn("clouds drift", supergrok["tasks"][0]["prompt"])
        self.assertEqual(supergrok["tasks"][0]["status"], "blocked")

    def test_existing_outputs_and_manifest_statuses_are_resumed(self) -> None:
        manifest = codex_media.prepare_manifest(self.project, stage="keyframes")
        manifest["tasks"][0]["status"] = "review"
        (self.project / "codex-media.json").write_text(json.dumps(manifest), encoding="utf-8")
        resumed = codex_media.prepare_manifest(self.project, stage="keyframes")
        self.assertEqual(resumed["tasks"][0]["status"], "review")

        output = self.project / "keyframes" / "kf_1a.png"
        output.parent.mkdir(exist_ok=True)
        output.write_bytes(b"png")
        complete = codex_media.prepare_manifest(self.project, stage="keyframes")
        self.assertEqual(complete["tasks"][0]["status"], "complete")

    def test_record_rejects_unknown_key_and_wrong_manifest_stage(self) -> None:
        codex_media.prepare_manifest(self.project, stage="keyframes")
        output = self.project / "keyframes" / "asset.png"
        output.parent.mkdir(exist_ok=True)
        output.write_bytes(b"png")
        with self.assertRaises(KeyError):
            codex_media.record_output(self.project, stage="keyframes", key="missing", output_path=output)

        with self.assertRaisesRegex(ValueError, "manifest stage"):
            codex_media.record_output(self.project, stage="supergrok", key="1a", output_path=output)


if __name__ == "__main__":
    unittest.main()
