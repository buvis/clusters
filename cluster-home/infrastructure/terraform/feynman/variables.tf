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
    feynman-master-1 = {
      id          = 4011
      macaddr     = "02:DE:4D:48:29:01"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
    feynman-worker-1 = {
      id          = 4021
      macaddr     = "02:DE:4D:48:29:0A"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
    feynman-worker-2 = {
      id          = 4022
      macaddr     = "02:DE:4D:48:29:0B"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
    feynman-worker-3 = {
      id          = 4023
      macaddr     = "02:DE:4D:48:29:0C"
      pv_zfs      = "feynman-tank"
      target_node = "feynman"
    },
  }
}
