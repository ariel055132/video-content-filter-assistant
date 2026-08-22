#!/usr/bin/env python3
"""Rebuild INDEX.md from new-schema and legacy Markdown summaries."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_LEVELS = {"quick-screen", "full-transcript"}
ALLOWED_RECOMMENDATIONS = {
    "skip",
    "summary-only",
    "selected-sections",
    "full-watch",
    "deep-study",
}
REQUIRED_NEW_FIELDS = {
    "schema_version",
    "document_type",
    "analysis_level",
    "title",
    "url",
    "analyzed_at",
    "recommendation",
    "recommendation_score",
    "quality_score",
}


@dataclass
class SummaryEntry:
    path: Path
    title: str
    analyzed_at: str
    document_type: str
    analysis_level: str
    recommendation: str
    recommendation_score: int | None
    quality_score: int | None
    creator: str
    source_url: str
    is_new_schema: bool
    warnings: list[str] = field(default_factory=list)


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("'", '"', "[")):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value.strip("'\"")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", text, re.DOTALL)
    if not match:
        return {}, text

    metadata: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line[:1].isspace():
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = _scalar(value)
    return metadata, text[match.end() :]


def _first_heading(body: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _filename_date(path: Path) -> str:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    return match.group(1) if match else "unknown"


def _infer_document_type(path: Path, metadata: dict[str, Any]) -> str:
    explicit = str(metadata.get("document_type", "")).strip()
    if explicit:
        return explicit
    stem = path.stem.lower()
    if re.search(r"(?:^|-)playlist(?:-|$)|(?:^|-)index(?:-|$)", stem):
        return "collection-index"
    return "video-summary"


def _infer_analysis_level(metadata: dict[str, Any], body: str) -> str:
    explicit = str(metadata.get("analysis_level", "")).strip()
    if explicit:
        return explicit
    if "快速初篩" in body:
        return "quick-screen"
    full_markers = (
        r"完整(?:日文|英文|中文)?(?:自動)?字幕",
        r"完整音(?:訊|軌)",
        r"完整逐字稿",
        r"完整轉錄",
        r"轉錄至(?:節目|影片)?結尾",
    )
    if any(re.search(pattern, body) for pattern in full_markers):
        return "full-transcript"
    return "legacy-unspecified"


def _infer_recommendation(metadata: dict[str, Any], body: str) -> str:
    explicit = str(metadata.get("recommendation", "")).strip()
    if explicit:
        return explicit
    patterns = (
        (r"Deeply study|深入研讀|深度學習", "deep-study"),
        (r"Watch full video|完整觀看|完整收聽", "full-watch"),
        (r"Watch selected sections|選段觀看|選段收聽", "selected-sections"),
        (r"Read AI summary only|只讀(?: AI)?摘要", "summary-only"),
        (r"\bSkip\b|建議略過|跳過整支", "skip"),
    )
    for pattern, value in patterns:
        if re.search(pattern, body, re.IGNORECASE):
            return value
    return "unspecified"


def _number(metadata: dict[str, Any], key: str) -> int | None:
    value = metadata.get(key)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _infer_recommendation_score(metadata: dict[str, Any], body: str) -> int | None:
    explicit = _number(metadata, "recommendation_score")
    if explicit is not None:
        return explicit
    patterns = (
        r"推薦(?:程度|分數|評分)[^\n\d]{0,20}(\d{1,2})\s*[/／]\s*10",
        r"Recommendation (?:Level|Score)[^\n\d]{0,20}(\d{1,2})\s*[/／]\s*10",
    )
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _infer_quality_score(metadata: dict[str, Any], body: str) -> int | None:
    explicit = _number(metadata, "quality_score")
    if explicit is not None:
        return explicit
    matches = re.findall(r"(?<!\d)(\d{1,2})\s*[/／]\s*25(?!\d)", body)
    return int(matches[-1]) if matches else None


def _bullet_value(body: str, labels: Iterable[str]) -> str:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(
        rf"^-\s*(?:\*\*)?(?:{label_pattern})(?:\*\*)?[：:]\s*(.+?)\s*$",
        body,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def _source_url(metadata: dict[str, Any], body: str) -> str:
    explicit = str(metadata.get("url", "")).strip()
    if explicit:
        return explicit
    line = _bullet_value(body, ("原始連結", "影片連結", "URL"))
    markdown_url = re.search(r"\((https?://[^)]+)\)", line)
    if markdown_url:
        return markdown_url.group(1)
    plain_url = re.search(r"https?://[^\s>]+", line)
    return plain_url.group(0).rstrip(".,)") if plain_url else ""


def _validate_new(metadata: dict[str, Any], entry: SummaryEntry) -> None:
    missing = sorted(key for key in REQUIRED_NEW_FIELDS if metadata.get(key, "") == "")
    if missing:
        entry.warnings.append("缺少欄位：" + ", ".join(missing))
    if entry.analysis_level not in ALLOWED_LEVELS:
        entry.warnings.append(f"未知 analysis_level：{entry.analysis_level}")
    if entry.recommendation not in ALLOWED_RECOMMENDATIONS:
        entry.warnings.append(f"未知 recommendation：{entry.recommendation}")
    if entry.recommendation_score is None or not 1 <= entry.recommendation_score <= 10:
        entry.warnings.append("recommendation_score 必須介於 1～10")
    if entry.quality_score is None or not 5 <= entry.quality_score <= 25:
        entry.warnings.append("quality_score 必須介於 5～25")


def parse_summary(path: Path) -> SummaryEntry:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(text)
    is_new = bool(metadata)
    entry = SummaryEntry(
        path=path,
        title=str(metadata.get("title", "")).strip() or _first_heading(body, path.stem),
        analyzed_at=str(metadata.get("analyzed_at", "")).strip() or _filename_date(path),
        document_type=_infer_document_type(path, metadata),
        analysis_level=_infer_analysis_level(metadata, body),
        recommendation=_infer_recommendation(metadata, body),
        recommendation_score=_infer_recommendation_score(metadata, body),
        quality_score=_infer_quality_score(metadata, body),
        creator=str(metadata.get("creator", "")).strip()
        or _bullet_value(body, ("作者", "頻道", "創作者", "節目")),
        source_url=_source_url(metadata, body),
        is_new_schema=is_new,
    )
    if is_new and entry.document_type == "video-summary":
        _validate_new(metadata, entry)
    return entry


def load_entries(summaries_dir: Path) -> list[SummaryEntry]:
    if not summaries_dir.is_dir():
        raise FileNotFoundError(f"找不到摘要目錄：{summaries_dir}")
    entries = [parse_summary(path) for path in summaries_dir.glob("*.md")]
    return sorted(entries, key=lambda item: (item.analyzed_at, item.path.name), reverse=True)


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _score(value: int | None, denominator: int) -> str:
    return f"{value}/{denominator}" if value is not None else "—"


def _report_link(entry: SummaryEntry, output_path: Path) -> str:
    try:
        relative = entry.path.resolve().relative_to(output_path.parent.resolve())
    except ValueError:
        relative = Path("summaries") / entry.path.name
    return f"[{_escape(entry.title)}]({relative.as_posix()})"


def _source_link(entry: SummaryEntry) -> str:
    return f"[原片]({entry.source_url})" if entry.source_url else "—"


def _level_label(level: str) -> str:
    return {
        "quick-screen": "quick-screen",
        "full-transcript": "full-transcript",
        "legacy-unspecified": "舊格式／未標示",
    }.get(level, level)


def _recommendation_label(value: str) -> str:
    return {
        "skip": "Skip",
        "summary-only": "Read summary",
        "selected-sections": "Selected sections",
        "full-watch": "Full watch",
        "deep-study": "Deep study",
        "unspecified": "—",
    }.get(value, value)


def render_index(entries: list[SummaryEntry], output_path: Path) -> str:
    videos = [entry for entry in entries if entry.document_type == "video-summary"]
    collections = [entry for entry in entries if entry.document_type != "video-summary"]
    quick_count = sum(entry.analysis_level == "quick-screen" for entry in videos)
    full_count = sum(entry.analysis_level == "full-transcript" for entry in videos)
    legacy_count = sum(entry.analysis_level == "legacy-unspecified" for entry in videos)
    warning_entries = [entry for entry in entries if entry.warnings]
    latest_analysis = max((entry.analyzed_at for entry in entries), default="—")

    lines = [
        "# 影片摘要索引",
        "",
        "> 本檔由 `python3 tools/rebuild_index.py` 自動產生；請勿手動編輯。",
        "",
        f"- 最新分析日：{latest_analysis}",
        f"- 獨立影片報告：{len(videos)}",
        f"- 集合／播放清單索引：{len(collections)}",
        f"- 分析層級：quick-screen {quick_count}、full-transcript {full_count}、舊格式／未標示 {legacy_count}",
        "",
        "## 獨立影片報告",
        "",
        "| 分析日 | 報告 | 層級 | 建議 | 推薦分 | 品質分 | 作者／頻道 | 來源 |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for entry in videos:
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape(entry.analyzed_at),
                    _report_link(entry, output_path),
                    _escape(_level_label(entry.analysis_level)),
                    _escape(_recommendation_label(entry.recommendation)),
                    _score(entry.recommendation_score, 10),
                    _score(entry.quality_score, 25),
                    _escape(entry.creator) or "—",
                    _source_link(entry),
                )
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## 集合與播放清單索引",
            "",
            "| 分析日 | 文件 | 類型 |",
            "|---|---|---|",
        )
    )
    if collections:
        for entry in collections:
            lines.append(
                f"| {_escape(entry.analyzed_at)} | {_report_link(entry, output_path)} | {_escape(entry.document_type)} |"
            )
    else:
        lines.append("| — | 尚無 | — |")

    lines.extend(("", "## 格式檢查", ""))
    if warning_entries:
        lines.append("下列新版報告需要修正：")
        lines.append("")
        for entry in warning_entries:
            lines.append(f"- `{entry.path.name}`：{'；'.join(entry.warnings)}")
    else:
        lines.append("新版報告的必要 metadata 與分數範圍檢查均通過。")
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="從 summaries/*.md 重建 INDEX.md")
    parser.add_argument(
        "--summaries-dir",
        type=Path,
        default=PROJECT_ROOT / "summaries",
        help="摘要目錄（預設：專案 summaries/）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "INDEX.md",
        help="索引輸出路徑（預設：專案 INDEX.md）",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只檢查現有索引是否為最新，不寫檔",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        entries = load_entries(args.summaries_dir)
    except (OSError, UnicodeError) as error:
        print(f"錯誤：{error}", file=sys.stderr)
        return 2
    rendered = render_index(entries, args.output)

    if args.check:
        if not args.output.exists():
            print(f"索引不存在：{args.output}", file=sys.stderr)
            return 1
        current = args.output.read_text(encoding="utf-8")
        if current != rendered:
            print("INDEX.md 不是最新版本；請執行 python3 tools/rebuild_index.py", file=sys.stderr)
            return 1
        print(f"索引已是最新版本（{len(entries)} 份文件）。")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    warning_count = sum(bool(entry.warnings) for entry in entries)
    print(f"已重建 {args.output}：{len(entries)} 份文件，{warning_count} 份新版文件有格式警告。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
