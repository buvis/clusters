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
    cores         = 4
    memory        = 12288
    disk0         = "32G"
    disk1         = "128G"
  }
}

variable "nodes" {
  type = map(map(string))
  default = {
    staging-master-1 = {
      id          = 4011
      macaddr     = "02:DE:4D:48:28:01"
      target_node = "higgs"
    },
    staging-worker-1 = {
      id          = 4021
      macaddr     = "02:DE:4D:48:28:0A"
      target_node = "higgs"
    },
    staging-worker-2 = {
      id          = 4022
      macaddr     = "02:DE:4D:48:28:0B"
      target_node = "higgs"
    },
    staging-worker-3 = {
      id          = 4023
      macaddr     = "02:DE:4D:48:28:0C"
      target_node = "higgs"
    },
  }
}
