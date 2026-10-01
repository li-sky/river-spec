"""Acceptance tests use temporary repositories; never recurse into the real SDD run."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).with_name("sdd.py")


class SDDTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="river-sdd-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.spec = self.root / "river-spec"
        self.code = self.root / "river-code"
        for directory in (self.spec / "scripts", self.code / "docs", self.code / "backend", self.code / "frontend", self.code / "scripts"):
            directory.mkdir(parents=True)
        shutil.copyfile(TOOL, self.spec / "scripts/sdd.py")
        # A separate one-test suite, not this suite, so run --check sdd is isolated.
        (self.spec / "scripts/test_sdd.py").write_text("import unittest\nclass Fixture(unittest.TestCase):\n def test_real_discovery(self): self.assertTrue(True)\n")
        (self.spec / "workflow.md").write_text("# Workflow\n\n## 行为\n\n预期行为。\n", encoding="utf-8")
        (self.spec / "README.md").write_text("[规格](workflow.md#行为)\n[源码](https://github.com/test/river-code/blob/main/backend/example.go)\n", encoding="utf-8")
        (self.code / "README.md").write_text("[规格](https://github.com/test/river-spec/blob/main/workflow.md#行为)\n")
        (self.code / "backend/example.go").write_text("package fixture\n")
        (self.code / "frontend/package.json").write_text('{"scripts":{"build":"exit 0"}}\n')
        (self.code / "scripts/test-media.sh").write_text("#!/bin/sh\nexit 0\n")
        self.mapping = {"schemaVersion": 1, "repository": "https://github.com/test/river-code",
                        "specRepository": "https://github.com/test/river-spec",
                        "documentation": {"url": "https://github.com/test/river-spec", "path": "README.md"},
                        "documents": [{"key": "workflow", "path": "workflow.md", "sources": ["backend"]}]}
        self.write_maps()
        self.git("init", "-q")
        self.git("config", "user.name", "SDD Fixture")
        self.git("config", "user.email", "sdd@example.invalid")
        self.commit()
        self.go = self.root / "fake-go"
        self.go.write_text(f"#!{sys.executable}\nimport os,sys\nif sys.argv[1:]==['version']:\n print('go version go1.23.0 fixture/fixture')\n sys.exit(0)\nif sys.argv[1]=='test' and os.environ.get('SDD_FIXTURE_FAIL'):\n sys.exit(23)\nprint('fixture check passed')\n")
        self.go.chmod(0o700)
        self.env = {**os.environ, "GO_BIN": str(self.go)}

    def write_maps(self):
        text = json.dumps(self.mapping, indent=2)
        (self.spec / "spec-map.json").write_text(text)
        (self.code / "docs/spec-map.json").write_text(text)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.code), *args], check=True, capture_output=True, text=True).stdout.strip()

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture baseline", "--allow-empty")
        return self.git("rev-parse", "HEAD")

    def cli(self, *args, expected=0, env=None, cwd=None):
        result = subprocess.run([sys.executable, str(self.spec / "scripts/sdd.py"), *args],
                                cwd=cwd or self.root, env=env or self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def plan_path(self, slug="change"):
        return self.spec / "plans" / (slug + ".md")

    def json_block(self, section, slug="change"):
        text = self.plan_path(slug).read_text(encoding="utf-8")
        tail = text.split("## " + section + "\n", 1)[1]
        return json.loads(tail.split("```json\n", 1)[1].split("```", 1)[0])

    def set_block(self, section, value, slug="change"):
        path = self.plan_path(slug)
        text = path.read_text(encoding="utf-8")
        beginning, tail = text.split("## " + section + "\n", 1)
        before, rest = tail.split("```json\n", 1)
        _, after = rest.split("```", 1)
        path.write_text(beginning + "## " + section + "\n" + before + "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```" + after, encoding="utf-8")

    def prepare(self, risk="docs", start=True):
        self.cli("new", "change", "--title", "修复明确问题", "--spec", "workflow", "--risk", risk)
        path = self.plan_path()
        text = path.read_text(encoding="utf-8").replace("TODO: 描述触发条件、实际问题和用户目标。", "实际问题影响用户，应修复。")
        text = text.replace("TODO: 明确期望行为、影响范围和边界。", "修复已说明的行为并保留兼容性。")
        text = text.replace("TODO: 填写可人工或自动验证的场景。", "用户完成操作时得到预期结果。")
        text = text.replace("TODO: 填写实现与规格同步任务。", "实现并同步规格及检查。")
        path.write_text(text, encoding="utf-8")
        if start:
            self.cli("start", "plans/change.md", "--code-dir", str(self.code))

    def review_and_check_boxes(self):
        path = self.plan_path()
        text = path.read_text(encoding="utf-8").replace("- [ ]", "- [x]")
        text = text.replace("TODO: 完成后补充实现差异审阅和人工验收结论。", "已核对实现差异，人工确认全部验收场景通过。")
        path.write_text(text, encoding="utf-8")

    def run_checks(self, expected=0, *extra, env=None):
        return self.cli("run", "plans/change.md", "--code-dir", str(self.code), *extra, expected=expected, env=env)

    def finish(self, expected=0):
        return self.cli("finish", "plans/change.md", "--code-dir", str(self.code), expected=expected)

    def test_new_does_not_overwrite_or_allow_path_slugs(self):
        for slug in ("../outside", "/tmp/outside", "Upper", "two--hyphens", ".hidden"):
            self.cli("new", slug, "--title", "Title", "--spec", "workflow", "--risk", "docs", expected=1)
        self.cli("new", "change", "--title", "Title", "--spec", "workflow", "--risk", "docs")
        before = self.plan_path().read_bytes()
        self.cli("new", "change", "--title", "Another", "--spec", "workflow", "--risk", "docs", expected=1)
        self.assertEqual(before, self.plan_path().read_bytes())

    def test_new_placeholders_rejected_but_pending_review_allowed(self):
        self.cli("new", "change", "--title", "Title", "--spec", "workflow", "--risk", "docs")
        self.cli("check", "plans/change.md", expected=1)
        self.plan_path().unlink()
        self.prepare(start=False)
        self.cli("check", "plans/change.md", cwd=self.code)
        self.cli("start", "plans/change.md", cwd=self.code)
        self.assertEqual(self.json_block("元信息")["status"], "in_progress")

    def test_run_and_finish_require_start(self):
        self.prepare(start=False)
        self.run_checks(expected=1)
        self.review_and_check_boxes()
        self.finish(expected=1)
        self.assertEqual(self.json_block("元信息")["status"], "draft")
        self.assertEqual(self.json_block("验证记录")["runs"], [])

    def test_legal_closure_and_checkbox_review_do_not_invalidate(self):
        self.prepare()
        self.run_checks()
        run = self.json_block("验证记录")["runs"][-1]
        self.assertEqual(run["check"], "links")
        self.assertTrue(run["codeClean"])
        self.assertEqual(run["toolSha256"], hashlib.sha256((self.spec / "scripts/sdd.py").read_bytes()).hexdigest())
        self.assertTrue(run["at"].endswith("Z"))
        self.review_and_check_boxes()
        self.finish()
        self.assertEqual(self.json_block("元信息")["status"], "done")
        self.assertEqual(self.json_block("验证记录")["delivery"]["status"], "not_released")
        self.cli("start", "plans/change.md", expected=1)
        self.run_checks(expected=1)

    def test_finish_requires_ac_tasks_and_real_review(self):
        self.prepare()
        self.run_checks()
        self.finish(expected=1)
        path = self.plan_path()
        path.write_text(path.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")
        self.finish(expected=1)
        self.review_and_check_boxes()
        self.finish()

    def test_failed_command_recorded_and_latest_failure_blocks_finish(self):
        self.prepare(risk="rules")
        self.run_checks()
        self.run_checks(expected=1, env={**self.env, "SDD_FIXTURE_FAIL": "yes"})
        runs = self.json_block("验证记录")["runs"]
        last = runs[-1]
        self.assertEqual(last["check"], "backend")
        self.assertEqual(last["exitCode"], 23)
        self.assertEqual(last["commands"][-1]["exitCode"], 23)
        self.assertEqual(last["commands"][-1]["argv"][1:], ["test", "./..."])
        self.assertEqual(last["commands"][-1]["cwd"], str(self.code / "backend"))
        self.review_and_check_boxes()
        self.finish(expected=1)
        self.run_checks()
        self.finish()

    def test_finish_blocks_untracked_dirty_and_records_dirty_runs(self):
        self.prepare()
        (self.code / "untracked.txt").write_text("dirty")
        self.run_checks()
        self.assertFalse(self.json_block("验证记录")["runs"][-1]["codeClean"])
        self.review_and_check_boxes()
        self.finish(expected=1)
        (self.code / "untracked.txt").unlink()
        self.finish(expected=1)  # Cleaning later cannot make old dirty evidence valid.
        self.run_checks()
        (self.code / "backend/example.go").write_text("package changed\n")
        self.finish(expected=1)

    def test_changed_head_invalidates_successful_evidence(self):
        self.prepare()
        self.run_checks()
        self.review_and_check_boxes()
        self.commit()
        self.finish(expected=1)
        self.run_checks()
        self.finish()

    def test_changed_plan_spec_tool_tests_and_map_invalidate(self):
        for changed in ("requirement", "spec", "tool", "support", "map"):
            with self.subTest(changed=changed):
                if self.plan_path().exists():
                    self.plan_path().unlink()
                self.prepare()
                self.run_checks()
                self.review_and_check_boxes()
                if changed == "requirement":
                    path = self.plan_path()
                    path.write_text(path.read_text(encoding="utf-8").replace("预期结果。", "新的预期结果。"), encoding="utf-8")
                elif changed == "spec":
                    with (self.spec / "workflow.md").open("a", encoding="utf-8") as stream: stream.write("\n新要求\n")
                elif changed == "tool":
                    with (self.spec / "scripts/sdd.py").open("a") as stream: stream.write("\n# implementation revision\n")
                elif changed == "support":
                    with (self.spec / "scripts/test_sdd.py").open("a") as stream: stream.write("\n# test revision\n")
                else:
                    self.mapping["sourceBaseline"] = "different"
                    (self.spec / "spec-map.json").write_text(json.dumps(self.mapping))
                self.finish(expected=1)
                if changed == "map":
                    self.write_maps()
                    self.commit()
                self.run_checks()
                self.finish()

    def test_risk_minimum_checks_and_unknown_custom_commands_rejected(self):
        self.prepare(risk="rules")
        meta = self.json_block("元信息")
        meta["checks"] = ["links"]
        self.set_block("元信息", meta)
        self.cli("check", "plans/change.md", expected=1)
        meta["checks"] = ["links", "backend", "shell"]
        self.set_block("元信息", meta)
        self.cli("check", "plans/change.md", expected=1)
        self.cli("run", "plans/change.md", "--check", "shell", expected=2)

    def test_selected_checks_cannot_skip_required_evidence(self):
        self.prepare(risk="rules")
        self.run_checks(0, "--check", "links")
        self.review_and_check_boxes()
        self.finish(expected=1)
        self.run_checks(0, "--check", "backend")
        self.finish()

    def test_cancelled_never_reopened_or_released(self):
        self.prepare()
        meta = self.json_block("元信息"); meta["status"] = "cancelled"
        self.set_block("元信息", meta)
        original = self.plan_path().read_bytes()
        self.cli("start", "plans/change.md", expected=1)
        self.run_checks(expected=1)
        self.review_and_check_boxes()
        self.finish(expected=1)
        self.assertEqual(self.json_block("验证记录")["delivery"]["status"], "not_released")
        self.assertEqual(self.json_block("元信息")["status"], "cancelled")

    def test_plan_traversal_and_symlink_escape_rejected(self):
        self.prepare()
        outside = self.root / "outside.md"
        outside.write_bytes(self.plan_path().read_bytes())
        self.cli("check", "../outside.md", expected=1)
        self.cli("check", "plans/../plans/change.md", expected=1)
        self.cli("check", str(outside), expected=1)
        (self.spec / "plans/escape.md").symlink_to(outside)
        self.cli("check", "plans/escape.md", expected=1)
        self.plan_path().unlink()
        (self.spec / "plans").rename(self.spec / "old-plans")
        (self.spec / "plans").symlink_to(self.root)
        self.cli("new", "escape", "--title", "Title", "--spec", "workflow", "--risk", "docs", expected=1)

    def test_links_reject_missing_local_and_github_targets_and_map_mismatch(self):
        self.prepare()
        for link in ("[bad](missing.md)", "[bad](https://github.com/test/river-code/blob/main/backend/missing.go)", "[bad](workflow.md#不存在)", "[bad](../../outside.md)"):
            with self.subTest(link=link):
                original = (self.spec / "README.md").read_text(encoding="utf-8")
                (self.spec / "README.md").write_text(original + "\n" + link, encoding="utf-8")
                self.run_checks(expected=1)
                (self.spec / "README.md").write_text(original, encoding="utf-8")
        (self.code / "docs/spec-map.json").write_text("{}")
        self.run_checks(expected=1)

    def test_sources_and_duplicate_spec_keys_rejected(self):
        self.prepare()
        self.mapping["documents"][0]["sources"] = ["missing"]
        self.write_maps(); self.commit()
        self.run_checks(expected=1)
        self.mapping["documents"].append(self.mapping["documents"][0].copy())
        self.write_maps()
        self.cli("check", "plans/change.md", expected=1)

    def test_empty_sdd_suite_is_rejected_and_real_fixture_suite_passes(self):
        self.prepare(risk="tooling")
        test = self.spec / "scripts/test_sdd.py"
        original = test.read_text()
        test.unlink()
        self.run_checks(expected=1)
        self.assertEqual(self.json_block("验证记录")["runs"][-1]["exitCode"], 1)
        test.write_text("# no tests\n")
        self.run_checks(expected=1)
        test.write_text(original)
        self.run_checks()
        self.review_and_check_boxes()
        self.finish()

    def test_profile_commands_cannot_be_missing_relabelled_or_wrong_cwd(self):
        self.prepare(risk="rules")
        self.run_checks()
        self.review_and_check_boxes()
        evidence = self.json_block("验证记录")
        for alteration in ("partial", "wrongargv", "wrongcwd", "failedcommand"):
            with self.subTest(alteration=alteration):
                changed = json.loads(json.dumps(evidence))
                record = changed["runs"][-1]
                if alteration == "partial": record["commands"] = record["commands"][:1]
                if alteration == "wrongargv": record["commands"][-1]["argv"] = ["npm", "run", "build"]
                if alteration == "wrongcwd": record["commands"][-1]["cwd"] = str(self.spec)
                if alteration == "failedcommand": record["commands"][-1]["exitCode"] = 9
                self.set_block("验证记录", changed)
                self.finish(expected=1)
        self.set_block("验证记录", evidence)
        self.finish()

    def test_missing_executable_failure_is_recorded(self):
        self.prepare(risk="rules")
        self.run_checks(expected=1, env={**self.env, "GO_BIN": str(self.root / "absent-go")})
        record = self.json_block("验证记录")["runs"][-1]
        self.assertEqual(record["exitCode"], 127)
        self.assertEqual(record["commands"][0]["exitCode"], 127)

    def test_concurrent_requirement_edit_is_not_overwritten(self):
        self.prepare()
        definition = importlib.util.spec_from_file_location("fixture_sdd", self.spec / "scripts/sdd.py")
        module = importlib.util.module_from_spec(definition)
        definition.loader.exec_module(module)
        loaded = module.Plan("plans/change.md")
        changed = self.plan_path().read_text(encoding="utf-8").replace("实际问题影响用户", "人工新增需求影响用户")
        self.plan_path().write_text(changed, encoding="utf-8")
        loaded.meta["status"] = "done"
        with self.assertRaises(module.GateError):
            loaded.save()
        self.assertEqual(self.plan_path().read_text(encoding="utf-8"), changed)


if __name__ == "__main__":
    unittest.main()
