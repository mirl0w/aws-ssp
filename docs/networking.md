# Networking

App modules never create or receive VPC/subnet IDs as inputs. They call
`modules/_shared/networking` internally, which looks up an existing VPC by
tag. This keeps every app module's blast radius limited to its own
resources — an app can't accidentally modify shared network infrastructure.

## Tagging contract

Whoever owns the "foundation" layer (usually the platform team, applied
once per environment, not per app) must tag the VPC and subnets like this:

| Resource         | Required tags                                    |
|-------------------|---------------------------------------------------|
| VPC               | `Name = "<environment>-vpc"`                       |
| Public subnets    | `Tier = "public"`, `Environment = "<environment>"`  |
| Private subnets   | `Tier = "private"`, `Environment = "<environment>"` |

## If no VPC exists yet (greenfield)

Run this once per environment, separately from any app deployment. It's
intentionally not part of the app-facing modules — creating a VPC is a
rare, high-blast-radius action that shouldn't be triggerable by an app
team's PR.

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "dev-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true # cheaper for dev; set false for prod

  public_subnet_tags = {
    Tier        = "public"
    Environment = "dev"
  }
  private_subnet_tags = {
    Tier        = "private"
    Environment = "dev"
  }
}
```

This satisfies the tagging contract above, so `modules/_shared/networking`
will find it immediately with no further changes.
