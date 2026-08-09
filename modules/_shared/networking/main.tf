# This module never creates network resources. It only looks up a VPC and
# subnets that a separate "foundation" layer already provisioned and tagged.
# App-facing modules (ecs-service, lambda-function, ec2-app) call this module
# instead of taking vpc_id/subnet_ids as developer-supplied inputs.
#
# Tagging contract every environment's VPC/subnets must follow:
#   VPC:            Name = "<environment>-vpc"
#   Public subnets:  Tier = "public",  Environment = "<environment>"
#   Private subnets: Tier = "private", Environment = "<environment>"

terraform {
  required_version=">=1.5.0"

}

locals {
  vpc_name = coalesce(var.vpc_name_tag, "${var.environment}-vpc")
}

data "aws_vpc" "this" {
  filter {
    name   = "tag:Name"
    values = [local.vpc_name]
  }
  lifecycle {
    postcondition {
      condition = self.id !=""
      error_message = "No VPC found with Name tag '${local.vpc_name}'. Has the foundation layer been applied for environment '${var.environment}'?"
    }
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
  lifecycle{
    postcondition{
      condition =length(self.ids) > 0
      error_message = "No private subnets found in VPC '${local.vpc_name}' with tags Tier=private, Environment=${var.environment}. check the foundation layer's tagging "
    }
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
  lifecycle {
    postcondition {
      condition     = length(self.ids) > 0
      error_message = "No public subnets found in VPC '${local.vpc_name}' with tags Tier=public, Environment=${var.environment}. Check the foundation layer's subnet tagging."
    }
  }
}
