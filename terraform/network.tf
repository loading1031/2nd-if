# ──────────────────────────────────────────────
# VCN
# ──────────────────────────────────────────────
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  display_name   = "2nd-if-vcn"
  cidr_blocks    = ["10.0.0.0/16"]
  dns_label      = "secondif"
}

# ──────────────────────────────────────────────
# Internet Gateway (VM1 인바운드/아웃바운드)
# ──────────────────────────────────────────────
resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "2nd-if-igw"
  enabled        = true
}

# ──────────────────────────────────────────────
# NAT Gateway (VM2 아웃바운드 전용)
# ──────────────────────────────────────────────
resource "oci_core_nat_gateway" "natgw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "2nd-if-natgw"
}

# ──────────────────────────────────────────────
# Route Tables
# ──────────────────────────────────────────────
resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-rt"

  route_rules {
    network_entity_id = oci_core_internet_gateway.igw.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_route_table" "private_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "private-rt"

  route_rules {
    network_entity_id = oci_core_nat_gateway.natgw.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

# ──────────────────────────────────────────────
# Security Lists
# ──────────────────────────────────────────────

# VM1: 웹 앱 (SSH + HTTP + HTTPS)
resource "oci_core_security_list" "public_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-sl"

  # SSH (admin IP만)
  ingress_security_rules {
    protocol  = "6" # TCP
    source    = var.admin_cidr
    stateless = false
    tcp_options {
      min = 22
      max = 22
    }
  }

  # HTTP
  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false
    tcp_options {
      min = 80
      max = 80
    }
  }

  # HTTPS
  ingress_security_rules {
    protocol  = "6"
    source    = "0.0.0.0/0"
    stateless = false
    tcp_options {
      min = 443
      max = 443
    }
  }

  # ICMP (ping)
  ingress_security_rules {
    protocol  = "1" # ICMP
    source    = "0.0.0.0/0"
    stateless = false
  }

  # Egress: 전체 허용
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    stateless   = false
  }
}

# VM2: Dify (VCN 내부 + SSH만)
resource "oci_core_security_list" "private_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "private-sl"

  # SSH (admin IP만, NAT Gateway 경유 또는 VM1에서 점프)
  ingress_security_rules {
    protocol  = "6"
    source    = "10.0.1.0/24" # public subnet에서 SSH
    stateless = false
    tcp_options {
      min = 22
      max = 22
    }
  }

  # VM1 → VM2 Dify API (포트 80)
  ingress_security_rules {
    protocol  = "6"
    source    = "10.0.1.0/24"
    stateless = false
    tcp_options {
      min = 80
      max = 80
    }
  }

  # ICMP (VCN 내부)
  ingress_security_rules {
    protocol  = "1"
    source    = "10.0.0.0/16"
    stateless = false
  }

  # Egress: 전체 허용 (Docker pull, 외부 API 등)
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
    stateless   = false
  }
}

# ──────────────────────────────────────────────
# Subnets
# ──────────────────────────────────────────────

# Public Subnet (VM1)
resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  display_name               = "public-subnet"
  cidr_block                 = "10.0.1.0/24"
  dns_label                  = "pub"
  route_table_id             = oci_core_route_table.public_rt.id
  security_list_ids          = [oci_core_security_list.public_sl.id]
  prohibit_public_ip_on_vnic = false
}

# Private Subnet (VM2)
resource "oci_core_subnet" "private" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  display_name               = "private-subnet"
  cidr_block                 = "10.0.2.0/24"
  dns_label                  = "priv"
  route_table_id             = oci_core_route_table.private_rt.id
  security_list_ids          = [oci_core_security_list.private_sl.id]
  prohibit_public_ip_on_vnic = true
}
