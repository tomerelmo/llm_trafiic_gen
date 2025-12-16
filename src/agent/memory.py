from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SimpleMemory:
    """Lightweight conversation buffer compatible with the strategy API."""

    messages: List[Dict[str, Any]] = field(default_factory=list)

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        self.messages.append({"inputs": inputs, "outputs": outputs})
