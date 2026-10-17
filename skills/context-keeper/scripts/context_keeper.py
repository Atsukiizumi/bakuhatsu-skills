#!/usr/bin/env python3
"""Context Keeper v2: privacy-aware local helpers; no network / no destructive actions.

This script never summarizes hidden model state. Semantic checkpoint content belongs to
an Agent with access to the actual conversation and to the current project.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = {
    "INDEX.md": "INDEX.template.md",
    "ACTIVE.md": "ACTIVE.template.md",
    "HANDOFF.md": "HANDOFF.template.md",
}
REQUIRED = {
    "ACTIVE.md": ["当前目标", "P0 不可丢失约束", "当前工作与状态", "已修改及未提交内容", "已验证与未验证", "下一步"],
    "HANDOFF.md": ["当前目标与验收", "P0 不可丢失约束", "P1 任务状态", "工作现场", "权威证据与引用", "下一步", "恢复核验"],
}
SKIP = {".git", "node_modules", ".venv", "venv", "bin", "obj", "dist", "build", ".next", "target", ".idea"}
KNOWN_EVENTS = {"precompact", "postcompact", "precompress", "sessionstart", "beforeagent"}


def root_path(raw: str) -> Path:
    p = Path(raw).expanduser().resolve()
    if not p.is_dir():
        raise ValueError(f"项目目录不存在: {p}")
    return p


def git(root: Path, *args: str) -> str | None:
    try:
        cp = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=8, check=False)
        return cp.stdout.strip() if cp.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def context_files(root: Path) -> list[str]:
    found = []
    max_files = 200
    for base, dirs, files in os.walk(root):
        relative = Path(base).relative_to(root)
        if len(relative.parts) > 5:
            dirs[:] = []
            continue
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".cache")]
        for name in files:
            if name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "README.md", "SKILL.md", "HANDOFF.md", "ACTIVE.md") or name.lower().endswith(".adr.md"):
                found.append((relative / name).as_posix())
                if len(found) >= max_files:
                    return sorted(found)
    return sorted(found)


def scan(root: Path) -> dict:
    status = git(root, "status", "--short", "--branch", "--untracked-files=normal")
    head = git(root, "rev-parse", "--short", "HEAD")
    changes = (status or "").splitlines()
    # Return a bounded status preview. Git paths may be sensitive: callers should
    # review before sharing externally. Never read the actual source/log contents.
    return {
        "root": str(root), "is_git_repo": status is not None, "commit": head,
        "git_status_preview": changes[:80], "git_status_truncated": len(changes) > 80,
        "agent_context_files": context_files(root),
        "checkpoint_files": {name: (root / ".ai-context" / name).exists() for name in TEMPLATES},
        "note": "只读文件盘点；未分析当前会话、业务真实性或 token 用量。",
    }


def init(root: Path) -> dict:
    target = root / ".ai-context"
    target.mkdir(exist_ok=True)
    (target / "runtime").mkdir(exist_ok=True)
    (target / "archive").mkdir(exist_ok=True)
    created, preserved = [], []
    for name, template in TEMPLATES.items():
        dest = target / name
        if dest.exists():
            preserved.append(str(dest.relative_to(root)))
            continue
        # Exclusive creation: prevents races and never overwrites existing work.
        try:
            with dest.open("x", encoding="utf-8", newline="\n") as f:
                f.write((SKILL_ROOT / "assets" / template).read_text(encoding="utf-8"))
            created.append(str(dest.relative_to(root)))
        except FileExistsError:
            preserved.append(str(dest.relative_to(root)))
    return {"created": created, "preserved": preserved,
            "warning": "模板仍包含待填写内容；请由 Agent 核对代码、当前任务和 Git 后补全。"}


def validate(root: Path) -> dict:
    warnings: list[str] = []
    errors: list[str] = []
    summary: dict[str, dict] = {}
    for name, required in REQUIRED.items():
        p = root / ".ai-context" / name
        if not p.is_file():
            errors.append(f"缺失 {p.relative_to(root)}")
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        headings = set(re.findall(r"(?m)^##\s+(.+?)\s*$", raw))
        missing = [text for text in required if not any(h.startswith(text) for h in headings)]
        if missing:
            errors.append(f"{name} 缺少必要章节: {', '.join(missing)}")
        placeholders = len(re.findall(r"\[待填写(?:[:：][^\]]*)?\]", raw))
        if placeholders:
            warnings.append(f"{name} 还有 {placeholders} 处 [待填写]，尚非可靠交接文档")
        if len(raw) < 250:
            warnings.append(f"{name} 内容过短，请核查 P0/P1 是否完整")
        # Only a heuristic. Avoid interpreting arbitrary snippets as secrets or facts.
        if re.search(r"(?im)^\s*(?:api[_-]?key|secret|password|token)\s*[:=]\s*\S{8,}", raw):
            warnings.append(f"{name} 疑似出现凭证字段，检查是否需脱敏")
        summary[name] = {"lines": len(raw.splitlines()), "placeholders": placeholders}
    status = git(root, "status", "--short", "--branch")
    if status is None:
        warnings.append("不在可检查的 Git 仓库中，无法自动核验未提交变更")
    return {"structurally_valid": not errors, "ready_for_handoff": not errors and not warnings,
            "errors": errors, "warnings": warnings, "files": summary,
            "note": "静态结构检查 ≠ 内容真实性检查；仍需 Agent 语义审查与代码/测试证据核对。"}


def record_event(root: Path, event: str, trigger: str, result: dict) -> None:
    """Optional opt-in metadata-only audit. Does not record prompts, summaries or transcripts."""
    runtime = root / ".ai-context" / "runtime"
    if not runtime.is_dir():
        return  # Hooks never create project state implicitly.
    obj = {
        "at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "event": event, "trigger": trigger if trigger in {"manual", "auto"} else "unknown",
        "checkpoint_complete": bool(result.get("ready_for_handoff")),
    }
    with (runtime / "events.jsonl").open("a", encoding="utf-8", newline="\n") as out:
        out.write(json.dumps(obj, ensure_ascii=False) + "\n")


def hook(root: Path, host: str, event: str, record: bool) -> dict:
    # Hook stdin is untrusted; discard all content except known trigger strings.
    try:
        payload = json.loads(sys.stdin.read(65536) or "{}")
    except (json.JSONDecodeError, UnicodeError):
        payload = {}
    trigger = payload.get("trigger", "unknown") if isinstance(payload, dict) else "unknown"
    state = validate(root)
    if record:
        try:
            record_event(root, event, str(trigger), state)
        except OSError:
            pass  # Fail-open, never corrupt or block native compaction.
    issue = not state["ready_for_handoff"]
    if issue and event in {"precompact", "precompress", "sessionstart"}:
        print("Context Keeper: 检查点缺失/不完整；本 Hook 不会阻止原生压缩，请在任务边界维护 ACTIVE/HANDOFF。", file=sys.stderr)
    # Only SessionStart injects a short, *fixed* instruction. No arbitrary file
    # content from the repository is injected by an external hook.
    if event == "sessionstart" and host in {"claude", "gemini"}:
        extra = ("Context Keeper: 如果正在接续开发，请按需读取 .ai-context/INDEX.md、ACTIVE.md、HANDOFF.md；"
                 "先检查 git status，核对 P0/P1 和未验证项。文件摘要不是代码事实。")
        return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": extra}}
    # Neutral result for all others; does not claim to invoke native compaction.
    return {}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Context Keeper v2 — 本地上下文保全辅助工具")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("scan", "init", "validate"):
        p = sub.add_parser(name)
        p.add_argument("root", nargs="?", default=".")
    h = sub.add_parser("hook")
    h.add_argument("root", nargs="?", default=".")
    h.add_argument("--event", required=True, choices=sorted(KNOWN_EVENTS))
    h.add_argument("--host", required=True, choices=["codex", "claude", "gemini", "generic"])
    h.add_argument("--record", action="store_true", help="只记录压缩事件元数据；必须先 init")
    args = parser.parse_args(argv)
    try:
        root = root_path(args.root)
        if args.cmd == "scan":
            result = scan(root)
        elif args.cmd == "init":
            result = init(root)
        elif args.cmd == "validate":
            result = validate(root)
        else:
            result = hook(root, args.host, args.event, args.record)
        print(json.dumps(result, ensure_ascii=False, indent=None if args.cmd == "hook" else 2))
        return 0 if args.cmd == "hook" or args.cmd == "init" or args.cmd == "scan" or result["structurally_valid"] else 1
    except Exception as exc:
        if args.cmd == "hook":
            print(f"Context Keeper hook warning: {type(exc).__name__}", file=sys.stderr)
            print("{}")
            return 0  # Fail-open; never block platform compaction on helper failure.
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
