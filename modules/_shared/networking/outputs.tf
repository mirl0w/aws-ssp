output "vpc_id" {
  value = data.aws_vpc.this.id
}

output "vpc_cidr_block" {
  value = data.aws_vpc.this.cidr_block
}

output "private_subnet_ids" {
  value = data.aws_subnets.private.ids
}

output "public_subnet_ids" {
  value = data.aws_subnets.public.ids
}
