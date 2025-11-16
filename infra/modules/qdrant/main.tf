resource "aws_security_group" "qdrant" {
  name        = "${var.name_prefix}-qdrant-sg"
  description = "Security group for Qdrant"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6333
    to_port     = 6333
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  ingress {
    from_port   = 6334
    to_port     = 6334
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.name_prefix}-qdrant-sg"
  }
}

data "aws_vpc" "main" {
  id = var.vpc_id
}

resource "aws_instance" "qdrant" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = var.private_subnet_ids[0]

  vpc_security_group_ids = [aws_security_group.qdrant.id]

  root_block_device {
    volume_type = "gp3"
    volume_size = 50
  }

  user_data = <<-EOF
              #!/bin/bash
              docker run -d \
                --name qdrant \
                -p 6333:6333 \
                -p 6334:6334 \
                -v qdrant_storage:/qdrant/storage \
                qdrant/qdrant
              EOF

  tags = {
    Name = "${var.name_prefix}-qdrant"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/host/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

