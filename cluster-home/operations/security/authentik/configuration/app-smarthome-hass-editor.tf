resource "authentik_group" "smarthome_hass_editor_users" {
  name         = "smarthome-hass-editor-users"
  is_superuser = false
  users        = [authentik_user.bob.id]
}

resource "authentik_provider_proxy" "smarthome_hass_editor" {
  name               = "smarthome-hass-editor"
  external_host      = "https://hass-editor.buvis.net"
  mode               = "forward_single"
  authorization_flow = data.authentik_flow.default_authorization_flow.id
  access_token_validity = "hours=24"
}

resource "authentik_application" "smarthome_hass_editor" {
  name              = "Hass Editor"
  slug              = "hass-editor"
  group             = "Smarthome"
  protocol_provider = resource.authentik_provider_proxy.smarthome_hass_editor.id
  meta_icon         = "https://www.home-assistant.io/images/favicon-192x192-full.png"
  meta_description  = "Hass Editor"
  open_in_new_tab   = true
}

resource "authentik_policy_binding" "smarthome_hass_editor" {
  target = authentik_application.smarthome_hass_editor.uuid
  group  = authentik_group.smarthome_hass_editor_users.id
  order  = 0
}
