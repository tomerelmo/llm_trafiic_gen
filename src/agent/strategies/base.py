from __future__ import annotations

import abc
from dataclasses import dataclass

from langchain_openai import ChatOpenAI

from ..memory import SimpleMemory
from ..browser import BrowserSession
from ..logging.logger import ActionLogger


@dataclass
class AgentContext:
    base_url: str
    headless: bool
    model: str
    temperature: float
    action_logger: ActionLogger
    memory: SimpleMemory


class SiteStrategy(abc.ABC):
    """Base class for site-specific playbooks."""

    def __init__(self, browser: BrowserSession, context: AgentContext) -> None:
        self.browser = browser
        self.context = context
        self.llm = ChatOpenAI(model=context.model, temperature=context.temperature)

    @abc.abstractmethod
    def run(self) -> None:
        """Execute the end-to-end interaction for a specific target."""

    def remember(self, text: str) -> None:
        self.context.memory.save_context({"input": text}, {"output": text})
