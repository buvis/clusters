resource "authentik_group" "monitoring_prometheus_users" {
  name         = "monitoring-prometheus-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "monitoring_prometheus" {
  name               = "monitoring-prometheus"
  external_host      = "https://prometheus.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "monitoring_prometheus" {
  name              = "Prometheus"
  slug              = "prometheus"
  group             = "Monitoring"
  protocol_provider = resource.authentik_provider_proxy.monitoring_prometheus.id
  meta_icon         = "https://luktom.net/wordpress/wp-content/uploads/2019/05/prometheus.png"
  meta_description  = "Prometheus"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "monitoring_prometheus" {
  target = authentik_application.monitoring_prometheus.uuid
  group  = authentik_group.monitoring_prometheus_users.id
  order  = 0
}
