# Self-service AWS deployment platform

Terraform-based platform that lets application teams deploy to AWS by
opening a pull request against `requests/`, without touching raw
Terraform resources or the AWS console directly.


## Design conventions

- **Modules are the only thing platform engineers hand-write AWS
  resources in.** Everything in `requests/` is just inputs to a module.
- **Modules are versioned independently** (git tags, e.g.
  `modules/ecs-service/v1.2.0`) so a breaking change to one app type
  doesn't force every team to re-plan.
- **Every module takes the same "shape" of core inputs** where it makes
  sense: `name`, `team`, `environment`, `tags` — so the request repo
  stays predictable across app types.
- **Networking is never a module input a developer fills in.** Modules
  look up the VPC/subnets themselves via `_shared/networking`, keyed off
  `environment`. Developers shouldn't need to know a subnet ID exists.
- **No module creates its own IAM policies from scratch per call** —
  each module ships a fixed, least-privilege role and only lets the
  caller attach a short list of pre-approved permission "add-ons"
  (e.g. `s3-read`, `sqs-send`) rather than arbitrary policy JSON.

