import logging
import os
import sys
from collections import OrderedDict

import structlog


def ordered_json_renderer(_, __, event_dict):
    ordered_data = OrderedDict(
        [
            ("timestamp", event_dict.get("timestamp")),
            ("level", event_dict.get("level")),
            ("module", event_dict.get("logger")),
            ("event", event_dict.get("event")),
        ]
    )
    if event_dict.get("exception", None):
        ordered_data["trace"] = event_dict.get("exception")
    return structlog.processors.JSONRenderer()(None, None, ordered_data)


def create_logger(name, app_log_dir=None):
    if app_log_dir:
        log_filename = "app.log"
        os.makedirs(app_log_dir, exist_ok=True)
        handler = logging.FileHandler(f"{app_log_dir}/{log_filename}")
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            ordered_json_renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    return structlog.get_logger(name)
