This hosts the application for personal efficiency.

## Baikal

### Prepare
[Baikal docker image](https://github.com/ckulka/baikal-docker) won't create all directories it needs. You have to do that upfront. Reference: https://github.com/ckulka/baikal-docker/issues/29

1. SSH to NFS server
2. Create the directories: `mkdir -p {/mnt/tank/pv/baikal/data/db,/mnt/tank/pv/baikal/config}`
3. Change the access rights: `chmod -R 775 /mnt/tank/pv/baikal`
4. Change the ownership: `chown -R 101:101 /mnt/tank/pv/baikal/*`

### Client setup

#### iPhone
1. Settings - Calendar - Accounts - Add Account
2. Server = `https://cal.buvis.net/cal.php/principals/<USER>`
3. Enter credentials for the <USER>
4. Rename the account to `baikal`

#### BusyCal
1. Preferences - Accounts - <plus icon>
2. Server address = `https://cal.buvis.net/dav.php/`
3. Enter credentials the <USER> and it will fetch its calendars

#### Outlook
1. Click Calendar icon at the bottome
2. Right click a calendar group - Add Calendar - From Internet
3. Location = `https://cal.buvis.net/cal.php/calendars/<USER>/<CALENDAR>?export`
4. When asked for credentials, enter the username as `\<USER>` to avoid login with default domain

## Linkace

### Setup
1. Comment out volumeMounts in deployment.yaml (otherwise /app/.env will be readonly and step 5 will fail)
2. Deploy by pushing to repository
3. Exec into pod: `kubectl exec -it deployment/linkace -n gtd -- sh`
4. Fix /app/.env permissions: `chmod 777 /app/.env`
5. Generate app key: `php artisan key:generate`
6. Navigate to [Linkace on buvis](https://bookmarks.buvis.net) and complete the setup
7. Database address and password can be found in `linkace-env` ConfigMap
9. Get app key from pod's `/app/.env` and copy it to `cluster-secrets` `SECRET_LINKACE_APP_KEY`
10. Uncomment volumeMounts in deployment.yaml
11. Push back to repo

Reference: https://www.linkace.org/docs/v1/setup/setup-with-docker/simple/

### Import bookmarks
1. Exec into pod with UTF-8 support: `LANG=en_US.UTF-8 kubectl exec -it deployment/linkace -n gtd -- sh`
2. Start creating `storage/bookmarks.html` from heredoc: `cat << EOF > storage/bookmarks.html`
3. Paste content to import
4. End with `EOF`
5. Import to linkace: `./artisan links:import bookmarks.html --skip-check --skip-meta-generation`

Reference:
- https://github.com/Kovah/LinkAce/issues/287#issuecomment-860229837
- https://www.linkace.org/docs/v1/cli/#import-links-from-a-html-bookmarks-file

## Paperless

### Setup
Database paperless for user paperless must be created in central database server.

1. SSH to database server
2. Login as postgres user: `sudo -i -u postgres`
3. Run SQL console: `psql`
4. Create user `paperless`: `CREATE USER paperless WITH CREATEDB ENCRYPTED PASSWORD '<secret password>';`
5. Create database `paperless`: `CREATE DATABASE paperless WITH OWNER=paperless`

### Backup
Reference: https://github.com/jonaswinkler/paperless-ng/blob/master/docs/administration.rst#document-exporter

1. Shell to the pod
2. Execute export: `document_exporter ../export --delete --use-filename-format`
