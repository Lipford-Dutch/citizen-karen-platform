"""Export FastAPI's OpenAPI 3.1 document to the checked-in API contract."""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app  # noqa: E402


target = ROOT / "api" / "openapi.yaml"
document = json.loads(json.dumps(app.openapi()))
target.write_text(
    yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8"
)
print(f"Wrote {target}")
