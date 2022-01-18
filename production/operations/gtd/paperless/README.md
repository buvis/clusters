## Setup
Database paperless for user paperless must be created in central database server.

1. SSH to database server
2. Login as postgres user: `sudo -i -u postgres`
3. Run SQL console: `psql`
4. Create user `paperless`: `CREATE USER paperless WITH CREATEDB ENCRYPTED PASSWORD '<secret password>';`
5. Create database `paperless`: `CREATE DATABASE paperless WITH OWNER=paperless`

## Backup
Reference: https://github.com/jonaswinkler/paperless-ng/blob/master/docs/administration.rst#document-exporter

1. Shell to the pod
2. Execute export: `document_exporter ../export --delete --use-filename-format`
