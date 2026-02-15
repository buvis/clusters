resource "authentik_outpost" "proxy_outpost" {
  name               = "proxy-outpost"
  type               = "proxy"
  service_connection = authentik_service_connection_kubernetes.local.id
  protocol_providers = [
    resource.authentik_provider_proxy.gtd_linkace.id,
    resource.authentik_provider_proxy.gtd_zettelkasten.id,
    resource.authentik_provider_proxy.media_bazarr.id,
    resource.authentik_provider_proxy.media_jellyseerr.id,
    resource.authentik_provider_proxy.media_lidarr.id,
    resource.authentik_provider_proxy.media_nzbget.id,
    resource.authentik_provider_proxy.media_prowlarr.id,
    resource.authentik_provider_proxy.media_qb.id,
    resource.authentik_provider_proxy.media_radarr.id,
    resource.authentik_provider_proxy.media_sonarr.id,
    resource.authentik_provider_proxy.media_tdarr.id,
    resource.authentik_provider_proxy.openfaas.id,
    resource.authentik_provider_proxy.radio_home.id,
    resource.authentik_provider_proxy.storage_kopia.id,
    resource.authentik_provider_proxy.smarthome_hass_editor.id,
  ]
  config = jsonencode({
    authentik_host          = "https://auth.buvis.net",
    authentik_host_insecure = false,
    authentik_host_browser  = "",
    log_level               = "debug",
    object_naming_template  = "ak-outpost-%(name)s",
    docker_network          = null,
    docker_map_ports        = true,
    docker_labels           = null,
    container_image         = null,
    kubernetes_replicas     = 1,
    kubernetes_namespace    = "security",
    kubernetes_ingress_annotations = {
      "cert-manager.io/cluster-issuer" = "letsencrypt-production"
    },
    kubernetes_ingress_class_name = "nginx",
    kubernetes_ingress_secret_name = "proxy-outpost-tls",
    kubernetes_service_type        = "ClusterIP",
    kubernetes_disabled_components = [],
    kubernetes_image_pull_secrets  = []
  })
}
