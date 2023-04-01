resource "authentik_group" "monitoring_alertmanager_users" {
  name         = "monitoring-alertmanager-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "monitoring_alertmanager" {
  name               = "monitoring-alertmanager"
  external_host      = "https://alertmanager.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "monitoring_alertmanager" {
  name              = "Alertmanager"
  slug              = "alerts"
  group             = "Monitoring"
  protocol_provider = resource.authentik_provider_proxy.monitoring_alertmanager.id
  meta_icon         = "https://luktom.net/wordpress/wp-content/uploads/2019/05/prometheus.png"
  meta_description  = "Alertmanager"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "monitoring_alertmanager" {
  target = authentik_application.monitoring_alertmanager.uuid
  group  = authentik_group.monitoring_alertmanager_users.id
  order  = 0
}
