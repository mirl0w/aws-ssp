variable "environment" {
  description = "Environment name this workload deploys into (e.g. dev, staging, prod). Used to find the matching VPC by tag."
  type        = string
}

variable "vpc_name_tag" {
  description = "Value of the 'Name' tag on the target VPC. Defaults to '<environment>-vpc' if not set."
  type        = string
  default     = null
}
