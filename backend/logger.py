import logging
import json
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from backend.config import LOG_FILE_PATH, LOG_MAX_BYTES, LOG_BACKUP_COUNT

os.makedirs("logs", exist_ok=True)

_handler = RotatingFileHandler(
    LOG_FILE_PATH,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT,
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
    retry_count: int = None,
    fallback_used: bool = None,
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
        "retry_count": retry_count,
        "fallback_used": fallback_used,
    }
    _logger.info(json.dumps(record))
