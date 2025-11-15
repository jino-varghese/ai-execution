# RDS PostgreSQL Module

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name_prefix = "${var.name_prefix}-db-subnet-"
  subnet_ids  = var.private_subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-db-subnet-group"
    }
  )
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  name_prefix = "${var.name_prefix}-db-params-"
  family      = "postgres15"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-db-parameter-group"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier_prefix = "${var.name_prefix}-db-"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name
  vpc_security_group_ids = [var.database_security_group_id]

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  multi_az               = var.multi_az
  skip_final_snapshot    = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.name_prefix}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  deletion_protection = var.deletion_protection

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-postgresql"
    }
  )
}
