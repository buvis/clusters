Install k3s to the first master
===============================

This role install the first k3s master.

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
  - install-k3s-chief
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
