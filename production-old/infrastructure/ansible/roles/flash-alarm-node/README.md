Flash Alarm worker
==================

Flash Arch Linux for Raspberry on SD card. After booting, Raspberry will be ready to be further configured by Ansible.

This is based on:
* https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-3
* https://gitlab.com/mipimipi/armutils/-/tree/master/

Requirements
------------

This can be only executed on a host running Arch Linux.

Role Variables
--------------

- **dev_sd** variable must be set and point to SD card's device, for example: /dev/sdc
- **sd_hostname** variable must be set to desired hostname of the node
- **node_role** variable must be set to desired node's role (c for first manager, m for additional manager, w for worker, anything else for standalone node not connected to cluster)
- **image_choice** variable must be set to select the image to flash:
  2 = RPi 2 or RPi 3 with full HW support
  3 = RPi 3 with generic kernel
  4 = RPi 4 with generic kernel

Dependencies
------------

No dependencies

Example Playbook
----------------

In this example, the user is asked to determine SD card's device, hostname and node role before starting flash-alarm-node role.

```
 - hosts: chief
  remote_user: "{{ default_user }}"
  become: true
  gather_facts: true

  pre_tasks:
  - name: list block devices
    command: lsblk -f
    register: blk_list

  - debug:
      msg: "{{ blk_list.stdout_lines }}"

  - pause:
      prompt: enter SD card device full name (/dev/ included; verify that mountpoint is empty!)
    register: dev_sd

  - pause:
      prompt: enter the desired hostname
    register: sd_hostname

  - pause:
      prompt: Choose node role (m = manager, w = worker, anything else = standalone node not connected to cluster)
    register: node_role

  - pause:
      prompt: |
        Select hardware you are flashing SD card for
          2 = RPi 2 or RPi 3 with full HW support
          3 = RPi 3 with generic kernel
          4 = RPi 4 with generic kernel
    register: image_choice

  - set_fact:
      dev_sd: "{{ dev_sd.user_input }}"

  - set_fact:
      sd_hostname: "{{ sd_hostname.user_input }}"

  - set_fact:
      node_role: "{{ node_role.user_input }}"

  - set_fact:
      image_choice: "{{ image_choice.user_input }}"

  roles:
    - flash-alarm-node
```

Research
--------
It seems that chrooting into freshly extracted alarm image causes DNS to break permanently on SD card. So before chrooting, you need to remove the dangling symlink and copy /etc/resolv.conf from host.
Also, I learnt that it fails when using arch-chroot from arch-install-scripts. It is better to follow manual chroot procedure from https://wiki.archlinux.org/index.php/Chroot. To avoid unmounting issues, it is necessary to `mount --make-rslave <dir_in_chroot>` after the initial mounts

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (https://buvis.net)
