Upgrade host
============

This role install k3s and joins the master.

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
  - join-k3s-as-worker
```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (tomas@buvis.net)
