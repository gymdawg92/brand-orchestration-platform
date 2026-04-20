import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log: dict = {
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
        }
        for key in ("brand_id", "task_type", "trace_id", "status_code", "duration_ms"):
            if hasattr(record, key):
                log[key] = getattr(record, key)
        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)
        return json.dumps(log)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
