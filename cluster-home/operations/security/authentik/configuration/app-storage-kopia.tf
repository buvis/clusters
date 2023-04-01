resource "authentik_group" "storage_kopia_users" {
  name         = "storage-kopia-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "storage_kopia" {
  name               = "storage-kopia"
  external_host      = "https://kopia.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "storage_kopia" {
  name              = "Kopia"
  slug              = "kopia"
  group             = "storage"
  protocol_provider = resource.authentik_provider_proxy.storage_kopia.id
  meta_icon         = "https://github.com/kopia/kopia/raw/master/app/assets/icon.ico"
  meta_description  = "Backups"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "storage_kopia" {
  target = authentik_application.storage_kopia.uuid
  group  = authentik_group.storage_kopia_users.id
  order  = 0
}
