## Install Proxmox

Taken from https://medium.com/devops-dudes/proxmox-101-8204eb154cd5

1. Download iso: https://www.proxmox.com/en/downloads/category/iso-images-pve
2. Burn it to USB: https://pve.proxmox.com/wiki/Prepare_Installation_Media (use 1M instead of 1m as block size)
3. Install Proxmox following the installation wizard
4. When done, check that you can connect to [Proxmox management UI](https://<server_ip>:8006)
5. Remove subscription notice
  a. ssh to proxmox server
  b. Go to UI site source: `cd /usr/share/javascript/proxmox-widget-toolkit/`
  c. Backup the file you'll modify: `cp proxmoxlib.js proxmoxlib.js.bak`
  d. Edit `proxmoxlib.js`: `vi proxmoxlib.js`
    - Find
    ```
    Ext.Msg.show({
      title: gettext('No valid subscription'),
    ```
    - Replace with
    ```
    void({
      title: gettext('No valid subscription'),
    ```
  e. Restart Proxmox UI: `systemctl restart pveproxy.service`
  f. Clear browser cache and reconnect UI
6. Use community repo
  a. Edit sources: `vi /etc/apt/sources.list`
  b. Add `deb http://download.proxmox.com/debian buster pve-no-subscription`
7. Disable enterprise repo
  a. Go to apt sources directory: `cd /etc/apt/sources.list.d`
  b. Backup enterprise list: `cp pve-enterprise.list pve-enterprise.list.bak`
  c. Edit enterprise list: `vi pve-enterprise.list`
  d. Comment out this line: `deb https://enterprise.proxmox.com/debian/pve buster pve-enterprise`
8. Update the system: `apt update && apt dist-upgrade`

## Create VM template

Taken from https://github.com/dy2k/proxmox-kubernetes#cloud-init-template and https://matthewkalnins.com/posts/home-lab-setup-part-1-proxmox-cloud-init/

1. SSH to proxmox machine
2. Get the image: `wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img`
  I couldn't use the following images:
  - Arch Linux: it lacks overlay module, so k3s won't run
  - CentOS: all VMs are named localhost, so Kubernetes will add one node only
3. Create VM: `qm create 9000 --name "ubuntu-cloudimg" --memory 4096 --cpu cputype=host --cores 4 --serial0 socket --vga serial0 --net0 virtio,bridge=vmbr0,tag=20 --agent enabled=1,fstrim_cloned_disks=1`
4. Import the image to local storage: `qm importdisk 9000 focal-server-cloudimg-amd64.qcow2 local-lvm --format qcow2`
5. Attach the disk to VM: `qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0`
6. Add cloudinit CDROM drive: `qm set 9000 --ide2 local-lvm:cloudinit`
7. Set disk to boot: `qm set 9000 --boot c --bootdisk scsi0`
9. Convert VM to template: `qm template 9000`

## Create infrastructure using Terraform

1. Install Terraform: `brew install terraform`
2. Initialize Terraform: `terraform init`
3. Provision the infrastructure: `terraform apply` (PM_PASS environment variable is set by direnv)
