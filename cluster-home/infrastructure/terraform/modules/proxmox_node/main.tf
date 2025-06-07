terraform {
  required_providers {
    proxmox = {
      source                = "bpg/proxmox"
      configuration_aliases = [proxmox.node]
    }
  }
}

resource "proxmox_virtual_environment_download_file" "talos_iso" {
  provider     = proxmox.node
  content_type = "iso"
  datastore_id = "local"
  node_name    = var.node_name
  url          = "https://factory.talos.dev/image/${var.talos_schematic_id}/${var.talos_version}/metal-amd64.iso"
  file_name    = "talos-${var.talos_version}-metal-amd64.iso"
  overwrite    = false
}

resource "proxmox_virtual_environment_vm" "vms" {
  for_each  = var.node_config.vms
  provider  = proxmox.node
  name      = each.key
  node_name = var.node_name
  vm_id     = each.value.id

  scsi_hardware   = "virtio-scsi-single"
  stop_on_destroy = true
  boot_order      = ["scsi0", "ide3"]

  agent {
    enabled = true
    trim    = true
  }

  startup {
    order      = "3"
    up_delay   = "60"
    down_delay = "60"
  }

  cpu {
    cores = each.value.cpu_cores
    type  = "host"
  }

  memory {
    dedicated = each.value.memory_size
  }

  cdrom {
    enabled = true
    file_id = proxmox_virtual_environment_download_file.talos_iso.id
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    iothread     = true
    discard      = "on"
    size         = each.value.disk_sizes.system
    file_format  = "raw"
  }

  disk {
    datastore_id = var.node_config.datastore
    interface    = "scsi1"
    iothread     = true
    discard      = "on"
    size         = each.value.disk_sizes.data
    file_format  = "raw"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }

    user_account {
      username = var.node_config.credentials.vm_username
      password = var.node_config.credentials.vm_password
      keys     = var.node_config.credentials.ssh_keys
    }
  }

  network_device {
    bridge      = "vmbr0"
    mac_address = each.value.macaddr
  }

  operating_system {
    type = "l26"
  }

  vga {
    type   = "virtio"
    memory = 16
  }
}
