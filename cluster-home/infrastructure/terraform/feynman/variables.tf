variable "pm_api_url" {
  default = "https://10.7.0.41:8006/api2/json"
}

variable "pm_user" {
  default = "root@pam"
}

variable "common" {
  type = map(string)
  default = {
    vm_template   = "talos"
    ciuser        = "bob"
    cores         = 4
    memory        = 12288
    disk0         = "32G"
    disk1         = "192G"
  }
}

variable "nodes" {
  type = map(map(string))
  default = {
    buvis-worker-04 = {
      id          = 4024
      macaddr     = "02:DE:4D:48:29:0A"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
    buvis-worker-05 = {
      id          = 4025
      macaddr     = "02:DE:4D:48:29:0B"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
    buvis-worker-06 = {
      id          = 4026
      macaddr     = "02:DE:4D:48:29:0C"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
    buvis-worker-07 = {
      id          = 4027
      macaddr     = "02:DE:4D:48:29:0D"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
  }
}
