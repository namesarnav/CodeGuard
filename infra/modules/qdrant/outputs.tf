output "qdrant_host" {
  description = "Qdrant host"
  value       = aws_instance.qdrant.private_ip
}

output "qdrant_port" {
  description = "Qdrant port"
  value       = 6333
}

