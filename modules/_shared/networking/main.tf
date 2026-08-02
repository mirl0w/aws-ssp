# This module never creates network resources. It only looks up a VPC and
# subnets that a separate "foundation" layer already provisioned and tagged.
# App-facing modules (ecs-service, lambda-function, ec2-app) call this module
# instead of taking vpc_id/subnet_ids as developer-supplied inputs.
#
# Tagging contract every environment's VPC/subnets must follow:
#   VPC:            Name = "<environment>-vpc"
#   Public subnets:  Tier = "public",  Environment = "<environment>"
#   Private subnets: Tier = "private", Environment = "<environment>"

locals {
  vpc_name = coalesce(var.vpc_name_tag, "${var.environment}-vpc")
}

data "aws_vpc" "this" {
  filter {
    name   = "tag:Name"
    values = [local.vpc_name]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.this.id]
  }
  tags = {
    Tier        = "private"
    Environment = var.environment
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.this.id]
  }
  tags = {
    Tier        = "public"
    Environment = var.environment
  }
}
