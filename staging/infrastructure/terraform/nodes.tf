resource "proxmox_vm_qemu" "kube-master" {
  for_each = var.nodes

  name        = each.key
  target_node = each.value.target_node
  agent       = 0
  clone       = var.common.vm_template
  vmid        = each.value.id
  memory      = each.value.memory
  cores       = each.value.cores
  network {
    model    = "virtio"
    macaddr  = each.value.macaddr
    bridge   = "vmbr0"
  }
  disk {
    type    = "scsi"
    storage = "local-lvm"
    size    = each.value.disk
    format  = "raw"
    ssd     = 1
    discard = "on"
  }
  serial {
    id = 0
    type = "socket"
  }
  bootdisk     = "scsi0"
  scsihw       = "virtio-scsi-pci"
  os_type      = "cloud-init"
  ipconfig0    = "ip=dhcp"
  ciuser       = var.common.ciuser
  cipassword   = data.sops_file.secrets.data["cipassword"]
  sshkeys      = data.sops_file.secrets.data["ssh_key"]
}
