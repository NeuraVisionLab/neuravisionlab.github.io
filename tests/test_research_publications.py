import csv
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import build


class PublicationMarkup(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.rows = []
        self.filters = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "pub-row" in attrs.get("class", "").split():
            self.rows.append(attrs)
        if tag == "button" and "data-filter" in attrs:
            self.filters.append(attrs)


class ResearchPublicationsTests(unittest.TestCase):
    def setUp(self):
        self.areas = [
            {"slug": "topology-page", "publication_tag": "topology"},
            {"slug": "uncertainty-page", "publication_tag": "uncertainty"},
            {"slug": "unconfigured-page", "publication_tag": ""},
        ]

    def attach(self, papers):
        build.attach_research_publications(self.areas, papers)

    def test_tagged_papers_appear_in_order_and_can_belong_to_multiple_topics(self):
        papers = [
            {"title": "New paper", "tags": "topology"},
            {"title": "Shared paper", "tags": "topology; uncertainty"},
            {"title": "Unrelated", "tags": "3d"},
        ]
        self.attach(papers)
        self.assertEqual(self.areas[0]["publications"], papers[:2])
        self.assertEqual(self.areas[1]["publications"], [papers[1]])
        self.assertEqual(self.areas[2]["publications"], [])

    def test_case_spacing_and_repeated_tags_do_not_change_membership(self):
        self.areas[0]["publication_tag"] = " Topology "
        paper = {"title": "Renamed freely", "tags": "  TOPOLOGY ; topology ; ; Uncertainty  "}
        self.attach([paper])
        self.assertEqual(self.areas[0]["publications"], [paper])
        self.assertEqual(self.areas[1]["publications"], [paper])

    def test_exact_tags_only_and_untagged_papers_are_excluded(self):
        self.attach([
            {"title": "Blank", "tags": ""},
            {"title": "Older row without tags"},
            {"title": "Longer tag", "tags": "topology-aware"},
            {"title": "Unrelated", "tags": "biology"},
        ])
        self.assertTrue(all(a["publications"] == [] for a in self.areas))

    def test_removing_a_tag_removes_the_paper_on_next_build(self):
        paper = {"title": "Paper", "tags": "topology; uncertainty"}
        self.attach([paper])
        paper["tags"] = "uncertainty"
        self.attach([paper])
        self.assertEqual(self.areas[0]["publications"], [])
        self.assertEqual(self.areas[1]["publications"], [paper])

    def test_new_csv_paper_appears_without_a_separate_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            data = temp / "data"
            shutil.copytree(build.DATA, data)
            legacy = data / "research_publications.csv"
            if legacy.exists():
                legacy.unlink()
            path = data / "publications.csv"
            with path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                fields, rows = reader.fieldnames, list(reader)
            if "tags" not in fields:
                fields.append("tags")
            new = dict.fromkeys(fields, "")
            new.update(title="Brand-new tagged paper", order="1", year="2030", tags=" TOPOLOGY ; uncertainty; 3d; Motion; topology ")
            rows.append(new)
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            out = temp / "site"
            out.mkdir()
            with patch.object(build, "DATA", data):
                build.build(out)
            # The browser receives normalized tokens, so the same multi-tag
            # paper is discoverable through every relevant topic filter.
            markup = PublicationMarkup((out / "publications.html").read_text())
            self.assertEqual(markup.rows[0].get("data-tags", "").split(),
                             ["3d", "motion", "topology", "uncertainty"])
            self.assertEqual([f.get("data-value") for f in markup.filters
                              if f["data-filter"] == "tags"],
                             ["topology", "uncertainty", "3d", "motion"])
            self.assertFalse(any(f["data-filter"] == "year" for f in markup.filters))
            topology = (out / "topology-aware-computer-vision.html").read_text()
            bibliography = topology.split('id="related-publications"', 1)[1].split('</section>', 1)[0]
            self.assertIn("Brand-new tagged paper", bibliography)
            self.assertLess(bibliography.index("Brand-new tagged paper"), bibliography.index("CAPE:"))
            self.assertNotIn('id="more-h"', topology)
            for slug in ["uncertainty-trustworthy-ai", "3d-shape-implicit", "trajectory-motion-forecasting"]:
                page = (out / f"{slug}.html").read_text()
                self.assertNotIn('id="more-h"', page)
                bibliography = page.split('id="related-publications"', 1)[1].split('</section>', 1)[0]
                self.assertIn("Brand-new tagged paper", bibliography)
                self.assertEqual(bibliography.count("Brand-new tagged paper"), 1)
                self.assertNotIn("CAPE:", bibliography)

            # Removing a topic tag must change the rendered bibliography on rebuild.
            new["tags"] = "topology; 3d"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with patch.object(build, "DATA", data):
                build.build(out)
            self.assertNotIn("Brand-new tagged paper", (out / "uncertainty-trustworthy-ai.html").read_text())
            self.assertNotIn("Brand-new tagged paper", (out / "trajectory-motion-forecasting.html").read_text())
            self.assertIn("Brand-new tagged paper", (out / "3d-shape-implicit.html").read_text())


if __name__ == "__main__":
    unittest.main()
