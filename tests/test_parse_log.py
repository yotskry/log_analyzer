import gzip
from tempfile import NamedTemporaryFile

import pytest

from log_analyzer.log_analyzer import parse_log


@pytest.mark.parametrize("use_gzip", [False, True])
def test_parse_log(use_gzip):
    """Check that parse_log() calculates URL stats correctly"""

    log_data = """\
1.1.1.1 - - [01/Jan/2020:01:01:01 +0300] "GET /api/call1 HTTP/1.1" 200 123 "-" "-" "-" "-" "-" 0.147
1.1.1.1 - - [01/Jan/2020:01:01:02 +0300] "GET /api/call1 HTTP/1.1" 200 123 "-" "-" "-" "-" "-" 0.853
1.1.1.1 - - [01/Jan/2020:01:01:03 +0300] "POST /api/call2 HTTP/1.1" 500 456 "-" "-" "-" "-" "-" 1.238
"""

    expected_stats = [
        {
            "url": "/api/call2",
            "count": 1,
            "count_perc": 33.333,
            "time_sum": 1.238,
            "time_perc": 55.317,
            "time_avg": 1.238,
            "time_max": 1.238,
            "time_med": 1.238,
        },
        {
            "url": "/api/call1",
            "count": 2,
            "count_perc": 66.667,
            "time_sum": 1.0,
            "time_perc": 44.683,
            "time_avg": 0.5,
            "time_max": 0.853,
            "time_med": 0.5,
        },
    ]

    mode = "wb" if use_gzip else "w"
    with NamedTemporaryFile(mode=mode, delete=False, suffix=".gz" if use_gzip else ".log") as temp_log:
        if use_gzip:
            with gzip.GzipFile(fileobj=temp_log, mode="wb") as gz:
                gz.write(log_data.encode("utf-8"))
        else:
            temp_log.write(log_data)

        temp_log_path = temp_log.name

    class LogFile:
        path = temp_log_path
        extension = ".gz" if use_gzip else ".log"

    parsed_logs = list(parse_log(LogFile(), url_limit=2))
    for entry in parsed_logs:
        for key in ["time_sum", "time_avg", "time_max", "time_med", "count_perc", "time_perc"]:
            entry[key] = round(entry[key], 3)
    assert parsed_logs == expected_stats, f"Error, received: {parsed_logs}"
