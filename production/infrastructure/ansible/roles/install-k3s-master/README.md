Upgrade host
============

This role install the additional k3s master.

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
- hosts: master
  remote_user: "{{ default_user }}"
  become: true
  gather_facts: true

  roles:
  - install-k3s-master
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
