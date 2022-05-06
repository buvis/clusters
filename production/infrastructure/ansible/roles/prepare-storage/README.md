Prepare storage
===============

This role creates and formats storage partition.

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
- hosts: worker
  remote_user: "{{ default_user }}"
  become: true
  gather_facts: true

  roles:
  - prepare-storage
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
