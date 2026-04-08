import logging
import json
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)

_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)

_logger = logging.getLogger("psyche_mend")
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)
_logger.propagate = False


def log_event(
    request_id: str,
    stage: str,
    status: str,
    duration_ms: float = None,
    emotion: str = None,
    model: str = None,
    error_type: str = None,
    input_type: str = None,
) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "request_id": request_id,
        "stage": stage,
        "status": status,
        "duration_ms": round(duration_ms, 1) if duration_ms is not None else None,
        "emotion": emotion,
        "model": model,
        "error_type": error_type,
        "input_type": input_type,
    }
    _logger.info(json.dumps(record))
