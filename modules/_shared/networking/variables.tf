variable "environment" {
  description = "Environment name this workload deploys into (e.g. dev, staging, prod). Used to find the matching VPC by tag."
  type        = string
  validation {
    condition     = length(trimspace(var.environment)) > 0
    error_message = "The 'environment' variable must be a non-empty string."
  }
}

variable "vpc_name_tag" {
  description = "Value of the 'Name' tag on the target VPC. Defaults to '<environment>-vpc' if not set."
  type        = string
  default     = null
}
