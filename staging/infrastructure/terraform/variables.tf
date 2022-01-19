variable "pm_api_url" {
  default = "https://10.7.0.40:8006/api2/json"
}

variable "pm_user" {
  default = "root@pam"
}

variable "common" {
  type = map(string)
  default = {
    vm_template   = "ubuntu-cloudimg"
    ciuser        = "bob"
  }
}

variable "nodes" {
  type = map(map(string))
  default = {
    kao-master-1 = {
      id          = 4010
      cores       = 4
      memory      = 4096
      disk        = "40G"
      macaddr     = "02:DE:4D:48:28:01"
      target_node = "kao"
    },
    kao-worker-1 = {
      id          = 4020
      cores       = 4
      memory      = 4096
      disk        = "40G"
      macaddr     = "02:DE:4D:48:28:0A"
      target_node = "kao"
    },
    kao-worker-2 = {
      id          = 4021
      cores       = 4
      memory      = 4096
      disk        = "40G"
      macaddr     = "02:DE:4D:48:28:0B"
      target_node = "kao"
    },
  }
}
