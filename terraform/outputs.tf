output "vm1_public_ip" {
  description = "VM1 (웹앱) 퍼블릭 IP"
  value       = oci_core_instance.vm1_webapp.public_ip
}

output "vm2_private_ip" {
  description = "VM2 (Dify) 프라이빗 IP"
  value       = oci_core_instance.vm2_dify.private_ip
}

output "adb_connection_string" {
  description = "Autonomous DB TLS 연결 문자열"
  value       = oci_database_autonomous_database.django_db.connection_strings[0].profiles[*].value
}

output "adb_service_console_url" {
  description = "Autonomous DB 서비스 콘솔 URL"
  value       = oci_database_autonomous_database.django_db.service_console_url
}

output "ssh_to_vm1" {
  description = "VM1 SSH 접속 명령어"
  value       = "ssh opc@${oci_core_instance.vm1_webapp.public_ip}"
}

output "ssh_to_vm2_via_vm1" {
  description = "VM2 SSH 접속 (VM1 경유)"
  value       = "ssh -J opc@${oci_core_instance.vm1_webapp.public_ip} opc@${oci_core_instance.vm2_dify.private_ip}"
}
