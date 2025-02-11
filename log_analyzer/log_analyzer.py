import argparse
import gzip
import json
import os
import re
import statistics
import sys
from collections import defaultdict, namedtuple
from datetime import datetime
from string import Template
from typing import Dict, Generator, Union

from logger.logger import create_logger

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log", "APP_LOGS": "./app_logs"}

LogFile = namedtuple("LogFile", ["path", "date", "extension"])
LOG_PATTERN = re.compile(r'"[A-Z]+ (?P<url>\S+) HTTP/[\d.]+" \d+ \d+ .* (?P<request_time>[\d.]+)$')


def find_latest_log(log_dir: str) -> LogFile | None:
    log_pattern = re.compile(r"nginx-access-ui\.log-(\d{8})(\.gz)?$")
    latest_log = None
    for filename in os.listdir(log_dir):
        match = log_pattern.match(filename)
        if not match:
            continue
        date_str, extension = match.groups()
        log_date = datetime.strptime(date_str, "%Y%m%d")
        full_path = os.path.join(log_dir, filename)
        extension = extension or ""

        if latest_log is None or log_date >= latest_log.date:
            latest_log = LogFile(full_path, log_date, extension)
    return latest_log


def parse_log(log_file, url_limit) -> Generator[Dict[str, Union[int, float, str]], None, None]:
    opener = gzip.open if log_file.extension == ".gz" else open
    url_stats = defaultdict(list)
    total_requests = 0
    total_request_time = float(0)

    with opener(log_file.path, "rt", encoding="utf-8") as f:
        for line in f:
            match = LOG_PATTERN.search(line)
            if match:
                url = match.group("url")
                request_time = float(match.group("request_time"))
                url_stats[url].append(request_time)
                total_requests += 1
                total_request_time += request_time

    parsed_data = []
    for url, times in url_stats.items():
        count = len(times)
        time_sum = sum(times)
        time_max = max(times)
        time_avg = time_sum / count
        time_med = statistics.median(times)
        count_perc = (count / total_requests) * 100
        time_perc = (time_sum / total_request_time) * 100

        parsed_data.append(
            {
                "url": url,
                "count": count,
                "count_perc": round(count_perc, 3),
                "time_sum": round(time_sum, 3),
                "time_perc": round(time_perc, 3),
                "time_avg": round(time_avg, 3),
                "time_max": round(time_max, 3),
                "time_med": round(time_med, 3),
            }
        )

    parsed_data.sort(key=lambda x: x["time_sum"], reverse=True)
    for entry in parsed_data[:url_limit]:
        yield entry


def generate_report(
    logs_stats: Generator[Dict[str, Union[int, float, str]], None, None], report_dir: str, logfile_date: datetime
):
    template_file = "log_analyzer/report.html"
    report_file_name = f"report-{logfile_date.year}.{logfile_date.month}.{logfile_date.day}.html"
    with open(template_file, "r", encoding="utf-8") as f:
        template = f.read()
    urls_stats = []
    for entry in logs_stats:
        urls_stats.append(json.dumps(entry, indent=2))
    urls_stats_json = "[\n  " + ",\n  ".join(urls_stats) + "\n]"

    report = Template(template)
    report_content = report.safe_substitute(table_json=urls_stats_json)

    os.makedirs(report_dir, exist_ok=True)
    with open(f"{report_dir}/{report_file_name}", "w", encoding="utf-8") as f:
        f.write(report_content)


def exit_on_error():
    print("Error detected, see logs for details")
    sys.exit(1)


def build_config():
    current_config = config.copy()
    config_file = args.config
    with open(config_file) as f:
        custom_config = json.load(f)
        current_config.update(custom_config)
    return current_config


def main():
    # Find latest nginx logfile
    try:
        latest_log = find_latest_log(current_config["LOG_DIR"])
    except FileNotFoundError:
        logger.info("Log file path is wrong")
        sys.exit(0)
    if latest_log is None:
        logger.error("Log file is not found")
        exit_on_error()
    logger.info(f"Latest log: {latest_log.path}")

    # Parse nginx log and generate report
    url_stats = parse_log(latest_log, current_config["REPORT_SIZE"])
    logger.info("Generating report...")
    generate_report(url_stats, current_config["REPORT_DIR"], latest_log.date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Log Analyzer", epilog="Generates a report showing the most suspicious web server logs"
    )
    group = parser.add_argument_group("Available options")
    parser.add_argument("--config", default="config/custom_config.json", help="Configuration file name")
    args = parser.parse_args()

    current_config = build_config()

    logger = create_logger(__name__, current_config.get("APP_LOGS", None))

    try:
        main()
    except (KeyboardInterrupt, Exception):
        logger.error("Unspecified error", exc_info=True)
        exit_on_error()
    logger.info("Report is generated successfully")
