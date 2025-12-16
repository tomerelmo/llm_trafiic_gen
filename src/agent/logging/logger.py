from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ActionRecord:
    """Represents a single user-like action executed by the agent."""

    action: str
    url: str
    metadata: Dict[str, Any]
    timestamp: str


class ActionLogger:
    """Structured logger that emits JSON lines for each performed action."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._buffer: List[ActionRecord] = []
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        self.logger = logging.getLogger("agent.actions")

    def record(self, action: str, url: str, **metadata: Any) -> None:
        record = ActionRecord(
            action=action,
            url=url,
            metadata=metadata,
            timestamp=datetime.utcnow().isoformat(),
        )
        self._buffer.append(record)
        self.logger.info("%s | %s | %s", action, url, json.dumps(metadata))

    def flush(self) -> None:
        if not self._buffer:
            return
        with self.log_path.open("a", encoding="utf-8") as fp:
            for record in self._buffer:
                fp.write(json.dumps(asdict(record)) + "\n")
        self._buffer.clear()

    def __enter__(self) -> "ActionLogger":
        return self

    def __exit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Any) -> None:  # type: ignore[override]
        self.flush()


__all__ = ["ActionLogger", "ActionRecord"]
