from __future__ import annotations

import os
import random
from pathlib import Path

import typer

from .browser import BrowserSession
from .logging.logger import ActionLogger
from .memory import SimpleMemory
from .strategies.base import AgentContext
from .strategies.juice_shop import JuiceShopProfile, JuiceShopStrategy

app = typer.Typer(add_completion=False)


@app.command()
def run(
    base_url: str = typer.Option("http://localhost:3000", help="Juice Shop base URL"),
    headless: bool = typer.Option(True, help="Run browser in headless mode"),
    model: str = typer.Option("gpt-4o-mini", help="OpenAI model name"),
    temperature: float = typer.Option(0.3, help="LLM temperature"),
    log_file: Path = typer.Option(Path("data/actions.log"), help="Action log location"),
) -> None:
    """Run the Juice Shop agent end-to-end."""

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY before launching the agent.")

    memory = SimpleMemory()
    with ActionLogger(log_file) as logger:
        browser = BrowserSession(headless=headless, action_logger=logger)
        context = AgentContext(
            base_url=base_url,
            headless=headless,
            model=model,
            temperature=temperature,
            action_logger=logger,
            memory=memory,
        )
        profile = JuiceShopProfile(
            email=f"agent_{random.randint(1000, 9999)}@example.com",
            password="P@ssw0rd!",
            security_answer="Automata",
        )
        strategy = JuiceShopStrategy(browser=browser, context=context, profile=profile)
        strategy.run()
        logger.flush()


@app.command()
def smoke(
    base_url: str = typer.Option(..., help="Target URL to open for a quick smoke test"),
    headless: bool = typer.Option(True, help="Run browser in headless mode"),
    steps: int = typer.Option(2, help="Number of links to follow after landing"),
    log_file: Path = typer.Option(Path("data/actions.log"), help="Action log location"),
    snapshot: bool = typer.Option(True, help="Capture an HTML snapshot after each navigation"),
) -> None:
    """Perform a lightweight visit to any URL to verify automation works."""

    with ActionLogger(log_file) as logger:
        browser = BrowserSession(headless=headless, action_logger=logger)
        with browser.session():
            browser.goto(base_url)
            if snapshot:
                browser.snapshot_dom("smoke_landing")

            page = browser.page
            hrefs = page.eval_on_selector_all("a[href]", "els => els.map(el => el.href).filter(Boolean)")
            for idx, href in enumerate(hrefs[:steps]):
                logger.record("follow_link", page.url, target=href)
                page.goto(href, wait_until="networkidle")
                page.wait_for_timeout(int(500))
                if snapshot:
                    browser.snapshot_dom(f"smoke_step_{idx+1}")


if __name__ == "__main__":
    app()
