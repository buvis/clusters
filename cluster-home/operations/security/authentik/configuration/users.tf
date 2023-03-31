resource "authentik_user" "bob" {
  username = "bob"
  name     = "Bob"
  email    = data.sops_file.secrets.data["email_bob"]
}

resource "authentik_user" "jani" {
  username = "jani"
  name     = "Jani"
  email    = data.sops_file.secrets.data["email_jani"]
}
