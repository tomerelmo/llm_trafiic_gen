# Autonomous Web Agent Prototype

This repository contains a minimal, modular agent that uses **LangChain** for orchestration and **Playwright** for realistic browser automation. The first target is the OWASP Juice Shop, but the code is structured so that site-specific strategies can be added with minimal changes.

## Architecture Overview

- `src/agent/browser.py` – Thin wrapper around Playwright that exposes navigation, form filling, DOM snapshots, and storage export while emitting structured action logs.
- `src/agent/logging/logger.py` – Structured JSONL action logger used across the stack.
- `src/agent/strategies/` – Site-specific playbooks. `juice_shop.py` includes a scripted registration/login/cart/checkout/order-history flow.
- `src/agent/strategies/base.py` – Defines the `AgentContext` and base class that wires LangChain memory and LLM access for reasoning-based behaviors.
- `src/agent/utils/human.py` – Helpers for human-like timing and simple weighted choices.
- `src/agent/main.py` – Typer CLI entry that sets up the context, logging, profile, and launches the Juice Shop strategy.
- `entrypoint.sh` – Docker entrypoint that validates the LLM API key and starts the agent.
- `Dockerfile` – Builds a runnable container with Playwright + Chromium installed.

## Quick Start (local)

1) Install dependencies **and** Playwright's Chromium binary (only needed once):

   ```bash
   pip install -r requirements.txt
   python -m playwright install --with-deps chromium
   ```

2) Export your LLM key (OpenAI-compatible, only used at runtime):

   ```bash
   export OPENAI_API_KEY="<your key>"
   ```

3) Smoke-test that automation works against any URL:

   ```bash
   PYTHONPATH=src python -m agent.main smoke --base-url https://example.com --steps 2 --headless True
   ```

   *Look for*: `data/actions.log` (JSONL action trace) and `data/snapshots/` (HTML dumps). Seeing new entries means the browser is
   launching and navigating successfully.

4) Run the full Juice Shop scenario (registration → login → shop → checkout → order history):

   ```bash
   PYTHONPATH=src python -m agent.main run --base-url http://localhost:3000 --headless True
   ```

   To visually observe actions, pass `--headless False`.

## Docker Usage

Build and run the container:

```bash
docker build -t web-agent .
docker run --rm -e OPENAI_API_KEY="<your key>" -p 3000:3000 web-agent --base-url http://host.docker.internal:3000 --headless True
```

> **Note:** Do not bake secrets into the image—pass them via environment variables at runtime.

### Docker smoke test

To simply confirm the containerized automation stack is working (without hitting Juice Shop), override the entrypoint command:

```bash
docker run --rm -e OPENAI_API_KEY="<your key>" web-agent smoke --base-url https://example.com --steps 2 --headless True
```

Action logs and snapshots are written inside the container at `/app/data`. Bind-mount `./data:/app/data` if you want to inspect
them on the host:

```bash
docker run --rm -e OPENAI_API_KEY="<your key>" -v "$(pwd)/data:/app/data" web-agent smoke --base-url https://example.com --steps 2
```

## Extending to Other Sites

1. Create a new strategy in `src/agent/strategies/<site>.py` that subclasses `SiteStrategy` and implements `run()`.
2. Use `BrowserSession` helpers to snapshot DOM, discover forms, and take structured actions; log everything via `ActionLogger`.
3. Wire the new strategy into `agent.main` (or a new CLI command) with minimal boilerplate.

The LangChain `ChatOpenAI` client and a lightweight conversation buffer are already available in the base strategy so you can prompt the LLM to reason over parsed HTML or extracted metadata to choose safe, human-like next actions.
