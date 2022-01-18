Upgrade host
============

This role upgrades system packages.

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
- hosts: standalone
  remote_user: "{{ default_user }}"
  become: true
  gather_facts: true

  roles:
  - role: upgrade-host
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
