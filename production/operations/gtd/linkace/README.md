## Setup
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

## Import bookmarks
1. Exec into pod with UTF-8 support: `LANG=en_US.UTF-8 kubectl exec -it deployment/linkace -n gtd -- sh`
2. Start creating `storage/bookmarks.html` from heredoc: `cat << EOF > storage/bookmarks.html`
3. Paste content to import
4. End with `EOF`
5. Import to linkace: `./artisan links:import bookmarks.html --skip-check --skip-meta-generation`

Reference:
- https://github.com/Kovah/LinkAce/issues/287#issuecomment-860229837
- https://www.linkace.org/docs/v1/cli/#import-links-from-a-html-bookmarks-file
