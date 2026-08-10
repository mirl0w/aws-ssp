#!/usr/bin/env python3
"""
Validate changed requests/**.yaml files against their module's JSON Schema
before Terraform ever sees them.

Usage:
    python3 scripts/validate_requests.py <file1.yaml> [file2.yaml ...]

Exit code is non-zero if any file fails validation. Designed to be called
from CI with the list of files changed in the PR (see
.github/workflows/validate-and-plan.yml), so unrelated requests aren't
re-validated on every push.
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "requests" / "schemas"
LATEST_MAJOR_WARN = True  # warn (don't fail) if a request pins an old major version


def load_schema(module_name: str) -> dict:
    schema_path = SCHEMA_DIR / f"{module_name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(
            f"No schema found for module '{module_name}' at {schema_path}. "
            f"Every module under modules/ must have a matching schema in requests/schemas/."
        )
    return json.loads(schema_path.read_text())


def validate_file(path: Path) -> list[str]:
    errors = []
    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"{path}: not valid YAML ({e})"]

    if not isinstance(data, dict):
        return [f"{path}: top-level content must be a mapping, got {type(data).__name__}"]

    module_name = data.get("module")
    if not module_name:
        return [f"{path}: missing required 'module' field"]

    try:
        schema = load_schema(module_name)
    except FileNotFoundError as e:
        return [f"{path}: {e}"]

    validator = Draft7Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{path}: [{loc}] {err.message}")

    # Extra checks the schema can't express on its own:
    image = (data.get("container") or {}).get("image", "")
    if image.endswith(":latest"):
        errors.append(
            f"{path}: container.image uses the ':latest' tag — pin an immutable "
            f"tag or digest so re-deploys are reproducible."
        )

    return errors


def main(argv: list[str]) -> int:
    files = [Path(p) for p in argv if p.startswith("requests/") and p.endswith((".yaml", ".yml"))]
    if not files:
        print("No requests/*.yaml files in this change set — nothing to validate.")
        return 0

    all_errors: list[str] = []
    for f in files:
        if not f.exists():
            continue  # file was deleted in this PR
        all_errors.extend(validate_file(f))

    if all_errors:
        print("Request validation FAILED:\n")
        for e in all_errors:
            print(f"  ✗ {e}")
        print(f"\n{len(all_errors)} error(s) across {len(files)} file(s).")
        return 1

    print(f"✓ All {len(files)} changed request file(s) are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))