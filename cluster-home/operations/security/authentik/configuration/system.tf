resource "authentik_service_connection_kubernetes" "local" {
  name  = "local"
  local = true
}
