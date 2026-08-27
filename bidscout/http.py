"""Minimal stdlib HTTP with retries, plus the SAM.gov daily request ledger.

The ledger is the guardrail that keeps unattended runs inside the measured
SAM.gov key budget: when the day's budget is spent, calls raise BudgetExhausted
instead of silently burning tomorrow's capacity or hammering a 429.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

from . import config


class BudgetExhausted(RuntimeError):
    """Raised when today's SAM.gov request budget is spent."""


class HttpError(RuntimeError):
    def __init__(self, status: int, url: str, body: str):
        super().__init__(f"HTTP {status} for {url}: {body[:200]}")
        self.status = status


def _ledger_path():
    return config.ensure_state_dir() / "sam_request_ledger.json"


def _load_ledger() -> dict:
    path = _ledger_path()
    if path.exists():
        return config.load_json(path)
    return {"date": "", "count": 0}


def sam_budget_remaining() -> int:
    ledger = _load_ledger()
    if ledger["date"] != date.today().isoformat():
        return config.SAM_DAILY_BUDGET
    return max(0, config.SAM_DAILY_BUDGET - ledger["count"])


def _spend_sam_budget(n: int = 1) -> None:
    ledger = _load_ledger()
    today = date.today().isoformat()
    if ledger["date"] != today:
        ledger = {"date": today, "count": 0}
    ledger["count"] += n
    config.save_json(_ledger_path(), ledger)


def request_json(url: str, params: dict | None = None, payload: dict | None = None,
                 retries: int = 3, timeout: int = 60, sam_metered: bool = False):
    """GET (params) or POST (payload) a JSON endpoint with backoff.

    sam_metered=True enforces and records the SAM.gov daily budget.
    """
    if sam_metered:
        if sam_budget_remaining() <= 0:
            raise BudgetExhausted(
                f"SAM.gov daily budget ({config.SAM_DAILY_BUDGET}) spent; "
                "retry after 00:00 UTC or raise SAM_DAILY_BUDGET if your key allows.")
        _spend_sam_budget()

    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    data = None
    headers = {"User-Agent": config.USER_AGENT, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                last_err = HttpError(e.code, url, body)
                continue
            raise HttpError(e.code, url, body) from e
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1))
                last_err = e
                continue
            raise
    raise last_err  # pragma: no cover
