# Prerequisites

Install the following tools on your workstation:

- [pre-commit]
- [direnv]
- [sops]
- [gpg]
- [ansible]
- [kubectl]

Create accounts:

- [ZeroSSL] to get certificates for ingress
- [Slack] to get notifications from Flux

# Production cluster

Anything that follows supposes you are working in [production directory](https://github.com/buvis-net/clusters/tree/main/production).

## Preparation

1. [Add renovate to Github](https://github.com/marketplace/renovate)
2. Make sure that postgres database `kubernetes` doesn't exist on datastore server
3. Update EAB Credentials for ZeroSSL ACME
    1. Generate new key-secret pair at [ZeroSSL | Developer](https://app.zerossl.com/developer)
    2. Update secrets for cert-manager:
        ```bash
        sops operations/kube-system/cert-manager/secrets.yaml`
        ```
4. Export `GITHUB_TOKEN` environment variable in `.envrc` file with [GitHub personal access token](https://github.com/settings/tokens) generated specifically for Flux
5. Export `SLACK_WEBHOOK_URL` environment variable in `.envrc`, get incoming webhook address `<SLACK_WEBHOOK_URL>` from [Slack](https://api.slack.com/apps)
6. Enable [SOPS](https://github.com/mozilla/sops) for Flux
    1. *(do only once in a lifetime)* Generate GPG key with no password protection. You can't protect the key with password, because Flux has no way of entering it when decrypting the secrets.
    2. Get fingerprint of the key `<SOPS_KEY_FINGERPRINT>`
        ```bash
        gpg --list-secret-keys
        ```
    3. Export `SOPS_KEY_FINGERPRINT` environment variable `.envrc` with the value from previous step

## Bootstrap the cluster

1. Flash the nodes: `ansible-playbook infrastructure/ansible/flash-node`
2. Get kube config: `ansible-playbook infrastructure/ansible/get-cluster-config`
3. Limit workloads scheduling to master nodes:
```bash
kubectl taint node <master> node-role.kubernetes.io/master:NoSchedule`
```

## CNI deployment

1. Install bgpd on home router
2. Copy `infrastructure/etc/bgpd.conf` to home router's `/etc` to configure bgpd to peer with the cluster
3. Install Calico operator (manifest from https://docs.projectcalico.org/getting-started/kubernetes/k3s/multi-node-install modified to refer to arm64 images):
```bash
kubectl apply -f infrastructure/manifests/deploy-tigera-operator.yaml`
```
4. Install Calico (manifest modified to use BGP peering with home router):
```bash
kubectl apply -f infrastructure/manifests/install-calico.yaml`
```

## Workloads deployment

[Flux](https://github.com/fluxcd/flux2) watches my [clusters repository](https://github.com/buvis-net/clusters) and makes the changes to them based on the YAML manifests.

To install Flux, run `make flux`

## Persistent volumes migration

It should be possible to migrate the persistent volumes from previous cluster installation from Longhorn's backups. I never tried that, so I don't know the exact procedure.


# Staging cluster

Anything that follows supposes you are working in [staging directory](https://github.com/buvis-net/clusters/tree/main/staging).

## Preparation

1. Export `GITHUB_TOKEN` environment variable in `.envrc` file with [GitHub personal access token](https://github.com/settings/tokens) generated specifically for Flux
2. Export `SLACK_WEBHOOK_URL` environment variable in `.envrc`, get incoming webhook address `<SLACK_WEBHOOK_URL>` from [Slack](https://api.slack.com/apps)
3. Enable [SOPS](https://github.com/mozilla/sops) for Flux
    1. *(do only once in a lifetime)* Generate GPG key with no password protection. You can't protect the key with password, because Flux has no way of entering it when decrypting the secrets.
    2. Get fingerprint of the key `<SOPS_KEY_FINGERPRINT>`
        ```bash
        gpg --list-secret-keys
        ```
    3. Export `SOPS_KEY_FINGERPRINT` environment variable `.envrc` with the value from previous step

## Install Proxmox

1. Download [Proxmox installation iso](https://www.proxmox.com/en/downloads/category/iso-images-pve)
2. Burn it to USB stick: https://pve.proxmox.com/wiki/Prepare_Installation_Media (use 1M instead of 1m as block size)
3. Boot Proxmox machine from the USB stick
4. Install Proxmox following the installation wizard
5. Enter root's password to `PM_PASS` environment variable in `.envrc`
6. Check that you can connect to Proxmox management UI at `https://<server_ip>:8006`
7. Remove subscription notice
  a. SSH to proxmox server
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
8. Use community repo
  a. Edit sources: `vi /etc/apt/sources.list`
  b. Add `deb http://download.proxmox.com/debian buster pve-no-subscription`
9. Disable enterprise repo
  a. Go to apt sources directory: `cd /etc/apt/sources.list.d`
  b. Backup enterprise list: `cp pve-enterprise.list pve-enterprise.list.bak`
  c. Edit enterprise list: `vi pve-enterprise.list`
  d. Comment out this line: `deb https://enterprise.proxmox.com/debian/pve buster pve-enterprise`
10. Update the system: `apt update && apt dist-upgrade`

## Create VM template

1. SSH to proxmox machine
2. Get the image for VM: `wget https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.img`
  Note: I couldn't use the following images:
  - Arch Linux: it lacks overlay module, so k3s won't run
  - CentOS: all VMs are named localhost, so Kubernetes will add one node only
3. Create VM: `qm create 9000 --name "ubuntu-cloudimg" --memory 4096 --cpu cputype=host --cores 4 --serial0 socket --vga serial0 --net0 virtio,bridge=vmbr0,tag=20 --agent enabled=1,fstrim_cloned_disks=1`
4. Import the image to local storage: `qm importdisk 9000 focal-server-cloudimg-amd64.qcow2 local-lvm --format qcow2`
5. Attach the disk to VM: `qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0`
6. Add cloudinit CDROM drive: `qm set 9000 --ide2 local-lvm:cloudinit`
7. Set disk to boot: `qm set 9000 --boot c --bootdisk scsi0`
9. Convert VM to template: `qm template 9000`

## Bootstrap the cluster

Run `make install`
