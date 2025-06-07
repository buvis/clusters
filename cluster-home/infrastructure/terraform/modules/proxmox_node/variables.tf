variable "node_name" {
  description = "The name of the Proxmox node"
  type        = string
}

variable "node_config" {
  description = "Complete node configuration including VMs, credentials, and defaults"
  type = object({
    api_url   = string
    datastore = string
    vms = map(object({
      id          = number
      macaddr     = string
      cpu_cores   = number
      memory_size = number
      disk_sizes = object({
        system = number
        data   = number
      })
    }))
    credentials = object({
      pm_username = string
      pm_password = string
      vm_username = string
      vm_password = string
      ssh_keys    = list(string)
    })
  })
}

variable "talos_schematic_id" {
  description = "Talos schematic ID for custom image"
  type        = string
}

variable "talos_version" {
  description = "Talos version to deploy"
  type        = string
}

