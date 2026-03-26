# ──────────────────────────────────────────────
# Oracle Autonomous Database (Always Free)
# ──────────────────────────────────────────────
resource "oci_database_autonomous_database" "django_db" {
  compartment_id = var.compartment_ocid
  display_name   = "2nd-if-db"
  db_name        = "SECONDIF"
  db_workload    = "OLTP"

  # Always Free 설정
  is_free_tier             = true
  compute_count            = 1    # 1 OCPU
  data_storage_size_in_gb = 20

  admin_password              = var.adb_admin_password
  is_mtls_connection_required = false # TLS 직접 연결 (Wallet 불필요)

  # VM1 IP에서만 접근 허용
  whitelisted_ips = [oci_core_instance.vm1_webapp.public_ip]
}
