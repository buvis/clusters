Get k3s configuration
=====================

This role downloads the k3s cluster configuration.

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
- hosts: chief
  remote_user: "{{ default_user }}"
  become: true
  gather_facts: true

  roles:
  - get-k3s-config
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
