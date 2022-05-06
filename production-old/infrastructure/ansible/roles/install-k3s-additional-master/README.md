Upgrade host
============

This role installs the additional k3s master.

Requirements
------------

None.

Role Variables
--------------

No variables.

Dependencies
------------

No dependencies.

Example Playbook
----------------

```
- hosts: manager
  remote_user: "{{ default_user }}"
  become: true
  gather_facts: true

  roles:
  - install-k3s-additional-master
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
