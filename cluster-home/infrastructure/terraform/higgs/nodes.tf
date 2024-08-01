resource "proxmox_vm_qemu" "kube-master" {
  for_each = var.nodes

  name        = each.key
  target_node = each.value.target_node
  onboot      = true
  agent       = 0
  clone       = var.common.vm_template
  vmid        = each.value.id
  cores       = var.common.cores
  memory      = var.common.memory
  bootdisk     = "scsi0"
  scsihw       = "virtio-scsi-pci"
  os_type      = "cloud-init"
  ipconfig0    = "ip=dhcp"
  ciuser       = var.common.ciuser
  cipassword   = data.sops_file.secrets.data["cipassword"]
  sshkeys      = data.sops_file.secrets.data["ssh_key"]

  network {
    model    = "virtio"
    macaddr  = each.value.macaddr
    bridge   = "vmbr0"
  }

  disk {
    type    = "scsi"
    storage = "local-lvm"
    size    = var.common.disk0
    format  = "raw"
    ssd     = 1
    discard = true
  }

  disk {
    type    = "scsi"
    storage = each.value.pv_zfs
    size    = var.common.disk1
    format  = "raw"
    ssd     = 1
    discard = true
  }

  serial {
    id = 0
    type = "socket"
  }
}
