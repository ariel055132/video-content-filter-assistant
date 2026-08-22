from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from rebuild_index import load_entries, parse_summary, render_index  # noqa: E402


class RebuildIndexTests(unittest.TestCase):
    fixtures = PROJECT_ROOT / "tests" / "fixtures" / "summaries"

    def test_reads_both_analysis_levels_and_collection(self) -> None:
        entries = load_entries(self.fixtures)
        videos = [entry for entry in entries if entry.document_type == "video-summary"]
        collections = [entry for entry in entries if entry.document_type != "video-summary"]

        self.assertEqual({entry.analysis_level for entry in videos}, {"quick-screen", "full-transcript"})
        self.assertEqual({entry.recommendation_score for entry in videos}, {5, 8})
        self.assertEqual({entry.quality_score for entry in videos}, {13, 20})
        self.assertEqual(len(collections), 1)
        self.assertFalse(any(entry.warnings for entry in entries))

    def test_rendered_index_contains_scores_and_links(self) -> None:
        entries = load_entries(self.fixtures)
        output = PROJECT_ROOT / "INDEX.md"
        rendered = render_index(entries, output)

        self.assertIn("quick-screen 1、full-transcript 1", rendered)
        self.assertIn("5/10", rendered)
        self.assertIn("20/25", rendered)
        self.assertIn("tests/fixtures/summaries/2026-08-16-demo-full", rendered)
        self.assertIn("集合與播放清單索引", rendered)

    def test_template_declares_required_dual_scores(self) -> None:
        template = (PROJECT_ROOT / "templates" / "video-summary.md").read_text(encoding="utf-8")
        self.assertIn("analysis_level: quick-screen", template)
        self.assertRegex(template, r"recommendation_score:\s+\d+")
        self.assertRegex(template, r"quality_score:\s+\d+")
        self.assertIn("## 分析依據、可信度與限制", template)

    def test_legacy_summary_is_read_only_compatible(self) -> None:
        legacy_paths = sorted((PROJECT_ROOT / "summaries").glob("*.md"))
        self.assertTrue(legacy_paths)
        entry = parse_summary(legacy_paths[0])
        self.assertEqual(entry.document_type, "video-summary")
        self.assertTrue(entry.title)
        self.assertIsNotNone(entry.quality_score)


if __name__ == "__main__":
    unittest.main()
