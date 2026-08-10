#!/usr/bin/env python3
"""
For each changed requests/**.yaml file, generate a minimal throwaway
Terraform root under .render/<request-name>/ that:
  - sources the module at the exact tag pinned in module_version
  - passes the request's fields through as module inputs

This is what `terraform plan` actually runs against in CI — app teams
never write this themselves, it's generated purely so their request can
be plan-checked before merge.
"""
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RENDER_DIR = REPO_ROOT / ".render"
MODULE_SOURCE_BASE = "git::https://github.com/ORG/platform.git"


def render(request_path: Path) -> None:
    data = yaml.safe_load(request_path.read_text())
    module_name = data["module"]
    module_version = data["module_version"]  # e.g. modules/ecs-service/v1.2.0
    tag = module_version.split("/")[-1]

    out_dir = RENDER_DIR / data["name"]
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = {k: v for k, v in data.items() if k not in ("module", "module_version")}

    lines = [
        f'module "{data["name"]}" {{',
        f'  source = "{MODULE_SOURCE_BASE}//modules/{module_name}?ref={tag}"',
    ]
    for key, val in inputs.items():
        lines.append(f"  {key} = {to_hcl(val)}")
    lines.append("}")

    (out_dir / "main.tf").write_text("\n".join(lines) + "\n")


def to_hcl(value) -> str:
    import json
    # Good enough for plan-rendering purposes: valid HCL accepts JSON syntax
    # for maps/lists/strings/numbers/bools.
    return json.dumps(value)


def main(argv: list[str]) -> int:
    files = [Path(p) for p in argv if p.startswith("requests/") and p.endswith((".yaml", ".yml"))]
    for f in files:
        if f.exists():
            render(f)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))