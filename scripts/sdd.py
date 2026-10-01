#!/usr/bin/env python3
"""Local two-repository SDD gates. Python 3.11+, no network or shell execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit

SPEC_ROOT = Path(__file__).resolve().parent.parent
TOOL_PATH = Path(__file__).resolve()
PROFILES = {"links", "sdd", "backend", "frontend", "media"}
MINIMUM = {
    "docs": ["links"], "tooling": ["links", "sdd"],
    "ui": ["links", "frontend"], "rules": ["links", "backend"],
    "service": ["links", "backend"], "storage": ["links", "backend"],
    "media": ["links", "frontend", "media"],
}
SECTIONS = ["元信息", "问题与目标", "预期行为与范围", "验收场景", "任务", "审阅结论", "验证记录"]
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
JSON_BLOCK = re.compile(r"(?ms)^```json[ \t]*\n(.*?)^```[ \t]*(?:\n|$)")
BOX = re.compile(r"^\s*-\s+\[([ xX])\]\s+(AC-\d{2,}|T-\d{2,}):\s*(.*)$")
PLACEHOLDER = re.compile(r"(?mi)^\s*(?:[-*]\s*)?(?:TODO|TBD|待填写|待补充|待审阅|尚未审阅|未审阅)(?:\b|[:：\s]|$)")
IGNORED_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "vendor", "__pycache__"}


class GateError(Exception):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(path: Path, root: Path) -> bool:
    return path.is_relative_to(root.resolve())


def confined(root: Path, value: str | Path) -> Path:
    path = (root / value).resolve()
    if not within(path, root):
        raise GateError(f"路径越出仓库：{value}")
    return path


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GateError(f"无法读取 JSON：{path}: {exc}") from exc


def spec_map() -> tuple[dict, dict[str, dict]]:
    mapping = read_json(SPEC_ROOT / "spec-map.json")
    if not isinstance(mapping, dict) or not isinstance(mapping.get("documents"), list):
        raise GateError("spec-map.json 必须包含 documents 数组")
    documents = {}
    for document in mapping["documents"]:
        if not isinstance(document, dict):
            raise GateError("spec-map 文档条目必须是对象")
        key, path, sources = document.get("key"), document.get("path"), document.get("sources")
        if not isinstance(key, str) or not key or key in documents:
            raise GateError("spec-map 文档 key 必须非空且唯一")
        if not isinstance(path, str) or not path or not isinstance(sources, list) or any(not isinstance(s, str) or not s for s in sources):
            raise GateError(f"spec-map {key} 的 path/sources 无效")
        target = confined(SPEC_ROOT, path)
        if not target.is_file():
            raise GateError(f"规格文件不存在：{path}")
        documents[key] = document
    return mapping, documents


def placeholder(text: str) -> bool:
    return not text.strip() or bool(PLACEHOLDER.search(text))


class Plan:
    def __init__(self, value: str | Path):
        if ".." in Path(value).parts:
            raise GateError("计划路径不能包含 .. 穿越段")
        self.path = confined(SPEC_ROOT, value)
        plans = confined(SPEC_ROOT, "plans")
        if not within(self.path, plans) or self.path.parent != plans or self.path.suffix != ".md":
            raise GateError("计划必须位于 SPEC_ROOT/plans/<slug>.md")
        try:
            self.text = self.path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GateError(f"无法读取计划：{self.path}: {exc}") from exc
        self.sections = {}
        self.spans = {}
        headings = []
        offset, fence = 0, None
        for line in self.text.splitlines(keepends=True):
            marker = re.match(r"^\s*(`{3,}|~{3,})", line)
            if marker:
                char = marker.group(1)[0]
                fence = None if fence == char else char if fence is None else fence
            elif fence is None:
                match = re.match(r"^##\s+(.+?)\s*$", line)
                if match:
                    headings.append((match.group(1), offset, offset + len(line)))
            offset += len(line)
        self.preamble = self.text[:headings[0][1]] if headings else self.text
        for index, (name, begin, content_begin) in enumerate(headings):
            end = headings[index + 1][1] if index + 1 < len(headings) else len(self.text)
            if name in self.sections:
                raise GateError(f"重复章节：{name}")
            self.sections[name] = self.text[content_begin:end]
            self.spans[name] = (begin, content_begin, end)
        for name in SECTIONS:
            if name not in self.sections:
                raise GateError(f"缺少章节：{name}")
        self.meta = self.json_section("元信息")
        self.evidence = self.json_section("验证记录")

    def json_section(self, name: str) -> dict:
        blocks = list(JSON_BLOCK.finditer(self.sections[name]))
        if len(blocks) != 1:
            raise GateError(f"{name} 必须包含一个 fenced json 对象")
        try:
            value = json.loads(blocks[0].group(1))
        except ValueError as exc:
            raise GateError(f"{name} JSON 无效：{exc}") from exc
        if not isinstance(value, dict):
            raise GateError(f"{name} JSON 必须是对象")
        return value

    def items(self, name: str, prefix: str) -> list[tuple[bool, str, str]]:
        items, seen = [], set()
        for line in self.sections[name].splitlines():
            match = BOX.match(line)
            if not match:
                if re.match(r"^\s*-\s+\[", line):
                    raise GateError(f"{name} 中的复选框必须使用 {prefix}-01: 文本")
                continue
            checked, key, text = match.groups()
            if not key.startswith(prefix + "-") or key in seen or placeholder(text):
                raise GateError(f"{name} 条目无效或未填写：{key}")
            seen.add(key)
            items.append((checked.lower() == "x", key, text))
        if not items or placeholder(self.sections[name]):
            raise GateError(f"{name} 至少需要一项非占位条目")
        return items

    def validate(self, final: bool = False) -> None:
        expected = {"id", "status", "specs", "risk", "checks"}
        if set(self.meta) != expected:
            raise GateError("元信息字段应为 id/status/specs/risk/checks")
        slug = self.meta["id"]
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug != self.path.stem:
            raise GateError("计划 id 必须与安全文件名 slug 一致")
        if not isinstance(self.meta["status"], str) or self.meta["status"] not in {"draft", "in_progress", "done", "cancelled"}:
            raise GateError("未知计划状态")
        risk, checks, specs = self.meta["risk"], self.meta["checks"], self.meta["specs"]
        if not isinstance(risk, str) or risk not in MINIMUM:
            raise GateError("未知 risk")
        for name, values in (("checks", checks), ("specs", specs)):
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
                raise GateError(f"{name} 必须是非空、无重复的字符串数组")
        if set(checks) - PROFILES or not set(MINIMUM[risk]).issubset(checks):
            raise GateError(f"{risk} 至少需要检查：{', '.join(MINIMUM[risk])}；仅允许固定 profiles")
        _, documents = spec_map()
        if any(key not in documents for key in specs):
            raise GateError("计划引用了未知 spec key")
        title = re.search(r"(?m)^#\s+(.+)$", self.preamble)
        if title is None or placeholder(title.group(1)):
            raise GateError("计划标题未填写")
        for name in ("问题与目标", "预期行为与范围"):
            if placeholder(self.sections[name]):
                raise GateError(f"{name} 未填写")
        ac, tasks = self.items("验收场景", "AC"), self.items("任务", "T")
        ev = self.evidence
        if not isinstance(ev.get("runs"), list) or not isinstance(ev.get("codeCommit"), str) or not isinstance(ev.get("delivery"), dict):
            raise GateError("验证记录需要 runs/codeCommit/delivery")
        if not isinstance(ev["delivery"].get("status"), str) or not isinstance(ev["delivery"].get("notes"), str):
            raise GateError("delivery 需要字符串 status/notes")
        if final:
            if placeholder(self.sections["审阅结论"]):
                raise GateError("finish 需要明确的非占位审阅结论")
            if not all(item[0] for item in ac + tasks):
                raise GateError("finish 需要人工勾选全部 AC/T")

    def fingerprint(self) -> str:
        sections = {name: re.sub(r"(?m)^(\s*-\s+)\[[ xX]\](\s+)", r"\1[]\2", content).strip()
                    for name, content in self.sections.items()
                    if name not in {"元信息", "验证记录", "审阅结论"}}
        payload = {"title": self.preamble.strip(), "metadata": {k: v for k, v in self.meta.items() if k != "status"}, "sections": sections}
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

    def save(self) -> None:
        if self.path.read_text(encoding="utf-8") != self.text:
            raise GateError("计划执行期间被外部修改；未覆盖文件，请重新检查")
        replacements = []
        for name, value in (("元信息", self.meta), ("验证记录", self.evidence)):
            block = JSON_BLOCK.search(self.sections[name])
            assert block is not None
            begin = self.spans[name][1] + block.start(1)
            end = self.spans[name][1] + block.end(1)
            replacements.append((begin, end, json.dumps(value, ensure_ascii=False, indent=2) + "\n"))
        text = self.text
        for begin, end, replacement in sorted(replacements, reverse=True):
            text = text[:begin] + replacement + text[end:]
        descriptor, temporary = tempfile.mkstemp(prefix=".sdd-", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(text)
            os.replace(temporary, self.path)
            self.__init__(self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def anchors(path: Path) -> set[str]:
    headings, counts = set(), {}
    for line in strip_code(path.read_text(encoding="utf-8")).splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", match.group(1))
        text = re.sub(r"<[^>]+>", "", text).replace("`", "")
        key = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
        number = counts.get(key, 0)
        counts[key] = number + 1
        headings.add(key + (f"-{number}" if number else ""))
    return headings


def strip_code(text: str) -> str:
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            char = marker.group(1)[0]
            fence = None if fence == char else char if fence is None else fence
            lines.append("")
        elif fence is None:
            lines.append(line)
    return "\n".join(lines)


def markdown_targets(text: str):
    text = strip_code(text)
    text = re.sub(r"`+[^`\n]*`+", "", text)
    inline = r"(?<!\\)!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[^)]*)?\)"
    reference = r"(?m)^\s*\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)"
    for pattern in (inline, reference):
        for match in re.finditer(pattern, text):
            yield match.group(1).strip("<>")
    for match in re.finditer(r"<(https?://[^>]+)>", text):
        yield match.group(1)


def check_links(code_dir: Path) -> None:
    mapping, documents = spec_map()
    mirror = read_json(code_dir / "docs/spec-map.json")
    if mirror != mapping:
        raise GateError("两边 spec-map.json 不一致")
    for key, document in documents.items():
        for source in document["sources"]:
            if not confined(code_dir, source).exists():
                raise GateError(f"{key} 源码路径不存在：{source}")
    roots = [SPEC_ROOT.resolve(), code_dir.resolve()]
    repositories = {}
    for url, root in ((mapping.get("repository"), code_dir),
                      (mapping.get("specRepository") or mapping.get("documentation", {}).get("url"), SPEC_ROOT)):
        if not isinstance(url, str) or urlsplit(url).hostname != "github.com":
            raise GateError("spec-map 需要两个 GitHub 仓库 URL")
        repositories[urlsplit(url).path.rstrip("/").removesuffix(".git")] = root.resolve()
    errors = []
    for root in roots:
        for markdown in root.rglob("*.md"):
            if any(part in IGNORED_DIRS for part in markdown.relative_to(root).parts):
                continue
            if not any(within(markdown.resolve(), allowed) for allowed in roots):
                errors.append(f"Markdown symlink 越出仓库：{markdown}")
                continue
            for target in markdown_targets(markdown.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                path = None
                if parsed.scheme or parsed.netloc:
                    if parsed.hostname != "github.com":
                        continue
                    pieces = unquote(parsed.path).split("/")
                    repo = "/" + "/".join(pieces[1:3])
                    if repo not in repositories:
                        continue
                    if len(pieces) == 3 or pieces[3:] == [""]:
                        path = repositories[repo]
                    elif len(pieces) >= 5 and pieces[3] in {"blob", "tree"}:
                        path = (repositories[repo] / "/".join(pieces[5:])).resolve()
                    else:
                        continue  # issues/commits/releases are not repository file paths.
                else:
                    value = unquote(parsed.path)
                    path = (markdown.parent / value).resolve() if value else markdown.resolve()
                if not any(within(path, allowed) for allowed in roots):
                    errors.append(f"{markdown.relative_to(root)}: 链接越出仓库：{target}")
                elif not path.exists():
                    errors.append(f"{markdown.relative_to(root)}: 链接不存在：{target}")
                elif parsed.fragment and path.is_file() and path.suffix == ".md":
                    if unquote(parsed.fragment) not in anchors(path):
                        errors.append(f"{markdown.relative_to(root)}: 标题锚点不存在：{target}")
    if errors:
        raise GateError("\n".join(errors))
    print("PASS links: 双仓库 Markdown、本地 GitHub 对应路径、spec-map 与 sources", flush=True)


def git_state(code_dir: Path) -> tuple[str, bool]:
    if not code_dir.is_dir():
        raise GateError(f"代码目录不存在：{code_dir}")
    results = []
    for args in (("rev-parse", "--show-toplevel"), ("rev-parse", "HEAD"), ("status", "--porcelain", "--untracked-files=all")):
        result = subprocess.run(["git", "-C", str(code_dir), *args], text=True, capture_output=True, check=False)
        if result.returncode:
            raise GateError(f"代码仓库 Git 操作失败：{' '.join(args)}")
        results.append(result.stdout.strip())
    if Path(results[0]).resolve() != code_dir.resolve():
        raise GateError("--code-dir 必须指向代码 Git 仓库根目录")
    return results[1], not bool(results[2])


def current_context(plan: Plan) -> dict:
    _, documents = spec_map()
    support = confined(SPEC_ROOT, "scripts/test_sdd.py")
    return {
        "toolSha256": digest(TOOL_PATH),
        "supportSha256": {"scripts/test_sdd.py": digest(support) if support.is_file() else None},
        "specMapSha256": digest(SPEC_ROOT / "spec-map.json"),
        "specSha256": {key: digest(confined(SPEC_ROOT, documents[key]["path"])) for key in plan.meta["specs"]},
        "planFingerprint": plan.fingerprint(),
    }


def commands_for(profile: str, code_dir: Path) -> list[tuple[list[str], Path]]:
    if profile == "links":
        return []  # Internal checker executes no shell/subprocess commands.
    if profile == "sdd":
        return [([sys.executable, "-m", "unittest", "discover", "-s", "scripts", "-p", "test_sdd.py"], SPEC_ROOT)]
    if profile == "backend":
        go = os.environ.get("GO_BIN") or shutil.which("go") or "go"
        return [([go, "version"], code_dir / "backend"), ([go, "test", "./..."], code_dir / "backend"), ([go, "vet", "./..."], code_dir / "backend")]
    if profile == "frontend":
        return [(["npm", "run", "build"], code_dir / "frontend")]
    if profile == "media":
        return [(["bash", "scripts/test-media.sh"], code_dir)]
    raise GateError(f"未知检查：{profile}")


def execute_command(argv: list[str], cwd: Path, capture: bool = False) -> tuple[int, str]:
    print(f"检查命令 argv={json.dumps(argv, ensure_ascii=False)} cwd={cwd}", flush=True)
    try:
        result = subprocess.run(argv, cwd=cwd, check=False, capture_output=capture, text=capture)
        output = ""
        if capture:
            output = result.stdout + result.stderr
            print(result.stdout, end="", flush=True)
            print(result.stderr, end="", file=sys.stderr, flush=True)
        return result.returncode, output
    except OSError as exc:
        print(f"无法执行检查：{exc}", file=sys.stderr)
        return 127, ""


def run_checks(plan: Plan, code_dir: Path, selected: list[str] | None) -> bool:
    profiles = selected if selected else plan.meta["checks"]
    if len(set(profiles)) != len(profiles) or any(p not in plan.meta["checks"] for p in profiles):
        raise GateError("--check 必须为计划 checks 中无重复的固定 profile")
    all_passed = True
    for profile in profiles:
        commit, clean_before = git_state(code_dir)
        context = current_context(plan)
        record = {"check": profile, "commands": [], "exitCode": 0,
                  "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                  "codeCommit": commit, "codeClean": clean_before, **context}
        print(f"运行 {profile}", flush=True)
        if profile == "links":
            try:
                check_links(code_dir)
            except (GateError, OSError) as exc:
                print(str(exc), file=sys.stderr)
                record["exitCode"] = 1
        elif profile == "sdd" and not confined(SPEC_ROOT, "scripts/test_sdd.py").is_file():
            print("SDD 检查需要 scripts/test_sdd.py，不能通过空测试。", file=sys.stderr)
            record["exitCode"] = 1
        else:
            for argv, cwd in commands_for(profile, code_dir):
                capture = profile == "sdd" or (profile == "backend" and argv[1:] == ["version"])
                exit_code, output = execute_command(argv, cwd, capture=capture)
                record["commands"].append({"argv": argv, "cwd": str(cwd), "exitCode": exit_code})
                if exit_code:
                    record["exitCode"] = exit_code
                    break
                if profile == "sdd" and not re.search(r"Ran\s+[1-9]\d*\s+tests?\b", output):
                    print("SDD 未发现实际测试，拒绝空成功证据。", file=sys.stderr)
                    record["exitCode"] = 1
                    break
                if profile == "backend" and argv[1:] == ["version"] and not output.startswith("go version go"):
                    print("GO_BIN/Go 命令未返回标准 Go 版本；请指定真正的 Go 编译器。", file=sys.stderr)
                    record["exitCode"] = 1
                    break
        try:
            after_commit, clean_after = git_state(code_dir)
            record["codeClean"] = clean_before and clean_after and after_commit == commit
        except GateError:
            record["codeClean"] = False
        plan.evidence["runs"].append(record)
        plan.evidence["codeCommit"] = commit
        plan.save()  # Persist failed checks as well; no raw stdout/stderr logs are stored.
        print(f"{profile}: {'PASS' if record['exitCode'] == 0 else 'FAIL'}", flush=True)
        if not record["codeClean"]:
            print("证据对应的代码未保持清洁；提交代码后重新检查才能 finish。", flush=True)
        all_passed = all_passed and record["exitCode"] == 0
    return all_passed


def finish(plan: Plan, code_dir: Path) -> None:
    plan.validate(final=True)
    if plan.meta["status"] != "in_progress":
        raise GateError("finish 仅适用于已 start 的 in_progress 计划")
    commit, clean = git_state(code_dir)
    if not clean:
        raise GateError("finish 需要清洁的代码 worktree，包括未跟踪文件")
    if plan.evidence["codeCommit"] != commit:
        raise GateError("验证记录 codeCommit 与当前代码 HEAD 不一致")
    expected = current_context(plan)
    for profile in plan.meta["checks"]:
        matching = [r for r in plan.evidence["runs"] if isinstance(r, dict) and r.get("check") == profile]
        if not matching:
            raise GateError(f"缺少检查证据：{profile}")
        latest = matching[-1]
        if type(latest.get("exitCode")) is not int or latest["exitCode"] != 0:
            raise GateError(f"最新检查失败：{profile}")
        if latest.get("codeCommit") != commit or latest.get("codeClean") is not True:
            raise GateError(f"{profile} 的代码提交或清洁状态已过期")
        for key, value in expected.items():
            if latest.get(key) != value:
                raise GateError(f"{profile} 的 {key} 证据已过期；重新检查")
        commands = latest.get("commands")
        if not isinstance(commands, list) or (profile != "links" and not commands):
            raise GateError(f"{profile} 的命令证据缺失")
        if any(not isinstance(c, dict) or type(c.get("exitCode")) is not int or c["exitCode"] != 0 or not isinstance(c.get("argv"), list) or not isinstance(c.get("cwd"), str) for c in commands):
            raise GateError(f"{profile} 的命令证据无效")
        canonical = commands_for(profile, code_dir)
        if len(commands) != len(canonical):
            raise GateError(f"{profile} 的命令证据不完整")
        for command, (argv, cwd) in zip(commands, canonical):
            actual = command["argv"]
            # GO_BIN is selected at run time; retain its actual executable while
            # requiring the complete fixed version/test/vet sequence and cwd.
            matches = actual == argv
            if profile == "backend":
                matches = len(actual) == len(argv) and isinstance(actual[0], str) and bool(actual[0]) and actual[1:] == argv[1:]
                matches = matches and actual[0] == commands[0]["argv"][0]
            if not matches or command["cwd"] != str(cwd):
                raise GateError(f"{profile} 的命令与固定 profile 不符")
    plan.meta["status"] = "done"
    plan.save()
    print("完成：done；delivery 状态保持独立，未执行发布。")


def new_plan(slug: str, title: str, specs: list[str], risk: str) -> Path:
    if not SLUG.fullmatch(slug) or len(slug) > 80:
        raise GateError("slug 仅允许小写字母、数字和单个分隔连字符，长度不超过 80")
    if not title.strip() or "\n" in title or "\r" in title:
        raise GateError("标题必须为非空单行")
    _, documents = spec_map()
    if len(set(specs)) != len(specs) or any(key not in documents for key in specs):
        raise GateError("--spec 必须为无重复的 spec-map key")
    plans = confined(SPEC_ROOT, "plans")
    plans.mkdir(exist_ok=True)
    path = confined(SPEC_ROOT, f"plans/{slug}.md")
    meta = {"id": slug, "status": "draft", "specs": specs, "risk": risk, "checks": MINIMUM[risk]}
    evidence = {"runs": [], "codeCommit": "", "delivery": {"status": "not_released", "notes": ""}}
    text = f"# {title.strip()}\n\n## 元信息\n\n```json\n{json.dumps(meta, ensure_ascii=False, indent=2)}\n```\n\n## 问题与目标\n\nTODO: 描述触发条件、实际问题和用户目标。\n\n## 预期行为与范围\n\nTODO: 明确期望行为、影响范围和边界。\n\n## 验收场景\n\n- [ ] AC-01: TODO: 填写可人工或自动验证的场景。\n\n## 任务\n\n- [ ] T-01: TODO: 填写实现与规格同步任务。\n\n## 审阅结论\n\nTODO: 完成后补充实现差异审阅和人工验收结论。\n\n## 验证记录\n\n```json\n{json.dumps(evidence, ensure_ascii=False, indent=2)}\n```\n"
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    except FileExistsError as exc:
        raise GateError(f"计划已存在，不覆盖：{path}") from exc
    print(f"已创建 {path.relative_to(SPEC_ROOT)}；填写 TODO 后 check/start。")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new")
    new.add_argument("slug")
    new.add_argument("--title", required=True)
    new.add_argument("--spec", action="append", required=True)
    new.add_argument("--risk", choices=MINIMUM, required=True)
    for command in ("check", "start", "run", "finish"):
        argument = sub.add_parser(command)
        argument.add_argument("plan")
        argument.add_argument("--code-dir", type=Path, default=SPEC_ROOT.parent / "river-code")
        if command == "run":
            argument.add_argument("--check", action="append", choices=sorted(PROFILES))
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            new_plan(args.slug, args.title, args.spec, args.risk)
            return 0
        plan = Plan(args.plan)
        plan.validate()
        code_dir = args.code_dir.resolve()
        if args.command == "check":
            print("PASS plan: 需求、范围、AC/T、规格引用与最低检查完整；未宣称产品验收。")
        elif args.command == "start":
            if plan.meta["status"] in {"done", "cancelled"}:
                raise GateError("done/cancelled 计划不能重开")
            plan.meta["status"] = "in_progress"
            plan.save()
            print("状态：in_progress；AC 仍需人工确认。")
        elif args.command == "run":
            if plan.meta["status"] != "in_progress":
                raise GateError("run 仅适用于已 start 的 in_progress 计划")
            return 0 if run_checks(plan, code_dir, args.check) else 1
        elif args.command == "finish":
            finish(plan, code_dir)
        return 0
    except (GateError, OSError, ValueError) as exc:
        print(f"SDD: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
