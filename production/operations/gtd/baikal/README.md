## Prepare
[Baikal docker image](https://github.com/ckulka/baikal-docker) won't create all directories it needs. You have to do that upfront. Reference: https://github.com/ckulka/baikal-docker/issues/29

1. SSH to NFS server
2. Create the directories: `mkdir -p {/mnt/tank/pv/baikal/data/db,/mnt/tank/pv/baikal/config}`
3. Change the access rights: `chmod -R 775 /mnt/tank/pv/baikal`
4. Change the ownership: `chown -R 101:101 /mnt/tank/pv/baikal/*`

## Client setup

### iPhone
1. Settings - Calendar - Accounts - Add Account
2. Server = `https://cal.buvis.net/cal.php/principals/<USER>`
3. Enter credentials for the <USER>
4. Rename the account to `baikal`

### BusyCal
1. Preferences - Accounts - <plus icon>
2. Server address = `https://cal.buvis.net/dav.php/`
3. Enter credentials the <USER> and it will fetch its calendars

### Outlook
1. Click Calendar icon at the bottome
2. Right click a calendar group - Add Calendar - From Internet
3. Location = `https://cal.buvis.net/cal.php/calendars/<USER>/<CALENDAR>?export`
4. When asked for credentials, enter the username as `\<USER>` to avoid login with default domain
