This provides storage to the cluster. I'm using [Rancher's Longhorn](https://rancher.com/products/longhorn). See [manifests](https://github.com/buvis-net/clusters/tree/main/production/operations/longhorn-system).

## Setup

### Prepare node
1. Install Open-iSCSI: `sudo pacman --noconfirm -Sy open-iscsi`
2. Enable and start iSCSI daemon: `sudo systemctl enable --now iscsid`

### Add disk to node
1. Attach the disk
2. Get device name: `lsblk`
3. Double check it: `sudo fdisk -l`
4. Wipe a partition (`/dev/sda1`): `sudo wipefs -fa /dev/sda1`
3. Wipe a disk (`/dev/sda`): `sudo wipefs -fa /dev/sda`
5. Create partition: `sudo fdisk /dev/sda`, n, p, <ENTER>, <ENTER>, <ENTER>, w
4. Refresh disk information: `sudo partprobe /dev/sda`
6. Format the disk: `sudo mkfs.ext4 /dev/sda1` (replace `/dev/sda1` by the name from step 2)
7. Create mountpoint: `sudo mkdir /mnt/lh01` (lh02, lh03, etc.)
8. Mount: `sudo mount /dev/sda1 /mnt/lh01`
9. Get info to fstab line: `cat /proc/self/mounts | grep /dev/sda1`
10. Get disk UUID: `lsblk -f`
11. Use info from steps 7 and 8 to create a permanent mount: `sudo vim /etc/fstab`
  ```
  # Longhorn storage
  UUID=825e9569-4086-4b24-a1ad-56a9b4a8fb4f /mnt/lh01 ext4 rw,relatime 0 0
  ```

### Add disk to Longhorn
1. Open Longhorn UI
2. Node - burger menu at node's line - Edit node and disks - Add disk

## Troubleshoot

### Volume degraded

1. Check logs of engine-manager pod on the node where there is volume failure

### Restore from backup

Follow [Restoring Volumes for Kubernetes StatefulSets](https://longhorn.io/docs/1.2.3/snapshots-and-backups/backup-and-restore/restore-statefulset/)
