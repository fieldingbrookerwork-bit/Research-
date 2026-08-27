"""Configuration: environment, niche definitions, paths, rate budgets."""

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = Path(os.environ.get("BIDSCOUT_STATE", REPO_ROOT / "state"))
FIXTURES_DIR = REPO_ROOT / "fixtures"

SAM_API_KEY = os.environ.get("SAM_API_KEY", "")
SAM_BASE = "https://api.sam.gov/prod/opportunities/v2/search"
SAM_ENTITY_BASE = "https://api.sam.gov/entity-information/v3/entities"
USASPENDING_BASE = "https://api.usaspending.gov/api/v2"

# SAM.gov personal (roleless) keys are reported at ~10 requests/day; role-based
# keys at ~1,000/day. Measure yours on day 1 (see RUNBOOK) and set the env var.
SAM_DAILY_BUDGET = int(os.environ.get("SAM_DAILY_BUDGET", "10"))

USER_AGENT = "bidscout/0.1 (solo founder research tool; contact via SAM entity POC)"

# Candidate niches for the scorer. The council's guidance: pick federal-heavy
# NAICS where USAspending award history is dense; avoid trades that bid mostly
# state/local. 561612 is included deliberately so the scorer can *demonstrate*
# the local-heavy problem with data rather than assumption.
CANDIDATE_NICHES = {
    "541511": "Custom computer programming services",
    "541512": "Computer systems design services",
    "541519": "Other computer related services",
    "541611": "Admin & general management consulting",
    "541690": "Other scientific & technical consulting",
    "541330": "Engineering services",
    "561210": "Facilities support services",
    "561612": "Security guards & patrol services (control: local-heavy)",
}

# Award type codes for USAspending spending_by_award: contracts only.
CONTRACT_AWARD_TYPES = ["A", "B", "C", "D"]


def ensure_state_dir() -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)
