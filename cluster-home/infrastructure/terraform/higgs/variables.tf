variable "pm_api_url" {
  default = "https://10.7.0.40:8006/api2/json"
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
    disk1         = "170G"
  }
}

variable "nodes" {
  type = map(map(string))
  default = {
    buvis-master = {
      id          = 4011
      macaddr     = "02:DE:4D:48:28:01"
      pv_zfs      = "higgs-tank"
      target_node = "higgs"
    },
    buvis-worker-01 = {
      id          = 4021
      macaddr     = "02:DE:4D:48:28:0A"
      pv_zfs      = "higgs-tank"
      target_node = "higgs"
    },
    buvis-worker-02 = {
      id          = 4022
      macaddr     = "02:DE:4D:48:28:0B"
      pv_zfs      = "higgs-tank"
      target_node = "higgs"
    },
    buvis-worker-03 = {
      id          = 4023
      macaddr     = "02:DE:4D:48:28:0C"
      pv_zfs      = "higgs-tank"
      target_node = "higgs"
    },
  }
}
