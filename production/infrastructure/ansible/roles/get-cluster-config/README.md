Get cluster configuration
=========================

This role retrieves cluster access configuration for kubectl to local PC for remote control.

Requirements
------------

No requirements.

Role Variables
--------------

No variables.

Dependencies
------------

No dependencies.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

  ```
  - hosts: chief
    remote_user: "{{ default_user }}"
    become: true
    gather_facts: true

    roles:
      - role: get-cluster-conf
  ```

License
-------

BSD

Author Information
------------------

Authored by Tomáš Bouška (https://buvis.net)
