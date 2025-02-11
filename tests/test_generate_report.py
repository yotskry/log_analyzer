import json
import re
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from log_analyzer.log_analyzer import generate_report


def test_generate_report_creates_file(sample_log_entries):
    """Test checks that report is created"""
    with TemporaryDirectory() as tmpdir:
        report_dir = Path(tmpdir)
        logfile_date = datetime(2025, 2, 1)

        generate_report(sample_log_entries, str(report_dir), logfile_date)

        expected_file = report_dir / "report-2025.2.1.html"
        assert expected_file.exists(), "Report was not created"


def test_generate_report_inserts_correct_json(sample_log_entries):
    """Test checks that report data is inserted to html template"""
    with TemporaryDirectory() as tmpdir:
        report_dir = Path(tmpdir)
        logfile_date = datetime(2025, 2, 1)
        log_entries_list = list(sample_log_entries)

        generate_report(iter(log_entries_list), str(report_dir), logfile_date)

        report_file = report_dir / "report-2025.2.1.html"
        with report_file.open("r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"var table = (\[.*?\]);", content, re.DOTALL)
        # Deserialize JSON
        report_json = json.loads(match.group(1))
        expected_json = log_entries_list

        assert report_json == expected_json, "Bad JSON data"
