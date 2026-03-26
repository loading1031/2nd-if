# ──────────────────────────────────────────────
# OCI 인증
# ──────────────────────────────────────────────
variable "tenancy_ocid" {
  description = "OCI Tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "OCI User OCID"
  type        = string
}

variable "oci_fingerprint" {
  description = "OCI API Key fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "OCI API private key 파일 경로"
  type        = string
}

variable "region" {
  description = "OCI Region (예: ap-chuncheon-1)"
  type        = string
  default     = "ap-chuncheon-1"
}

variable "compartment_ocid" {
  description = "OCI Compartment OCID (보통 tenancy_ocid와 동일)"
  type        = string
}

# ──────────────────────────────────────────────
# SSH
# ──────────────────────────────────────────────
variable "ssh_public_key" {
  description = "VM에 등록할 SSH 공개키 내용"
  type        = string
}

# ──────────────────────────────────────────────
# 네트워크
# ──────────────────────────────────────────────
variable "admin_cidr" {
  description = "SSH 접근 허용 CIDR (예: 123.45.67.89/32)"
  type        = string
}

# ──────────────────────────────────────────────
# Autonomous DB
# ──────────────────────────────────────────────
variable "adb_admin_password" {
  description = "Autonomous DB ADMIN 비밀번호 (12-30자, 대소문자+숫자+특수문자)"
  type        = string
  sensitive   = true
}
